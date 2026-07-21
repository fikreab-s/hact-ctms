"""
HACT CTMS — Integration Celery Tasks
=====================================
Async tasks for syncing data between Django and external systems.
Tasks are safe to run even if external systems are offline — they
log warnings and can be retried automatically.
"""

import logging

from celery import shared_task

logger = logging.getLogger("hact.integrations.tasks")


# =============================================================================
# OpenClinica Sync Tasks
# =============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.sync_subject_to_openclinica",
)
def sync_subject_to_openclinica(self, subject_id: int):
    """
    Sync a newly enrolled subject to OpenClinica.
    Called after subject creation in Django.
    """
    from integrations.openclinica import create_study_subject, is_available

    if not is_available():
        logger.warning("OpenClinica not available — retrying in 60s (subject_id=%s)", subject_id)
        raise self.retry(exc=Exception("OpenClinica not available"))

    try:
        # Import here to avoid circular imports
        from clinical.models import Subject

        subject = Subject.objects.select_related("study", "site").get(id=subject_id)

        # OpenClinica SOAP web services match a study by its **Unique Protocol ID**
        # (study:unique_identifier), NOT the S_… OID. Prefer the dedicated field;
        # fall back to the OID field (legacy) only if the identifier is unset.
        study = subject.study
        study_identifier = study.openclinica_study_identifier or study.openclinica_study_oid
        if not study_identifier:
            logger.info(
                "Study %s has no OpenClinica identifier — skipping OC sync for subject %s",
                study.protocol_number,
                subject.subject_identifier,
            )
            return {"status": "skipped", "reason": "no_study_identifier"}

        # Site is matched by its Unique (Site) Protocol ID, which we mirror as site_code.
        site_oid = subject.site.site_code if subject.site else ""

        result = create_study_subject(
            study_oid=study_identifier,
            site_oid=site_oid,
            subject_label=subject.subject_identifier,
            enrollment_date=str(subject.enrollment_date or subject.created_at.date()),
            gender="m",  # Default — OC requires this field
        )

        if result["success"]:
            logger.info(
                "✅ Subject %s synced to OpenClinica (OID: %s)",
                subject.subject_identifier,
                result.get("subject_oid"),
            )
            return {"status": "success", "oc_oid": result.get("subject_oid")}
        else:
            logger.error(
                "❌ Failed to sync subject %s to OC: %s",
                subject.subject_identifier,
                result.get("error"),
            )
            raise self.retry(exc=Exception(result.get("error")))

    except Exception as e:
        logger.exception("Error syncing subject %s to OpenClinica", subject_id)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.sync_form_data_to_openclinica",
)
def sync_form_data_to_openclinica(self, form_instance_id: int):
    """
    Sync form instance data (item responses) to OpenClinica via ODM XML import.
    Called when a form is submitted in Django.
    """
    from integrations.openclinica import (
        build_odm_for_form_instance,
        import_data_odm,
        is_available,
    )

    if not is_available():
        logger.warning(
            "OpenClinica not available — retrying in 60s (form_instance_id=%s)",
            form_instance_id,
        )
        raise self.retry(exc=Exception("OpenClinica not available"))

    try:
        from clinical.models import FormInstance

        form_instance = (
            FormInstance.objects.select_related(
                "subject", "subject__study", "form", "subject_visit", "subject_visit__visit"
            )
            .prefetch_related("responses", "responses__item")
            .get(id=form_instance_id)
        )

        # Only sync if the study has an OC OID configured
        study = form_instance.subject.study
        if not study.openclinica_study_oid:
            logger.info("Study %s has no OC OID — skipping form sync", study.protocol_number)
            return {"status": "skipped", "reason": "no_study_oid"}

        # Build ODM XML from form instance
        odm_xml = build_odm_for_form_instance(form_instance)

        # Import into OpenClinica
        result = import_data_odm(odm_xml)

        if result["success"]:
            logger.info(
                "✅ Form data synced to OC (form_instance=%s, study=%s)",
                form_instance_id,
                study.protocol_number,
            )
            return {"status": "success"}
        else:
            logger.error(
                "❌ ODM import failed for form_instance %s: %s",
                form_instance_id,
                result.get("error"),
            )
            raise self.retry(exc=Exception(result.get("error")))

    except Exception as e:
        logger.exception("Error syncing form data %s to OpenClinica", form_instance_id)
        raise self.retry(exc=e)


