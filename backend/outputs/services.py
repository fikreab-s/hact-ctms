"""
Outputs — CSV Export Service
==============================
Generates CSV export files for all clinical data in a study.
Exports are saved to Django's MEDIA_ROOT/exports/ directory.
When Nextcloud is integrated (Day 9+), the file writing logic
will be swapped to push files via WebDAV instead.
"""

import csv
import io
import os
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings


def _ensure_export_dir(study_protocol):
    """Create the export directory structure: media/exports/<protocol>/."""
    export_dir = Path(settings.MEDIA_ROOT) / "exports" / study_protocol
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# Individual CSV Export Functions
# =============================================================================


def export_subjects_csv(study):
    """Export subject demographics and enrollment data."""
    from clinical.models import Subject

    subjects = Subject.objects.filter(study=study).select_related("site").order_by(
        "subject_identifier"
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "Screening Number", "Site Code", "Site Name",
        "Status", "Consent Date", "Enrollment Date", "Completion Date",
        "Created At",
    ])

    for s in subjects:
        writer.writerow([
            s.subject_identifier,
            s.screening_number or "",
            s.site.site_code,
            s.site.name,
            s.status,
            s.consent_signed_date or "",
            s.enrollment_date or "",
            s.completion_date or "",
            s.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return output.getvalue()


def export_visits_csv(study):
    """Export subject visit schedule with window compliance."""
    from clinical.models import SubjectVisit

    visits = (
        SubjectVisit.objects.filter(subject__study=study)
        .select_related("subject", "visit")
        .order_by("subject__subject_identifier", "visit__visit_order")
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "Visit Name", "Visit Order", "Planned Day",
        "Scheduled Date", "Actual Date", "Status",
        "Window Before", "Window After", "Within Window",
    ])

    for sv in visits:
        # Calculate window compliance
        within_window = ""
        if sv.actual_date and sv.subject.enrollment_date:
            window_range = sv.visit.get_window_range(sv.subject.enrollment_date)
            if window_range:
                earliest, latest = window_range
                within_window = "Yes" if earliest <= sv.actual_date <= latest else "No"

        writer.writerow([
            sv.subject.subject_identifier,
            sv.visit.visit_name,
            sv.visit.visit_order,
            sv.visit.planned_day,
            sv.scheduled_date or "",
            sv.actual_date or "",
            sv.status,
            sv.visit.window_before or "",
            sv.visit.window_after or "",
            within_window,
        ])

    return output.getvalue()


def export_form_data_csv(study):
    """Export all form instance responses (one row per item response)."""
    from clinical.models import ItemResponse

    responses = (
        ItemResponse.objects.filter(form_instance__subject__study=study)
        .select_related(
            "form_instance__form",
            "form_instance__subject",
            "form_instance__subject_visit__visit",
            "item",
        )
        .order_by(
            "form_instance__subject__subject_identifier",
            "form_instance__form__name",
            "item__order",
        )
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "Visit", "Form Name", "Form Status",
        "Field Name", "Field Label", "Field Type", "Value",
        "Submitted At", "Signed By", "Signed At",
    ])

    for ir in responses:
        fi = ir.form_instance
        visit_name = ""
        if fi.subject_visit:
            visit_name = fi.subject_visit.visit.visit_name

        writer.writerow([
            fi.subject.subject_identifier,
            visit_name,
            fi.form.name,
            fi.status,
            ir.item.field_name,
            ir.item.field_label,
            ir.item.field_type,
            ir.value,
            fi.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if fi.submitted_at else "",
            fi.signed_by.username if fi.signed_by else "",
            fi.signed_at.strftime("%Y-%m-%d %H:%M:%S") if fi.signed_at else "",
        ])

    return output.getvalue()


