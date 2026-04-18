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

def _build_soap_envelope(body_xml: str) -> str:
    """Wrap a SOAP body in the standard envelope with OC WS Security header."""
    password_hash = hashlib.md5(OC_ADMIN_PASSWORD.encode()).hexdigest()
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
    root = _send_soap_request("StudyService", "listAll", body)
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
    root = _send_soap_request("StudyService", "getMetadata", body)
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

    root = _send_soap_request("StudySubjectService", "create", body)
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

    root = _send_soap_request("StudySubjectService", "listAllByStudy", body)
    if root is None:
        return []

    subjects = []
    for subj in root.iter("{http://openclinica.org/ws/beans}studySubject"):
        label = subj.findtext("{http://openclinica.org/ws/beans}label", "")
        oid = subj.findtext("{http://openclinica.org/ws/beans}secondaryLabel", "")
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

    root = _send_soap_request("EventService", "schedule", body)
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

    root = _send_soap_request("DataImportService", "import", body)
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

    # Build ItemData elements from responses
    item_data_elements = []
    for response in form_instance.responses.select_related("item").all():
        item_oid = f"I_{response.item.field_name.upper()}"
        value = response.value or ""
        item_data_elements.append(
            f'<ItemData ItemOID="{item_oid}" Value="{value}"/>'
        )

    items_xml = "\n            ".join(item_data_elements)

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
          <ItemGroupData ItemGroupOID="IG_DEFAULT" TransactionType="Insert">
            {items_xml}
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""
    return odm_xml