@shared_task(name="integrations.check_openclinica_health")
def check_openclinica_health():
    """
    Periodic health check for OpenClinica.
    Can be scheduled via Celery Beat to monitor OC availability.
    """
    from integrations.openclinica import is_available, list_studies

    available = is_available()
    logger.info("OpenClinica health check: %s", "✅ Available" if available else "❌ Down")

    if available:
        studies = list_studies()
        logger.info("OpenClinica has %d studies", len(studies))
        return {"status": "healthy", "studies_count": len(studies)}

    return {"status": "unavailable"}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.schedule_event_in_openclinica",
)
def schedule_event_in_openclinica(
    self, subject_id: int, visit_id: int, start_date: str
):
    """
    Schedule a visit event in OpenClinica for a subject.
    Called when a SubjectVisit is created or updated in Django.
    """
    from integrations.openclinica import is_available, schedule_event

    if not is_available():
        logger.warning("OpenClinica not available — retrying")
        raise self.retry(exc=Exception("OpenClinica not available"))

    try:
        from clinical.models import Subject, Visit

        subject = Subject.objects.select_related("study").get(id=subject_id)
        visit = Visit.objects.get(id=visit_id)

        # SOAP EventService matches the study by Unique Protocol ID, not the OID.
        study = subject.study
        study_identifier = study.openclinica_study_identifier or study.openclinica_study_oid
        event_oid = visit.openclinica_event_definition_oid

        if not study_identifier or not event_oid:
            logger.info(
                "Missing OC identifiers — skipping event schedule (study=%s, event_oid=%s)",
                study_identifier,
                event_oid,
            )
            return {"status": "skipped", "reason": "missing_oids"}

        result = schedule_event(
            study_oid=study_identifier,
            subject_label=subject.subject_identifier,
            event_definition_oid=event_oid,
            start_date=start_date,
        )

        if result["success"]:
            logger.info(
                "✅ Event %s scheduled in OC for subject %s",
                event_oid,
                subject.subject_identifier,
            )
            return {"status": "success"}
        else:
            logger.error("❌ Event scheduling failed: %s", result.get("error"))
            raise self.retry(exc=Exception(result.get("error")))

    except Exception as e:
        logger.exception("Error scheduling event in OpenClinica")
        raise self.retry(exc=e)


# =============================================================================
# Nextcloud eTMF Tasks
# =============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="integrations.create_etmf_for_study",
)
def create_etmf_for_study(self, protocol_number: str):
    """
    Create the eTMF folder structure in Nextcloud for a new study.
    Called when a Study is created in Django.
    """
    from integrations.nextcloud import create_etmf_structure, is_available

    if not is_available():
        logger.warning("Nextcloud not available — retrying in 30s (study=%s)", protocol_number)
        raise self.retry(exc=Exception("Nextcloud not available"))

    try:
        ok = create_etmf_structure(protocol_number)
        if ok:
            logger.info("✅ eTMF structure created in Nextcloud for %s", protocol_number)
            return {"status": "success", "protocol": protocol_number}
        else:
            raise self.retry(exc=Exception("eTMF folder creation failed"))

    except Exception as e:
        logger.exception("Error creating eTMF for %s", protocol_number)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="integrations.create_site_etmf",
)
def create_site_etmf(self, protocol_number: str, site_code: str):
    """
    Create the per-site eTMF subfolder tree in Nextcloud for a new site.
    Called when a Site is created in Django.
    """
    from integrations.nextcloud import create_site_etmf_folder, is_available

    if not is_available():
        logger.warning(
            "Nextcloud not available — retrying in 30s (site=%s/%s)",
            protocol_number, site_code,
        )
        raise self.retry(exc=Exception("Nextcloud not available"))

    try:
        ok = create_site_etmf_folder(protocol_number, site_code)
        if ok:
            logger.info("✅ eTMF site folder created in Nextcloud for %s / %s", protocol_number, site_code)
            return {"status": "success", "protocol": protocol_number, "site": site_code}
        raise self.retry(exc=Exception("eTMF site folder creation failed"))

    except Exception as e:
        logger.exception("Error creating eTMF site folder for %s / %s", protocol_number, site_code)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="integrations.upload_document_to_etmf",
)
def upload_document_to_etmf(
    self,
    protocol_number: str,
    category: str,
    filename: str,
    content_b64: str,
    content_type: str = "application/pdf",
):
    """
    Upload a document to the eTMF in Nextcloud.
    Content is passed as base64-encoded string (Celery-serializable).
    """
    import base64
    from integrations.nextcloud import upload_to_etmf, is_available

    if not is_available():
        logger.warning("Nextcloud not available — retrying")
        raise self.retry(exc=Exception("Nextcloud not available"))

    try:
        content = base64.b64decode(content_b64)
        url = upload_to_etmf(protocol_number, category, filename, content, content_type)

        if url:
            logger.info("✅ Document uploaded to eTMF: %s/%s/%s", protocol_number, category, filename)
            return {"status": "success", "url": url}
        else:
            raise self.retry(exc=Exception("Document upload failed"))

    except Exception as e:
        logger.exception("Error uploading document to eTMF")
        raise self.retry(exc=e)


