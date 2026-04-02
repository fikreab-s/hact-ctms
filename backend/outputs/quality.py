"""
Outputs — Data Quality Calculation Engine
=============================================
Generates comprehensive data quality reports for a study.
Currently triggered on-demand via API; Celery Beat scheduling
will be added in a future phase.

Report Types:
- missing_data: Required fields without values
- query_status: Open/answered/closed query counts by site
- enrollment: Target vs actual enrollment by site
- completion: Form completion rates per visit
- visit_compliance: % of visits within protocol windows
- comprehensive: All of the above combined
"""

from collections import defaultdict
from datetime import date

from django.db.models import Count, Q


def generate_quality_report(study, report_type="comprehensive"):
    """Generate quality report data for a study.

    Args:
        study: Study model instance
        report_type: One of 'missing_data', 'query_status',
                     'enrollment', 'completion', 'visit_compliance',
                     'comprehensive'

    Returns:
        dict: Structured report data (saved to DataQualityReport.report_data)
    """
    generators = {
        "missing_data": _calc_missing_data,
        "query_status": _calc_query_status,
        "enrollment": _calc_enrollment_progress,
        "completion": _calc_form_completion,
        "visit_compliance": _calc_visit_compliance,
    }

    if report_type == "comprehensive":
        report_data = {
            "report_type": "comprehensive",
            "study_protocol": study.protocol_number,
            "study_name": study.name,
            "study_status": study.status,
            "generated_date": date.today().isoformat(),
            "sections": {},
        }
        for name, func in generators.items():
            report_data["sections"][name] = func(study)
        report_data["summary"] = _calc_summary(report_data["sections"])
        return report_data
    elif report_type in generators:
        return {
            "report_type": report_type,
            "study_protocol": study.protocol_number,
            "generated_date": date.today().isoformat(),
            "data": generators[report_type](study),
        }
    else:
        raise ValueError(f"Unknown report type: {report_type}")


# =============================================================================
# Individual Quality Calculators
# =============================================================================


def _calc_missing_data(study):
    """Find required fields without values across all submitted forms."""
    from clinical.models import Form, FormInstance, Item, ItemResponse

    results = []
    forms = Form.objects.filter(study=study, is_active=True).prefetch_related("items")

    for form in forms:
        required_items = Item.objects.filter(form=form, required=True)
        if not required_items.exists():
            continue

        form_instances = FormInstance.objects.filter(
            form=form,
            subject__study=study,
        ).select_related("subject")

        for fi in form_instances:
            filled_item_ids = set(
                ItemResponse.objects.filter(form_instance=fi)
                .exclude(value="")
                .values_list("item_id", flat=True)
            )

            missing = []
            for item in required_items:
                if item.id not in filled_item_ids:
                    missing.append({
                        "field_name": item.field_name,
                        "field_label": item.field_label,
                    })

            if missing:
                results.append({
                    "subject_id": fi.subject.subject_identifier,
                    "form_name": form.name,
                    "form_instance_id": fi.id,
                    "status": fi.status,
                    "missing_fields": missing,
                    "missing_count": len(missing),
                })

    total_missing = sum(r["missing_count"] for r in results)

    return {
        "total_missing_fields": total_missing,
        "forms_with_missing_data": len(results),
        "details": results,
    }


def _calc_query_status(study):
    """Calculate query metrics by site and status."""
    from clinical.models import Query

    queries = Query.objects.filter(
        item_response__form_instance__subject__study=study
    ).select_related(
        "item_response__form_instance__subject__site"
    )

    # Overall counts
    total = queries.count()
    by_status = dict(
        queries.values_list("status").annotate(count=Count("id")).values_list("status", "count")
    )

    # Per-site breakdown
    site_data = defaultdict(lambda: {"open": 0, "answered": 0, "closed": 0, "total": 0})
    for q in queries:
        site_code = q.item_response.form_instance.subject.site.site_code
        site_data[site_code][q.status] += 1
        site_data[site_code]["total"] += 1

    return {
        "total_queries": total,
        "open": by_status.get("open", 0),
        "answered": by_status.get("answered", 0),
        "closed": by_status.get("closed", 0),
        "resolution_rate": (
            round(by_status.get("closed", 0) / total * 100, 1) if total > 0 else 100.0
        ),
        "by_site": dict(site_data),
    }


def _calc_enrollment_progress(study):
    """Calculate enrollment progress by site."""
    from clinical.models import Site, Subject

    sites = Site.objects.filter(study=study)
    site_data = []

    total_enrolled = 0
    total_subjects = 0

    for site in sites:
        subjects = Subject.objects.filter(site=site)
        enrolled = subjects.filter(status="enrolled").count()
        all_count = subjects.count()

        total_enrolled += enrolled
        total_subjects += all_count

        site_data.append({
            "site_code": site.site_code,
            "site_name": site.name,
            "status": site.status,
            "total_subjects": all_count,
            "screened": subjects.filter(status="screened").count(),
            "enrolled": enrolled,
            "completed": subjects.filter(status="completed").count(),
            "discontinued": subjects.filter(status="discontinued").count(),
            "screen_failed": subjects.filter(status="screen_failed").count(),
        })

    return {
        "total_subjects": total_subjects,
        "total_enrolled": total_enrolled,
        "enrollment_rate": (
            round(total_enrolled / total_subjects * 100, 1) if total_subjects > 0 else 0
        ),
        "by_site": site_data,
    }