def export_adverse_events_csv(study):
    """Export adverse events listing."""
    from safety.models import AdverseEvent

    events = (
        AdverseEvent.objects.filter(study=study)
        .select_related("subject", "reported_by")
        .order_by("subject__subject_identifier", "start_date")
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "AE Term", "Start Date", "End Date",
        "Severity", "Serious", "Serious Criteria", "Causality",
        "Outcome", "Action Taken", "Reported At", "Reported By",
    ])

    for ae in events:
        writer.writerow([
            ae.subject.subject_identifier,
            ae.ae_term,
            ae.start_date or "",
            ae.end_date or "",
            ae.severity,
            "Yes" if ae.serious else "No",
            ae.serious_criteria or "",
            ae.causality or "",
            ae.outcome or "",
            ae.action_taken or "",
            ae.reported_at.strftime("%Y-%m-%d %H:%M:%S") if ae.reported_at else "",
            ae.reported_by.username if ae.reported_by else "",
        ])

    return output.getvalue()


def export_lab_results_csv(study):
    """Export lab results with reference ranges and flags."""
    from lab.models import LabResult

    results = (
        LabResult.objects.filter(subject__study=study)
        .select_related("subject", "subject_visit__visit")
        .order_by("subject__subject_identifier", "result_date", "test_name")
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "Visit", "Test Name", "Result Value", "Unit",
        "Ref Range Low", "Ref Range High", "Flag",
        "Result Date", "Imported At",
    ])

    for lr in results:
        visit_name = ""
        if lr.subject_visit:
            visit_name = lr.subject_visit.visit.visit_name

        writer.writerow([
            lr.subject.subject_identifier,
            visit_name,
            lr.test_name,
            lr.result_value,
            lr.unit,
            lr.reference_range_low or "",
            lr.reference_range_high or "",
            lr.flag or "",
            lr.result_date or "",
            lr.imported_at.strftime("%Y-%m-%d %H:%M:%S") if lr.imported_at else "",
        ])

    return output.getvalue()


def export_queries_csv(study):
    """Export data queries with lifecycle information."""
    from clinical.models import Query

    queries = (
        Query.objects.filter(item_response__form_instance__subject__study=study)
        .select_related(
            "item_response__form_instance__subject",
            "item_response__form_instance__form",
            "item_response__item",
            "raised_by",
            "resolved_by",
        )
        .order_by("-raised_at")
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Subject ID", "Form Name", "Field Name", "Current Value",
        "Query Text", "Status", "Response Text",
        "Raised By", "Raised At", "Resolved By", "Resolved At",
    ])

    for q in queries:
        ir = q.item_response
        writer.writerow([
            ir.form_instance.subject.subject_identifier,
            ir.form_instance.form.name,
            ir.item.field_name,
            ir.value,
            q.query_text,
            q.status,
            q.response_text or "",
            q.raised_by.username if q.raised_by else "",
            q.raised_at.strftime("%Y-%m-%d %H:%M:%S") if q.raised_at else "",
            q.resolved_by.username if q.resolved_by else "",
            q.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if q.resolved_at else "",
        ])

    return output.getvalue()


# =============================================================================
# Bundled ZIP Export
# =============================================================================


def export_study_zip(study, user=None):
    """Bundle all CSV exports into a single ZIP file.

    Returns:
        tuple: (file_path, snapshot_record)
    """
    from outputs.models import DatasetSnapshot

    ts = _timestamp()
    export_dir = _ensure_export_dir(study.protocol_number)
    zip_filename = f"{study.protocol_number}_raw_export_{ts}.zip"
    zip_path = export_dir / zip_filename

    csv_files = {
        "subjects.csv": export_subjects_csv(study),
        "visits.csv": export_visits_csv(study),
        "form_data.csv": export_form_data_csv(study),
        "adverse_events.csv": export_adverse_events_csv(study),
        "lab_results.csv": export_lab_results_csv(study),
        "queries.csv": export_queries_csv(study),
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in csv_files.items():
            zf.writestr(name, content)

    # Create snapshot record
    relative_url = f"/media/exports/{study.protocol_number}/{zip_filename}"
    snapshot = DatasetSnapshot.objects.create(
        study=study,
        snapshot_type="raw",
        file_url=relative_url,
        generated_by=user,
        description=f"Raw CSV data export generated on {ts}.",
        criteria={
            "export_type": "csv_zip",
            "files_included": list(csv_files.keys()),
            "timestamp": ts,
        },
    )

    return str(zip_path), snapshot
