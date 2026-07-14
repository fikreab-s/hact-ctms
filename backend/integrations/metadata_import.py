"""
HACT CTMS — Import CRF metadata from OpenClinica into CTMS
==========================================================
Option A: OpenClinica is the source of truth for CRF *definitions*. This module
pulls a study's ODM metadata from OpenClinica, parses it, and upserts the
matching CTMS ``Visit`` / ``Form`` / ``Item`` / ``VisitForm`` rows — storing the
*real* OpenClinica OIDs so captured data round-trips back into OpenClinica.

Idempotent: re-running matches existing rows by OID (then by name) and updates
them in place, so it is safe to re-sync whenever the CRF changes in OC.
"""

import logging

from django.db import transaction

from clinical.models import Form, Item, Visit, VisitForm

from . import openclinica
from .openclinica_metadata import parse_odm_metadata

logger = logging.getLogger("hact.integrations.oc_metadata_import")


def import_study_metadata(study, dry_run=False):
    """Import CRF metadata from OpenClinica for ``study``.

    Args:
        study: clinical.Study instance (must have an OpenClinica identifier/OID).
        dry_run: if True, parse + compute the summary but write nothing.

    Returns a dict summary (safe to return straight from an API view).
    """
    identifier = study.openclinica_study_identifier or study.openclinica_study_oid
    if not identifier:
        return {
            "ok": False,
            "error": (
                "Study has no OpenClinica identifier. Set the 'OpenClinica "
                "Unique Protocol ID' (or Study OID) first."
            ),
        }

    odm_xml = openclinica.get_study_metadata(identifier)
    if not odm_xml:
        return {
            "ok": False,
            "error": (
                "OpenClinica returned no metadata for identifier "
                f"'{identifier}'. Check the study exists in OC, is 'available', "
                "and the WS account is authorized."
            ),
        }

    parsed = parse_odm_metadata(odm_xml)
    if not parsed:
        return {
            "ok": False,
            "error": "Could not parse the ODM metadata returned by OpenClinica.",
            "raw_odm": odm_xml[:4000],
        }

    summary = {
        "ok": True,
        "dry_run": dry_run,
        "identifier": identifier,
        "study_oid": parsed["study"].get("oid", ""),
        "counts": {
            "events": len(parsed["events"]),
            "forms": len(parsed["forms"]),
            "items": len(parsed["items"]),
        },
        "visits": {"created": 0, "updated": 0},
        "forms": {"created": 0, "updated": 0},
        "items": {"created": 0, "updated": 0},
        "visit_form_links": 0,
        "preview": _build_preview(parsed),
    }
    if dry_run:
        summary["raw_odm"] = odm_xml[:6000]
        return summary

    with transaction.atomic():
        # ── Visits (StudyEventDef) ──
        used_orders = set(
            Visit.objects.filter(study=study).values_list("visit_order", flat=True)
        )
        visit_by_oid = {}
        for ev in parsed["events"]:
            visit, created, order_taken = _upsert_visit(study, ev, used_orders)
            visit_by_oid[ev["oid"]] = visit
            used_orders.add(order_taken)
            summary["visits"]["created" if created else "updated"] += 1

        # ── Forms (FormDef) ──
        form_by_oid = {}
        for fm in parsed["forms"]:
            form, created = _upsert_form(study, fm)
            form_by_oid[fm["oid"]] = form
            summary["forms"]["created" if created else "updated"] += 1

        # ── Items (ItemDef, flattened per form) ──
        for it in parsed["items"]:
            form = form_by_oid.get(it["form_oid"])
            if form is None:
                continue
            created = _upsert_item(form, it)
            summary["items"]["created" if created else "updated"] += 1

        # ── VisitForm mappings (StudyEventDef -> FormRef) ──
        for ev in parsed["events"]:
            visit = visit_by_oid.get(ev["oid"])
            if visit is None:
                continue
            for foid in ev["form_oids"]:
                form = form_by_oid.get(foid)
                if form is None:
                    continue
                _, vf_created = VisitForm.objects.get_or_create(
                    visit=visit, form=form, defaults={"is_required": True}
                )
                if vf_created:
                    summary["visit_form_links"] += 1

    logger.info("OC metadata import for study %s: %s", study.id, summary["counts"])
    return summary


