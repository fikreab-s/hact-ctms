"""
Outputs — CDISC ODM XML Export
=================================
Generates a basic CDISC ODM 1.3.2 XML export of clinical data.

This provides a regulatory-standard data exchange format for immediate use.
Full SDTM submission-ready packages are deferred to the OpenClinica
integration (Day 7-8), where OC exports CDISC ODM data which then goes
through ETL tools (SAS/Pinnacle 21) for final SDTM domain generation.

Reference: CDISC ODM 1.3.2 Specification
"""

import os
from datetime import datetime
from pathlib import Path
from xml.dom.minidom import Document

from django.conf import settings


def _ensure_export_dir(study_protocol):
    """Create the export directory structure."""
    export_dir = Path(settings.MEDIA_ROOT) / "exports" / study_protocol
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def export_study_odm(study, user=None):
    """Generate CDISC ODM 1.3.2 XML for a study.

    Structure:
        <ODM>
          <Study OID="S_xxx">
            <GlobalVariables>
            <MetaDataVersion>
              <FormDef> per form
              <ItemGroupDef> per form
              <ItemDef> per item
          <AdminData> (optional)
          <ClinicalData StudyOID="S_xxx">
            <SubjectData SubjectKey="SUBJ-001">
              <StudyEventData StudyEventOID="V_xxx">
                <FormData FormOID="F_xxx">
                  <ItemGroupData>
                    <ItemData ItemOID="I_xxx" Value="xxx"/>

    Returns:
        tuple: (file_path, snapshot_record)
    """
    from clinical.models import Form, FormInstance, Item, ItemResponse, Subject, Visit
    from outputs.models import DatasetSnapshot

    doc = Document()

    # Root <ODM> element
    odm = doc.createElement("ODM")
    odm.setAttribute("xmlns", "http://www.cdisc.org/ns/odm/v1.3")
    odm.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    odm.setAttribute("ODMVersion", "1.3.2")
    odm.setAttribute("FileType", "Snapshot")
    odm.setAttribute("FileOID", f"HACT_{study.protocol_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    odm.setAttribute("CreationDateTime", datetime.now().isoformat())
    odm.setAttribute("Originator", "HACT CTMS")
    odm.setAttribute("SourceSystem", "HACT Django Backend")
    doc.appendChild(odm)

    study_oid = study.openclinica_study_oid or f"S_{study.protocol_number}"

    # =========================================================================
    # <Study> — Metadata
    # =========================================================================
    study_el = doc.createElement("Study")
    study_el.setAttribute("OID", study_oid)
    odm.appendChild(study_el)

    # GlobalVariables
    gv = doc.createElement("GlobalVariables")
    study_el.appendChild(gv)

    study_name = doc.createElement("StudyName")
    study_name.appendChild(doc.createTextNode(study.name))
    gv.appendChild(study_name)

    study_desc = doc.createElement("StudyDescription")
    study_desc.appendChild(doc.createTextNode(f"Protocol: {study.protocol_number}"))
    gv.appendChild(study_desc)

    protocol_name = doc.createElement("ProtocolName")
    protocol_name.appendChild(doc.createTextNode(study.protocol_number))
    gv.appendChild(protocol_name)

    # MetaDataVersion
    mdv = doc.createElement("MetaDataVersion")
    mdv.setAttribute("OID", "MDV.HACT.001")
    mdv.setAttribute("Name", f"{study.protocol_number} Metadata v1")
    study_el.appendChild(mdv)

    # Protocol
    protocol = doc.createElement("Protocol")
    mdv.appendChild(protocol)

    # StudyEventDefs (one per visit)
    visits = Visit.objects.filter(study=study).order_by("visit_order")
    for visit in visits:
        event_oid = visit.openclinica_event_definition_oid or f"SE_{visit.visit_name.replace(' ', '_')}"

        se_ref = doc.createElement("StudyEventRef")
        se_ref.setAttribute("StudyEventOID", event_oid)
        se_ref.setAttribute("OrderNumber", str(visit.visit_order))
        se_ref.setAttribute("Mandatory", "Yes")
        protocol.appendChild(se_ref)

        se_def = doc.createElement("StudyEventDef")
        se_def.setAttribute("OID", event_oid)
        se_def.setAttribute("Name", visit.visit_name)
        se_def.setAttribute("Repeating", "No")
        se_def.setAttribute("Type", "Scheduled")
        mdv.appendChild(se_def)

    # FormDefs, ItemGroupDefs, ItemDefs
    forms = Form.objects.filter(study=study, is_active=True).prefetch_related("items")
    for form in forms:
        form_oid = form.openclinica_crf_oid or f"F_{form.name.replace(' ', '_')}"
        ig_oid = f"IG_{form.name.replace(' ', '_')}"

        # FormDef
        form_def = doc.createElement("FormDef")
        form_def.setAttribute("OID", form_oid)
        form_def.setAttribute("Name", form.name)
        form_def.setAttribute("Repeating", "No")
        mdv.appendChild(form_def)

        ig_ref = doc.createElement("ItemGroupRef")
        ig_ref.setAttribute("ItemGroupOID", ig_oid)
        ig_ref.setAttribute("Mandatory", "Yes")
        form_def.appendChild(ig_ref)

        # Add FormRef to each StudyEventDef
        for se_def_node in mdv.getElementsByTagName("StudyEventDef"):
            f_ref = doc.createElement("FormRef")
            f_ref.setAttribute("FormOID", form_oid)
            f_ref.setAttribute("Mandatory", "No")
            se_def_node.appendChild(f_ref)

        # ItemGroupDef
        ig_def = doc.createElement("ItemGroupDef")
        ig_def.setAttribute("OID", ig_oid)
        ig_def.setAttribute("Name", form.name)
        ig_def.setAttribute("Repeating", "No")
        mdv.appendChild(ig_def)

        # ItemDefs
        items = Item.objects.filter(form=form).order_by("order")
        for item in items:
            item_oid = f"I_{form.name.replace(' ', '_')}_{item.field_name}"

            i_ref = doc.createElement("ItemRef")
            i_ref.setAttribute("ItemOID", item_oid)
            i_ref.setAttribute("Mandatory", "Yes" if item.required else "No")
            ig_def.appendChild(i_ref)

            i_def = doc.createElement("ItemDef")
            i_def.setAttribute("OID", item_oid)
            i_def.setAttribute("Name", item.field_name)
            i_def.setAttribute("DataType", _map_field_type(item.field_type))
            i_def.setAttribute("Length", "200")

            desc = doc.createElement("Description")
            tt = doc.createElement("TranslatedText")
            tt.setAttribute("xml:lang", "en")
            tt.appendChild(doc.createTextNode(item.field_label))
            desc.appendChild(tt)
            i_def.appendChild(desc)

            mdv.appendChild(i_def)

    # =========================================================================
    # <ClinicalData> — Actual patient data
    # =========================================================================
    clinical_data = doc.createElement("ClinicalData")
    clinical_data.setAttribute("StudyOID", study_oid)
    clinical_data.setAttribute("MetaDataVersionOID", "MDV.HACT.001")
    odm.appendChild(clinical_data)

    subjects = Subject.objects.filter(
        study=study
    ).prefetch_related(
        "subject_visits__visit",
    ).order_by("subject_identifier")

    for subject in subjects:
        subj_data = doc.createElement("SubjectData")
        subj_data.setAttribute("SubjectKey", subject.subject_identifier)
        clinical_data.appendChild(subj_data)

        # StudyEventData per visit
        for sv in subject.subject_visits.select_related("visit").all():
            event_oid = (
                sv.visit.openclinica_event_definition_oid
                or f"SE_{sv.visit.visit_name.replace(' ', '_')}"
            )

            se_data = doc.createElement("StudyEventData")
            se_data.setAttribute("StudyEventOID", event_oid)
            if sv.actual_date:
                se_data.setAttribute("StartDate", sv.actual_date.isoformat())
            subj_data.appendChild(se_data)

            # FormData per form instance for this subject+visit
            form_instances = FormInstance.objects.filter(
                subject=subject,
                subject_visit=sv,
            ).select_related("form")

            for fi in form_instances:
                form_oid = (
                    fi.form.openclinica_crf_oid
                    or f"F_{fi.form.name.replace(' ', '_')}"
                )
                ig_oid = f"IG_{fi.form.name.replace(' ', '_')}"

                form_data = doc.createElement("FormData")
                form_data.setAttribute("FormOID", form_oid)
                se_data.appendChild(form_data)

                ig_data = doc.createElement("ItemGroupData")
                ig_data.setAttribute("ItemGroupOID", ig_oid)
                form_data.appendChild(ig_data)

                # ItemData per response
                responses = ItemResponse.objects.filter(
                    form_instance=fi
                ).select_related("item")

                for ir in responses:
                    item_oid = f"I_{fi.form.name.replace(' ', '_')}_{ir.item.field_name}"
                    item_data = doc.createElement("ItemData")
                    item_data.setAttribute("ItemOID", item_oid)
                    item_data.setAttribute("Value", ir.value or "")
                    ig_data.appendChild(item_data)

    # =========================================================================
    # Write to file
    # =========================================================================
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = _ensure_export_dir(study.protocol_number)
    filename = f"{study.protocol_number}_ODM_{ts}.xml"
    file_path = export_dir / filename

    xml_content = doc.toprettyxml(indent="  ", encoding="UTF-8")
    with open(file_path, "wb") as f:
        f.write(xml_content)

    # Create snapshot record
    relative_url = f"/media/exports/{study.protocol_number}/{filename}"
    snapshot = DatasetSnapshot.objects.create(
        study=study,
        snapshot_type="SDTM",
        file_url=relative_url,
        generated_by=user,
        description=f"CDISC ODM 1.3.2 export generated on {ts}.",
        criteria={
            "export_type": "cdisc_odm",
            "odm_version": "1.3.2",
            "subjects_included": subjects.count(),
            "timestamp": ts,
        },
    )

    return str(file_path), snapshot


def _map_field_type(django_field_type):
    """Map Django field types to CDISC ODM DataTypes."""
    mapping = {
        "text": "text",
        "textarea": "text",
        "number": "float",
        "integer": "integer",
        "date": "date",
        "datetime": "datetime",
        "dropdown": "text",
        "radio": "text",
        "checkbox": "text",
    }
    return mapping.get(django_field_type, "text")
