"""
Safety — CIOMS I PDF Generator
=================================
Generates a CIOMS I (Council for International Organizations of Medical
Sciences) Initial Case Report Form PDF from AdverseEvent + Subject data.

The CIOMS I form is the international standard for expedited reporting
of Serious Adverse Events (SAEs) to regulatory authorities.

Storage:
- Currently saved to Django MEDIA_ROOT/cioms/
- Will be swapped to Nextcloud WebDAV upload on Day 9
"""

import os
from datetime import date

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_cioms_pdf(cioms_form):
    """Generate a CIOMS I PDF for a given CiomsForm record.

    Args:
        cioms_form: CiomsForm model instance (with adverse_event FK)

    Returns:
        str: File path to the generated PDF
    """
    ae = cioms_form.adverse_event
    subject = ae.subject
    study = ae.study
    site = subject.site

    # Create output directory
    output_dir = os.path.join(
        settings.MEDIA_ROOT, "cioms", study.protocol_number
    )
    os.makedirs(output_dir, exist_ok=True)

    filename = f"CIOMS_{study.protocol_number}_AE-{ae.pk}_{date.today().isoformat()}.pdf"
    file_path = os.path.join(output_dir, filename)

    # Build PDF
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CiomsTitle",
        parent=styles["Title"],
        fontSize=14,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    header_style = ParagraphStyle(
        "CiomsHeader",
        parent=styles["Heading2"],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.white,
        backColor=colors.HexColor("#16213e"),
        borderPadding=(4, 4, 4, 4),
    )
    label_style = ParagraphStyle(
        "CiomsLabel",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.HexColor("#444444"),
    )
    value_style = ParagraphStyle(
        "CiomsValue",
        parent=styles["Normal"],
        fontSize=9,
        spaceBefore=1,
        spaceAfter=2,
    )

    elements = []

    # =========================================================================
    # HEADER
    # =========================================================================
    elements.append(Paragraph("CIOMS I — SUSPECTED ADVERSE REACTION REPORT", title_style))
    elements.append(Paragraph(
        f"<i>Generated: {date.today().isoformat()} | "
        f"Form Version: {cioms_form.form_version} | "
        f"Status: {cioms_form.get_status_display()}</i>",
        label_style,
    ))
    elements.append(Spacer(1, 4 * mm))

    # =========================================================================
    # SECTION I — PATIENT INFORMATION
    # =========================================================================
    elements.append(Paragraph("I. PATIENT INFORMATION", header_style))
    patient_data = [
        [_field("Patient Initials", subject.subject_identifier, label_style, value_style),
         _field("Country", site.country, label_style, value_style)],
        [_field("Date of Birth", str(subject.date_of_birth) if hasattr(subject, 'date_of_birth') and subject.date_of_birth else "Not recorded", label_style, value_style),
         _field("Sex", getattr(subject, 'gender', 'Not recorded'), label_style, value_style)],
        [_field("Study Site", f"{site.site_code} — {site.name}", label_style, value_style),
         _field("Protocol Number", study.protocol_number, label_style, value_style)],
    ]
    elements.append(_make_table(patient_data))
    elements.append(Spacer(1, 3 * mm))

    # =========================================================================
    # SECTION II — SUSPECTED REACTION
    # =========================================================================
    elements.append(Paragraph("II. SUSPECTED ADVERSE REACTION", header_style))
    reaction_data = [
        [_field("Adverse Event Term", ae.ae_term, label_style, value_style),
         _field("Severity", ae.get_severity_display(), label_style, value_style)],
        [_field("Onset Date", str(ae.start_date), label_style, value_style),
         _field("Resolution Date", str(ae.end_date) if ae.end_date else "Ongoing", label_style, value_style)],
        [_field("Serious", "YES" if ae.serious else "NO", label_style, value_style),
         _field("Seriousness Criteria", ae.serious_criteria or "N/A", label_style, value_style)],
        [_field("Causality Assessment", ae.get_causality_display() if ae.causality else "Not assessed", label_style, value_style),
         _field("Outcome", ae.get_outcome_display() if ae.outcome else "Not resolved", label_style, value_style)],
    ]
    elements.append(_make_table(reaction_data))
    elements.append(Spacer(1, 3 * mm))

    # =========================================================================
    # SECTION III — ACTION TAKEN
    # =========================================================================
    elements.append(Paragraph("III. ACTION TAKEN", header_style))
    action_data = [
        [_field("Action Taken", ae.action_taken or "None specified", label_style, value_style, colspan=2)],
    ]
    elements.append(_make_table(action_data, colWidths=[None]))
    elements.append(Spacer(1, 3 * mm))

    # =========================================================================
    # SECTION IV — STUDY / REPORTER INFORMATION
    # =========================================================================
    elements.append(Paragraph("IV. STUDY & REPORTER INFORMATION", header_style))
    study_data = [
        [_field("Study Name", study.name, label_style, value_style),
         _field("Phase", study.phase, label_style, value_style)],
        [_field("Sponsor", study.sponsor, label_style, value_style),
         _field("Reported By", ae.reported_by.get_full_name() if ae.reported_by else "System", label_style, value_style)],
        [_field("Date of Report", str(ae.reported_at.date()) if ae.reported_at else "N/A", label_style, value_style),
         _field("Regulatory Authority", cioms_form.regulatory_authority or "Not specified", label_style, value_style)],
    ]
    elements.append(_make_table(study_data))
    elements.append(Spacer(1, 3 * mm))

    # =========================================================================
    # SECTION V — REGULATORY SUBMISSION
    # =========================================================================
    elements.append(Paragraph("V. REGULATORY SUBMISSION STATUS", header_style))
    reg_data = [
        [_field("Submission Deadline", str(cioms_form.submission_deadline) if cioms_form.submission_deadline else "Not set", label_style, value_style),
         _field("Submitted Date", str(cioms_form.submitted_date) if cioms_form.submitted_date else "Not yet submitted", label_style, value_style)],
    ]
    elements.append(_make_table(reg_data))
    elements.append(Spacer(1, 6 * mm))

    # =========================================================================
    # FOOTER
    # =========================================================================
    elements.append(Paragraph(
        f"<i>CIOMS Form ID: {cioms_form.pk} | "
        f"AE ID: {ae.pk} | "
        f"Subject: {subject.subject_identifier} | "
        f"This document is system-generated and constitutes part of the study safety record.</i>",
        ParagraphStyle("Footer", parent=label_style, fontSize=6, textColor=colors.grey),
    ))

    doc.build(elements)

    # Update CiomsForm with file location
    relative_url = f"/media/cioms/{study.protocol_number}/{filename}"
    cioms_form.file_url = relative_url
    cioms_form.save(update_fields=["file_url"])

    return file_path


# =============================================================================
# Helper functions
# =============================================================================


def _field(label, value, label_style, value_style, colspan=1):
    """Create a stacked label + value paragraph for table cells."""
    return [
        Paragraph(f"<b>{label}</b>", label_style),
        Paragraph(str(value), value_style),
    ]


def _make_table(data, colWidths=None):
    """Create a styled CIOMS table from nested data."""
    # Flatten: each row contains lists of [label, value] paragraphs
    table_data = []
    for row in data:
        flat_row = []
        for cell in row:
            if isinstance(cell, list) and len(cell) == 2:
                combined = Paragraph(
                    f"<font size='7' color='#444444'><b>{cell[0].text}</b></font><br/>"
                    f"<font size='9'>{cell[1].text}</font>",
                    getSampleStyleSheet()["Normal"],
                )
                flat_row.append(combined)
            else:
                flat_row.append(cell)
        table_data.append(flat_row)

    num_cols = max(len(r) for r in table_data) if table_data else 2
    if colWidths is None:
        page_width = A4[0] - 30 * mm
        colWidths = [page_width / num_cols] * num_cols

    table = Table(table_data, colWidths=colWidths)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table
