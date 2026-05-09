"""
Clinical signals — Integration hooks for external systems.
Connects Django model lifecycle events to Celery tasks for
OpenClinica sync, Nextcloud eTMF folder management, and SENAITE lab sync.

Auto-trigger rules:
  - Study created       → Nextcloud eTMF folder
  - Subject enrolled    → OpenClinica subject sync
  - FormInstance submit  → OpenClinica ODM data import
  - SubjectVisit created → OpenClinica event schedule
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("hact.clinical.signals")


@receiver(post_save, sender="clinical.Study")
def study_post_save(sender, instance, created, **kwargs):
    """
    When a Study is created, automatically:
    1. Create eTMF folder structure in Nextcloud (if available)
    """
    if not created:
        return

    protocol = instance.protocol_number

    # --- Nextcloud: Create eTMF folder tree ---
    try:
        from integrations.tasks import create_etmf_for_study

        create_etmf_for_study.delay(protocol)
        logger.info(
            "Triggered eTMF creation in Nextcloud for study %s", protocol
        )
    except Exception as e:
        # Don't fail study creation if Nextcloud task can't be dispatched
        logger.warning(
            "Could not dispatch eTMF creation for %s: %s", protocol, e
        )


@receiver(post_save, sender="clinical.Subject")
def subject_post_save(sender, instance, created, **kwargs):
    """
    When a Subject is enrolled, sync to OpenClinica as a StudySubject.
    Only triggers if:
      - Subject status is 'enrolled'
      - Study has an openclinica_study_oid configured
    """
    if instance.status != "enrolled":
        return

    # Only sync if the study has an OC OID
    if not instance.study.openclinica_study_oid:
        return

    try:
        from integrations.tasks import sync_subject_to_openclinica

        sync_subject_to_openclinica.delay(instance.id)
        logger.info(
            "Triggered OC subject sync for %s (study: %s)",
            instance.subject_identifier,
            instance.study.protocol_number,
        )
    except Exception as e:
        logger.warning(
            "Could not dispatch OC subject sync for %s: %s",
            instance.subject_identifier, e,
        )


@receiver(post_save, sender="clinical.FormInstance")
def form_instance_post_save(sender, instance, created, **kwargs):
    """
    When a FormInstance is submitted, sync form data to OpenClinica via ODM XML.
    Only triggers if:
      - FormInstance status is 'submitted'
      - Study has an openclinica_study_oid configured
    """
    if instance.status != "submitted":
        return

    study = instance.subject.study
    if not study.openclinica_study_oid:
        return

    try:
        from integrations.tasks import sync_form_data_to_openclinica

        sync_form_data_to_openclinica.delay(instance.id)
        logger.info(
            "Triggered OC form data sync for form '%s' (subject: %s)",
            instance.form.name,
            instance.subject.subject_identifier,
        )
    except Exception as e:
        logger.warning(
            "Could not dispatch OC form sync for FormInstance %s: %s",
            instance.id, e,
        )


@receiver(post_save, sender="clinical.SubjectVisit")
def subject_visit_post_save(sender, instance, created, **kwargs):
    """
    When a SubjectVisit is created, schedule the event in OpenClinica.
    Only triggers if:
      - SubjectVisit was just created
      - Study has an openclinica_study_oid
      - Visit has an openclinica_event_definition_oid
    """
    if not created:
        return

    subject = instance.subject
    visit = instance.visit

    if not subject.study.openclinica_study_oid:
        return

    if not visit.openclinica_event_definition_oid:
        return

    # Use scheduled_date or actual_date
    start_date = str(
        instance.actual_date or instance.scheduled_date or instance.created_at.date()
    )

    try:
        from integrations.tasks import schedule_event_in_openclinica

        schedule_event_in_openclinica.delay(subject.id, visit.id, start_date)
        logger.info(
            "Triggered OC event schedule: %s for subject %s on %s",
            visit.visit_name,
            subject.subject_identifier,
            start_date,
        )
    except Exception as e:
        logger.warning(
            "Could not dispatch OC event schedule for SubjectVisit %s: %s",
            instance.id, e,
        )