@shared_task(name="integrations.check_nextcloud_health")
def check_nextcloud_health():
    """
    Periodic health check for Nextcloud.
    Can be scheduled via Celery Beat to monitor availability.
    """
    from integrations.nextcloud import is_available, get_server_info, list_etmf_studies

    available = is_available()
    logger.info("Nextcloud health check: %s", "✅ Available" if available else "❌ Down")

    if available:
        info = get_server_info() or {}
        studies = list_etmf_studies()
        return {
            "status": "healthy",
            "version": info.get("versionstring", "unknown"),
            "etmf_studies": len(studies),
        }

    return {"status": "unavailable"}

# =============================================================================
# ERPNext Tasks
# =============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.sync_site_to_erpnext",
)
def sync_site_to_erpnext(self, site_id):
    """
    Sync a Django Site to an ERPNext Customer.
    """
    from clinical.models import Site
    from integrations.erpnext import sync_site_to_customer
    
    try:
        site = Site.objects.get(id=site_id)
        
        # Prepare data
        site_data = {
            "name": site.name,
            "code": site.site_code,
            "status": site.status
        }
        
        erpnext_id = sync_site_to_customer(site_data)
        
        # Save ERPNext ID back to site
        if erpnext_id and not site.erpnext_site_id:
            site.erpnext_site_id = erpnext_id
            site.save(update_fields=['erpnext_site_id'])
            
        return f"Site {site.name} synced to ERPNext as {erpnext_id}"
        
    except Site.DoesNotExist:
        logger.error(f"Site {site_id} not found.")
        return None
    except Exception as e:
        logger.error(f"ERPNext sync failed: {str(e)}")
        raise self.retry(exc=e)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.check_erpnext_health",
)
def check_erpnext_health(self):
    """Periodic task to verify ERPNext API connectivity."""
    from integrations.erpnext import check_availability
    
    is_up = check_availability()
    if not is_up:
        logger.warning("ERPNext health check failed. Retrying in 60s...")
        raise self.retry()
    return True


