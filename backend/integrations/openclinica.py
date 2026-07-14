"""
HACT CTMS — OpenClinica CE 3.17 Integration Client
====================================================
Connects to OpenClinica Community Edition via:
  - SOAP Web Services (StudySubjectService, DataImportService)
  - REST endpoints (data import/export where available)

OpenClinica 3.x uses SOAP/XML Web Services API.
Docs: https://docs.openclinica.com/3.1/technical-documents/web-services

This module is ADDITIVE — no existing Django models/views are modified.
"""

import hashlib
import logging
import os
from xml.etree import ElementTree as ET

import requests

logger = logging.getLogger("hact.integrations.openclinica")

# =============================================================================
# Configuration
# =============================================================================

OC_BASE_URL = os.environ.get("OPENCLINICA_URL", "http://openclinica:8080/OpenClinica")
OC_WS_URL = os.environ.get("OPENCLINICA_WS_URL", "http://openclinica:8080/OpenClinica-ws")
OC_ADMIN_USER = os.environ.get("OPENCLINICA_ADMIN_USER", "root")
OC_ADMIN_PASSWORD = os.environ.get("OPENCLINICA_ADMIN_PASSWORD", "Admin123!")

# SOAP Namespaces used by OpenClinica 3.x Web Services
NS = {
    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    "oc": "http://openclinica.org/ws/study/v1",
    "oc_subj": "http://openclinica.org/ws/studySubject/v1",
    "oc_data": "http://openclinica.org/ws/data/v1",
    "oc_event": "http://openclinica.org/ws/event/v1",
    "beans": "http://openclinica.org/ws/beans",
    "odm": "http://www.cdisc.org/ns/odm/v1.3",
}


# =============================================================================
# SOAP Envelope Builder
# =============================================================================