# ── Upsert helpers ───────────────────────────────────────────────────────────

def _upsert_visit(study, ev, used_orders):
    """Return (visit, created, order_used)."""
    visit = None
    if ev["oid"]:
        visit = Visit.objects.filter(
            study=study, openclinica_event_definition_oid=ev["oid"]
        ).first()
    if visit is None:
        visit = Visit.objects.filter(study=study, visit_name=ev["name"]).first()

    is_screening = ev["type"] == "scheduled" and "screen" in ev["name"].lower()

    if visit is None:
        order = ev["order"] if ev["order"] not in used_orders else _next_order(used_orders)
        visit = Visit.objects.create(
            study=study,
            visit_name=ev["name"],
            visit_order=order,
            planned_day=0,
            is_screening=is_screening,
            openclinica_event_definition_oid=ev["oid"],
        )
        return visit, True, order

    visit.visit_name = ev["name"]
    visit.openclinica_event_definition_oid = ev["oid"] or visit.openclinica_event_definition_oid
    visit.save(update_fields=["visit_name", "openclinica_event_definition_oid", "updated_at"])
    return visit, False, visit.visit_order


def _next_order(used_orders):
    order = 1
    while order in used_orders:
        order += 1
    return order


def _upsert_form(study, fm):
    """Return (form, created)."""
    form = None
    if fm["oid"]:
        form = Form.objects.filter(study=study, openclinica_crf_oid=fm["oid"]).first()
    if form is None:
        form = Form.objects.filter(study=study, name=fm["name"]).first()

    if form is None:
        form = Form.objects.create(
            study=study,
            name=fm["name"],
            version=fm["version"],
            is_active=True,
            openclinica_crf_oid=fm["oid"],
        )
        return form, True

    form.name = fm["name"]
    form.version = fm["version"] or form.version
    form.openclinica_crf_oid = fm["oid"] or form.openclinica_crf_oid
    form.is_active = True
    form.save(update_fields=["name", "version", "openclinica_crf_oid", "is_active", "updated_at"])
    return form, False


def _upsert_item(form, it):
    """Return created (bool). Matches by OC item OID, then field_name."""
    item = None
    if it["oid"]:
        item = Item.objects.filter(form=form, openclinica_item_oid=it["oid"]).first()
    if item is None:
        item = Item.objects.filter(form=form, field_name=it["name"]).first()

    fields = dict(
        field_label=it["label"],
        field_type=it["field_type"],
        required=it["required"],
        validation_rule=it.get("validation_rule", "") or "",
        options=it.get("options"),
        order=it.get("order", 0),
        openclinica_item_oid=it["oid"],
        openclinica_item_group_oid=it.get("group_oid", ""),
    )

    if item is None:
        Item.objects.create(form=form, field_name=it["name"], **fields)
        return True

    for k, v in fields.items():
        setattr(item, k, v)
    # Preserve CTMS-only overlays (display_condition / cross_field_validation /
    # section) — the OC import never clears them.
    item.save()
    return False


def _build_preview(parsed):
    """A compact, human-readable preview for the dry-run response / UI."""
    forms_by_oid = {f["oid"]: f["name"] for f in parsed["forms"]}
    items_by_form = {}
    for it in parsed["items"]:
        items_by_form.setdefault(it["form_oid"], []).append(it)

    preview_forms = []
    for f in parsed["forms"]:
        its = items_by_form.get(f["oid"], [])
        preview_forms.append({
            "name": f["name"],
            "oid": f["oid"],
            "item_count": len(its),
            "items": [
                {
                    "name": i["name"], "label": i["label"], "type": i["field_type"],
                    "required": i["required"],
                    "options": len(i["options"]) if i["options"] else 0,
                    "validation": i["validation_rule"],
                }
                for i in its
            ],
        })

    preview_events = [
        {
            "name": e["name"], "oid": e["oid"], "order": e["order"],
            "forms": [forms_by_oid.get(o, o) for o in e["form_oids"]],
        }
        for e in parsed["events"]
    ]
    return {"events": preview_events, "forms": preview_forms}