def _calc_form_completion(study):
    """Calculate form completion rates per form type."""
    from clinical.models import Form, FormInstance

    forms = Form.objects.filter(study=study, is_active=True)
    form_data = []

    total_instances = 0
    total_submitted = 0
    total_signed = 0

    for form in forms:
        instances = FormInstance.objects.filter(
            form=form, subject__study=study
        )
        count = instances.count()
        submitted = instances.filter(status__in=["submitted", "signed", "locked"]).count()
        signed = instances.filter(status__in=["signed", "locked"]).count()
        drafts = instances.filter(status="draft").count()

        total_instances += count
        total_submitted += submitted
        total_signed += signed

        form_data.append({
            "form_name": form.name,
            "total_instances": count,
            "draft": drafts,
            "submitted": submitted,
            "signed": signed,
            "completion_rate": round(submitted / count * 100, 1) if count > 0 else 0,
            "signature_rate": round(signed / count * 100, 1) if count > 0 else 0,
        })

    return {
        "total_form_instances": total_instances,
        "overall_completion_rate": (
            round(total_submitted / total_instances * 100, 1) if total_instances > 0 else 0
        ),
        "overall_signature_rate": (
            round(total_signed / total_instances * 100, 1) if total_instances > 0 else 0
        ),
        "by_form": form_data,
    }


def _calc_visit_compliance(study):
    """Calculate visit window compliance rates."""
    from clinical.models import SubjectVisit

    subject_visits = (
        SubjectVisit.objects.filter(subject__study=study)
        .select_related("subject", "visit")
    )

    total = 0
    within = 0
    outside = 0
    not_evaluated = 0

    visit_data = defaultdict(lambda: {"total": 0, "within": 0, "outside": 0, "pending": 0})

    for sv in subject_visits:
        visit_name = sv.visit.visit_name
        visit_data[visit_name]["total"] += 1
        total += 1

        if sv.actual_date and sv.subject.enrollment_date:
            window_range = sv.visit.get_window_range(sv.subject.enrollment_date)
            if window_range:
                earliest, latest = window_range
                if earliest <= sv.actual_date <= latest:
                    within += 1
                    visit_data[visit_name]["within"] += 1
                else:
                    outside += 1
                    visit_data[visit_name]["outside"] += 1
            else:
                not_evaluated += 1
                visit_data[visit_name]["pending"] += 1
        else:
            not_evaluated += 1
            visit_data[visit_name]["pending"] += 1

    return {
        "total_visits": total,
        "within_window": within,
        "outside_window": outside,
        "not_evaluated": not_evaluated,
        "compliance_rate": (
            round(within / (within + outside) * 100, 1) if (within + outside) > 0 else 100.0
        ),
        "by_visit": {
            name: {
                **data,
                "compliance_rate": (
                    round(data["within"] / (data["within"] + data["outside"]) * 100, 1)
                    if (data["within"] + data["outside"]) > 0 else 100.0
                ),
            }
            for name, data in visit_data.items()
        },
    }


# =============================================================================
# Summary
# =============================================================================


def _calc_summary(sections):
    """Generate a high-level quality score summary."""
    missing = sections.get("missing_data", {})
    queries = sections.get("query_status", {})
    enrollment = sections.get("enrollment", {})
    completion = sections.get("completion", {})
    compliance = sections.get("visit_compliance", {})

    # Quality indicators (traffic light)
    indicators = []

    # Missing data
    total_missing = missing.get("total_missing_fields", 0)
    if total_missing == 0:
        indicators.append({"name": "Missing Data", "status": "green", "value": "None"})
    elif total_missing <= 5:
        indicators.append({"name": "Missing Data", "status": "yellow", "value": f"{total_missing} fields"})
    else:
        indicators.append({"name": "Missing Data", "status": "red", "value": f"{total_missing} fields"})

    # Open queries
    open_queries = queries.get("open", 0)
    if open_queries == 0:
        indicators.append({"name": "Open Queries", "status": "green", "value": "None"})
    elif open_queries <= 3:
        indicators.append({"name": "Open Queries", "status": "yellow", "value": str(open_queries)})
    else:
        indicators.append({"name": "Open Queries", "status": "red", "value": str(open_queries)})

    # Form completion
    comp_rate = completion.get("overall_completion_rate", 0)
    if comp_rate >= 95:
        indicators.append({"name": "Form Completion", "status": "green", "value": f"{comp_rate}%"})
    elif comp_rate >= 80:
        indicators.append({"name": "Form Completion", "status": "yellow", "value": f"{comp_rate}%"})
    else:
        indicators.append({"name": "Form Completion", "status": "red", "value": f"{comp_rate}%"})

    # Visit compliance
    visit_rate = compliance.get("compliance_rate", 100)
    if visit_rate >= 95:
        indicators.append({"name": "Visit Compliance", "status": "green", "value": f"{visit_rate}%"})
    elif visit_rate >= 80:
        indicators.append({"name": "Visit Compliance", "status": "yellow", "value": f"{visit_rate}%"})
    else:
        indicators.append({"name": "Visit Compliance", "status": "red", "value": f"{visit_rate}%"})

    return {
        "indicators": indicators,
        "overall_status": (
            "green" if all(i["status"] == "green" for i in indicators)
            else "red" if any(i["status"] == "red" for i in indicators)
            else "yellow"
        ),
    }