def _localname(tag: str) -> str:
    """Return an XML tag's local name, stripping any '{namespace}' prefix."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _build_soap_envelope(body_xml: str) -> str:
    """Wrap a SOAP body in the standard envelope with OC WS Security header.

    OpenClinica SOAP web services require the password to be hashed with
    **SHA-1** (not MD5) and supplied in the WS-Security UsernameToken.
    See the OpenClinica Web Services Guide, "Using OpenClinica Web Services".
    """
    password_hash = hashlib.sha1(OC_ADMIN_PASSWORD.encode()).hexdigest()
    return (
        '<soapenv:Envelope'
        ' xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        ' xmlns:v1="http://openclinica.org/ws/study/v1"'
        ' xmlns:sub="http://openclinica.org/ws/studySubject/v1"'
        ' xmlns:data="http://openclinica.org/ws/data/v1"'
        ' xmlns:event="http://openclinica.org/ws/event/v1"'
        ' xmlns:beans="http://openclinica.org/ws/beans">'
        '<soapenv:Header>'
        '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
        '<wsse:UsernameToken>'
        f'<wsse:Username>{OC_ADMIN_USER}</wsse:Username>'
        f'<wsse:Password>{password_hash}</wsse:Password>'
        '</wsse:UsernameToken>'
        '</wsse:Security>'
        '</soapenv:Header>'
        '<soapenv:Body>'
        f'{body_xml}'
        '</soapenv:Body>'
        '</soapenv:Envelope>'
    )


def _send_soap_request(service_path: str, soap_action: str, body_xml: str) -> ET.Element:
    """Send a SOAP request to OpenClinica and return the parsed XML response."""
    url = f"{OC_WS_URL}/ws/{service_path}"
    envelope = _build_soap_envelope(body_xml)

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action,
    }

    try:
        response = requests.post(url, data=envelope.encode('utf-8'), headers=headers, timeout=30)
        # SOAP faults return HTTP 500 but still contain valid XML — don't raise_for_status
        if response.status_code not in (200, 500):
            logger.error("Unexpected HTTP %s from %s", response.status_code, url)
            return None
        root = ET.fromstring(response.text)
        # Check for SOAP Fault
        fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
        if fault is not None:
            fault_string = fault.findtext("faultstring", "Unknown SOAP Fault")
            logger.error("SOAP Fault from %s: %s", service_path, fault_string)
            return None
        return root
    except requests.exceptions.ConnectionError:
        logger.warning("OpenClinica is not reachable at %s — is the profile running?", url)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("OpenClinica SOAP request failed: %s", e)
        return None
    except ET.ParseError as e:
        logger.error("Failed to parse OpenClinica response: %s (body: %s)", e, response.text[:200])
        return None


# =============================================================================
# Study Service
# =============================================================================

def list_studies() -> list:
    """List all studies in OpenClinica via SOAP ListAll."""
    body = "<v1:listAllRequest/>"
    root = _send_soap_request("study/v1", "listAll", body)
    if root is None:
        return []

    studies = []
    ns = "http://openclinica.org/ws/study/v1"
    for study_el in root.iter(f"{{{ns}}}study"):
        oid = study_el.findtext(f"{{{ns}}}identifier", "")
        name = study_el.findtext(f"{{{ns}}}name", "")
        oc_oid = study_el.findtext(f"{{{ns}}}oid", "")
        if oid:  # skip empty
            studies.append({"identifier": oid, "name": name, "oid": oc_oid})
    return studies


def get_study_metadata(study_oid: str) -> str:
    """Get study metadata (ODM XML) from OpenClinica."""
    body = f"""<v1:getMetadataRequest>
      <v1:studyMetadata>
        <beans:identifier>{study_oid}</beans:identifier>
      </v1:studyMetadata>
    </v1:getMetadataRequest>"""
    root = _send_soap_request("study/v1", "getMetadata", body)
    if root is None:
        return None
    # Return the raw ODM XML string
    odm_el = root.find(".//{http://www.cdisc.org/ns/odm/v1.3}ODM")
    if odm_el is not None:
        return ET.tostring(odm_el, encoding="unicode")
    return None


# =============================================================================
# Study Subject Service
# =============================================================================

def create_study_subject(
    study_oid: str,
    site_oid: str,
    subject_label: str,
    enrollment_date: str,
    gender: str = "m",
) -> dict:
    """
    Create a study subject in OpenClinica.
    Returns {"success": True, "subject_oid": "..."} or {"success": False, "error": "..."}.
    """
    body = f"""<sub:createRequest>
      <sub:studySubject>
        <beans:label>{subject_label}</beans:label>
        <beans:enrollmentDate>{enrollment_date}</beans:enrollmentDate>
        <beans:subject>
          <beans:uniqueIdentifier>{subject_label}</beans:uniqueIdentifier>
          <beans:gender>{gender}</beans:gender>
        </beans:subject>
        <beans:studyRef>
          <beans:identifier>{study_oid}</beans:identifier>
          <beans:siteRef>
            <beans:identifier>{site_oid}</beans:identifier>
          </beans:siteRef>
        </beans:studyRef>
      </sub:studySubject>
    </sub:createRequest>"""

    root = _send_soap_request("studySubject/v1", "create", body)
    if root is None:
        return {"success": False, "error": "OpenClinica not reachable"}

    # Parse result
    result = root.findtext(".//{http://openclinica.org/ws/studySubject/v1}result", "")
    if result.lower() == "success":
        subj_oid = root.findtext(
            ".//{http://openclinica.org/ws/studySubject/v1}subjectOID", ""
        )
        logger.info("Created OC subject: %s -> OID: %s", subject_label, subj_oid)
        return {"success": True, "subject_oid": subj_oid}
    else:
        error = root.findtext(".//{http://openclinica.org/ws/studySubject/v1}error", "Unknown")
        logger.error("OC subject creation failed for %s: %s", subject_label, error)
        return {"success": False, "error": error}


def list_study_subjects(study_oid: str, site_oid: str = "") -> list:
    """List all subjects in a study/site."""
    site_ref = ""
    if site_oid:
        site_ref = f"""<beans:siteRef>
            <beans:identifier>{site_oid}</beans:identifier>
          </beans:siteRef>"""

    body = f"""<sub:listAllByStudyRequest>
      <sub:studyRef>
        <beans:identifier>{study_oid}</beans:identifier>
        {site_ref}
      </sub:studyRef>
    </sub:listAllByStudyRequest>"""

    root = _send_soap_request("studySubject/v1", "listAllByStudy", body)
    if root is None:
        return []

    # The listAllByStudy response returns each subject in the studySubject/v1
    # namespace (not beans), so match by local element name to be robust to
    # whichever namespace OpenClinica emits. De-duplicate by label.
    subjects = []
    seen = set()
    for subj in root.iter():
        if _localname(subj.tag) != "studySubject":
            continue
        label = ""
        oid = ""
        for child in subj.iter():
            ln = _localname(child.tag)
            text = (child.text or "").strip()
            if ln == "label" and not label:
                label = text
            elif ln in ("subjectOID", "oid", "secondaryLabel") and text and not oid:
                oid = text
        if label and label not in seen:
            seen.add(label)
            subjects.append({"label": label, "oid": oid})
    return subjects


# =============================================================================
# Event Service
# =============================================================================

def schedule_event(
    study_oid: str,
    subject_label: str,
    event_definition_oid: str,
    start_date: str,
) -> dict:
    """Schedule a study event for a subject in OpenClinica."""
    body = f"""<event:scheduleRequest>
      <event:event>
        <beans:studySubjectRef>
          <beans:label>{subject_label}</beans:label>
        </beans:studySubjectRef>
        <beans:studyRef>
          <beans:identifier>{study_oid}</beans:identifier>
        </beans:studyRef>
        <beans:eventDefinitionOID>{event_definition_oid}</beans:eventDefinitionOID>
        <beans:startDate>{start_date}</beans:startDate>
      </event:event>
    </event:scheduleRequest>"""

    root = _send_soap_request("event/v1", "schedule", body)
    if root is None:
        return {"success": False, "error": "OpenClinica not reachable"}

    result = root.findtext(".//{http://openclinica.org/ws/event/v1}result", "")
    if result.lower() == "success":
        logger.info("Scheduled OC event %s for subject %s", event_definition_oid, subject_label)
        return {"success": True}
    else:
        error = root.findtext(".//{http://openclinica.org/ws/event/v1}error", "Unknown")
        return {"success": False, "error": error}


# =============================================================================
# Data Import Service (ODM XML)
# =============================================================================

def import_data_odm(odm_xml: str) -> dict:
    """
    Import clinical data into OpenClinica using ODM XML format.
    This is the primary mechanism for syncing form data from Django → OC.
    """
    body = f"""<data:importRequest>
      <data:odm><![CDATA[{odm_xml}]]></data:odm>
    </data:importRequest>"""

    root = _send_soap_request("data/v1", "import", body)
    if root is None:
        return {"success": False, "error": "OpenClinica not reachable"}

    result = root.findtext(".//{http://openclinica.org/ws/data/v1}result", "")
    if result.lower() == "success":
        logger.info("ODM data import succeeded")
        return {"success": True}
    else:
        error = root.findtext(".//{http://openclinica.org/ws/data/v1}error", "Unknown")
        logger.error("ODM data import failed: %s", error)
        return {"success": False, "error": error}


# =============================================================================
# Health Check
# =============================================================================

def is_available() -> bool:
    """Check if OpenClinica is reachable and responding."""
    try:
        resp = requests.get(f"{OC_BASE_URL}/MainMenu", timeout=5, allow_redirects=False)
        return resp.status_code in (200, 302)
    except requests.exceptions.RequestException:
        return False


def diagnostic(
    study_identifier: str = "",
    create_label: str = "",
    site_identifier: str = "",
) -> dict:
    """Return a detailed snapshot of OpenClinica WS connectivity for debugging.

    Performs a real authenticated ``listAll`` (Study service) and, optionally,
    ``listAllByStudy`` for a given study identifier, returning the raw HTTP
    status and a response snippet so auth/endpoint issues are visible without
    server shell access. Read-only unless ``create_label`` is supplied, in
    which case it attempts a real ``createStudySubject`` and returns the raw
    result/error (used to surface data-level validation problems).
    """
    out = {
        "base_url": OC_BASE_URL,
        "ws_url": OC_WS_URL,
        "admin_user": OC_ADMIN_USER,
        "password_configured": bool(os.environ.get("OPENCLINICA_ADMIN_PASSWORD")),
        "password_hash_algo": "sha1",
        "reachable_main": is_available(),
    }

    envelope = _build_soap_envelope("<v1:listAllRequest/>")
    url = f"{OC_WS_URL}/ws/study/v1"
    headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "listAll"}
    try:
        resp = requests.post(url, data=envelope.encode("utf-8"), headers=headers, timeout=20)
        text = resp.text or ""
        out["listAll"] = {
            "endpoint": url,
            "http_status": resp.status_code,
            "result": ("success" if "<ns1:result>Success</ns1:result>" in text
                       or ">Success<" in text else "not-success"),
            "snippet": text[:600],
        }
    except requests.exceptions.RequestException as e:
        out["listAll"] = {"endpoint": url, "error": str(e)}

    if study_identifier:
        out["studies_parsed"] = list_studies()
        out["subjects_for_identifier"] = list_study_subjects(study_identifier)

        # Raw listAllByStudy so the response structure is visible for debugging.
        subj_body = f"""<sub:listAllByStudyRequest>
          <sub:studyRef>
            <beans:identifier>{study_identifier}</beans:identifier>
          </sub:studyRef>
        </sub:listAllByStudyRequest>"""
        subj_url = f"{OC_WS_URL}/ws/studySubject/v1"
        try:
            resp = requests.post(
                subj_url,
                data=_build_soap_envelope(subj_body).encode("utf-8"),
                headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "listAllByStudy"},
                timeout=20,
            )
            out["listAllByStudy_raw"] = {
                "http_status": resp.status_code,
                "snippet": (resp.text or "")[:900],
            }
        except requests.exceptions.RequestException as e:
            out["listAllByStudy_raw"] = {"error": str(e)}

    if create_label and study_identifier:
        import datetime

        site_ref = ""
        if site_identifier:
            site_ref = (
                f"<beans:siteRef><beans:identifier>{site_identifier}"
                f"</beans:identifier></beans:siteRef>"
            )
        create_body = f"""<sub:createRequest>
          <sub:studySubject>
            <beans:label>{create_label}</beans:label>
            <beans:enrollmentDate>{datetime.date.today()}</beans:enrollmentDate>
            <beans:subject>
              <beans:uniqueIdentifier>{create_label}</beans:uniqueIdentifier>
              <beans:gender>m</beans:gender>
            </beans:subject>
            <beans:studyRef>
              <beans:identifier>{study_identifier}</beans:identifier>
              {site_ref}
            </beans:studyRef>
          </sub:studySubject>
        </sub:createRequest>"""
        create_url = f"{OC_WS_URL}/ws/studySubject/v1"
        try:
            resp = requests.post(
                create_url,
                data=_build_soap_envelope(create_body).encode("utf-8"),
                headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "create"},
                timeout=20,
            )
            out["create_probe"] = {
                "endpoint": create_url,
                "http_status": resp.status_code,
                "snippet": (resp.text or "")[:800],
            }
        except requests.exceptions.RequestException as e:
            out["create_probe"] = {"endpoint": create_url, "error": str(e)}

    return out


# =============================================================================
# ODM XML Builder — Convert Django FormInstance → ODM XML for import
# =============================================================================

def build_odm_for_form_instance(form_instance) -> str:
    """
    Build ODM XML from a Django FormInstance + its ItemResponses.
    This creates the minimal ODM ClinicalData needed for OC import.
    """
    study = form_instance.subject.study
    subject = form_instance.subject
    form = form_instance.form

    study_oid = study.openclinica_study_oid or f"S_{study.protocol_number}"
    subject_key = subject.subject_identifier

    # Group ItemData by the item's *real* OpenClinica ItemGroup OID. When a CRF
    # was imported from OpenClinica these OIDs are stored on each Item, so data
    # lands in the correct group; otherwise we fall back to a single default
    # group and name-derived OIDs (best effort, legacy behaviour).
    from xml.sax.saxutils import escape as _xml_escape

    groups = {}
    for response in form_instance.responses.select_related("item").all():
        item = response.item
        item_oid = item.openclinica_item_oid or f"I_{item.field_name.upper()}"
        group_oid = item.openclinica_item_group_oid or "IG_DEFAULT"
        value = _xml_escape(response.value or "", {'"': "&quot;"})
        groups.setdefault(group_oid, []).append(
            f'<ItemData ItemOID="{item_oid}" Value="{value}"/>'
        )

    group_blocks = []
    for group_oid, item_els in groups.items():
        items_xml = "\n            ".join(item_els)
        group_blocks.append(
            f'<ItemGroupData ItemGroupOID="{group_oid}" TransactionType="Insert">\n'
            f'            {items_xml}\n'
            f'          </ItemGroupData>'
        )
    groups_xml = "\n          ".join(group_blocks) or (
        '<ItemGroupData ItemGroupOID="IG_DEFAULT" TransactionType="Insert"/>'
    )

    # Get event OID if available
    event_oid = "SE_VISIT"
    if form_instance.subject_visit and form_instance.subject_visit.visit:
        event_oid = (
            form_instance.subject_visit.visit.openclinica_event_definition_oid
            or f"SE_{form_instance.subject_visit.visit.visit_name.upper().replace(' ', '_')}"
        )

    form_oid = form.openclinica_crf_oid or f"F_{form.name.upper().replace(' ', '_')}"

    odm_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3"
     FileType="Transactional" FileOID="HACT_SYNC"
     CreationDateTime="{form_instance.updated_at.isoformat() if hasattr(form_instance, 'updated_at') else ''}">
  <ClinicalData StudyOID="{study_oid}">
    <SubjectData SubjectKey="{subject_key}">
      <StudyEventData StudyEventOID="{event_oid}">
        <FormData FormOID="{form_oid}">
          {groups_xml}
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""
    return odm_xml