# =============================================================================
# SENAITE Integration Tasks (Laboratory)
# =============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="integrations.sync_sample_to_senaite",
)
def sync_sample_to_senaite(self, sample_id):
    """
    Push a SampleCollection record from Django to SENAITE as an AnalysisRequest.
    Triggered when a new SampleCollection is created.
    """
    from lab.models import SampleCollection
    from integrations.senaite import create_sample

    try:
        sample = SampleCollection.objects.select_related(
            "subject", "subject__study"
        ).get(id=sample_id)

        # Already pushed? Don't create a duplicate AnalysisRequest in SENAITE.
        if sample.senaite_sample_id:
            logger.info(
                "SampleCollection %s already linked to SENAITE %s — skipping push.",
                sample_id, sample.senaite_sample_id,
            )
            return {"status": "skipped", "reason": "already_synced"}

        study = getattr(sample.subject, "study", None)
        client_title = (
            getattr(study, "senaite_client_title", "") or "HACT Clinical Trials"
        )

        sample_data = {
            "client_title": client_title,
            "sample_type": sample.sample_type,
            "subject_identifier": sample.subject.subject_identifier,
        }

        result = create_sample(sample_data)

        if result.get("success") and result.get("senaite_id"):
            sample.senaite_sample_id = result["senaite_id"]
            sample.save(update_fields=["senaite_sample_id"])
            logger.info("Sample %s synced to SENAITE: %s", sample_id, result["senaite_id"])
            return f"Sample {sample_id} synced to SENAITE as {result['senaite_id']}"
        else:
            logger.warning("SENAITE sample creation returned no ID: %s", result.get("error"))
            return None

    except SampleCollection.DoesNotExist:
        logger.error("SampleCollection %s not found.", sample_id)
        return None
    except Exception as e:
        logger.error("SENAITE sample sync failed: %s", str(e))
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    name="integrations.pull_results_from_senaite",
)
def pull_results_from_senaite(self, study_id=None):
    """
    Pull published lab results from SENAITE and import into Django LabResult.
    Auto-flags results (H/L/N) based on ReferenceRange.

    Can be called on-demand or scheduled via Celery Beat.
    """
    from decimal import Decimal, InvalidOperation
    from django.utils import timezone
    from lab.models import LabResult, ReferenceRange
    from clinical.models import Study, Subject

    from integrations.senaite import fetch_published_results, parse_senaite_date

    try:
        # Scope the pull to the study's SENAITE Client when a study is given.
        client_title = "HACT Clinical Trials"
        if study_id:
            study = Study.objects.filter(id=study_id).first()
            if study and study.senaite_client_title:
                client_title = study.senaite_client_title

        results = fetch_published_results(client_title=client_title)

        if not results:
            logger.info("No published results found in SENAITE.")
            return "No results to import."

        # Load reference ranges for flagging. A test can have several ranges
        # (per gender); since CTMS Subjects carry no demographic sex here, prefer
        # the gender-agnostic ('all') range for deterministic flagging instead of
        # letting an arbitrary "last one wins".
        ref_ranges = {}
        rr_qs = ReferenceRange.objects.all()
        if study_id:
            rr_qs = rr_qs.filter(study_id=study_id)
        for rr in rr_qs:
            key = rr.test_name.lower()
            existing = ref_ranges.get(key)
            if existing is None or (existing.gender != "all" and rr.gender == "all"):
                ref_ranges[key] = rr

        imported = 0
        skipped = 0

        for row in results:
            subject_id = (row.get("subject_identifier") or "").strip()
            test_name = (row.get("test_name") or "").strip()
            result_value = (row.get("result_value") or "").strip()
            analysis_uid = (row.get("senaite_analysis_uid") or "").strip()

            if not subject_id or not test_name or not result_value:
                skipped += 1
                continue

            # Find subject
            subject_qs = Subject.objects.filter(subject_identifier=subject_id)
            if study_id:
                subject_qs = subject_qs.filter(study_id=study_id)
            subject = subject_qs.first()

            if not subject:
                skipped += 1
                continue

            # De-duplicate on the SENAITE Analysis UID when available (stable and
            # unique per result). Fall back to the legacy value-based check only
            # for older rows that predate provenance tracking.
            if analysis_uid:
                exists = LabResult.objects.filter(
                    senaite_analysis_uid=analysis_uid
                ).exists()
            else:
                exists = LabResult.objects.filter(
                    subject=subject,
                    test_name=test_name,
                    result_value=result_value,
                ).exists()

            if exists:
                skipped += 1
                continue

            # Auto-flag
            flag = ""
            ref_low = None
            ref_high = None
            rr = ref_ranges.get(test_name.lower())
            if rr:
                ref_low = rr.range_low
                ref_high = rr.range_high
                try:
                    val = Decimal(result_value)
                    if val < rr.range_low:
                        flag = "L"
                    elif val > rr.range_high:
                        flag = "H"
                    else:
                        flag = "N"
                except (InvalidOperation, ValueError):
                    flag = ""

            # Import result — use the real SENAITE result date when parseable.
            result_date = parse_senaite_date(row.get("result_date")) or timezone.now().date()
            LabResult.objects.create(
                subject=subject,
                test_name=test_name,
                result_value=result_value,
                unit=row.get("unit", ""),
                reference_range_low=ref_low,
                reference_range_high=ref_high,
                flag=flag,
                result_date=result_date,
                senaite_sample_id=row.get("senaite_sample_id", ""),
                senaite_analysis_uid=analysis_uid,
            )
            imported += 1

        logger.info("SENAITE import complete: %d imported, %d skipped", imported, skipped)
        return f"Imported {imported} results, skipped {skipped}"

    except Exception as e:
        logger.error("SENAITE result pull failed: %s", str(e))
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="integrations.check_senaite_health",
)
def check_senaite_health(self):
    """Periodic task to verify SENAITE API connectivity."""
    from integrations.senaite import check_availability

    is_up = check_availability()
    if not is_up:
        logger.warning("SENAITE health check failed. Retrying in 60s...")
        raise self.retry()
    return True
