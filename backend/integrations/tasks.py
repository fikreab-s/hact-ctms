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

        study_oid = subject.study.openclinica_study_oid
        if not study_oid:
            logger.info(
                "Study %s has no OC OID — skipping OC sync for subject %s",
                subject.study.protocol_number,
                subject.subject_identifier,
            )
            return {"status": "skipped", "reason": "no_study_oid"}

        site_oid = subject.site.site_code if subject.site else ""

        result = create_study_subject(
            study_oid=study_oid,
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

        study_oid = subject.study.openclinica_study_oid
        event_oid = visit.openclinica_event_definition_oid

        if not study_oid or not event_oid:
            logger.info(
                "Missing OC OIDs — skipping event schedule (study_oid=%s, event_oid=%s)",
                study_oid,
                event_oid,
            )
            return {"status": "skipped", "reason": "missing_oids"}

        result = schedule_event(
            study_oid=study_oid,
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
