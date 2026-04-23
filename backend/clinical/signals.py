"""
Clinical signals — Integration hooks for external systems.
Connects Django model lifecycle events to Celery tasks for
OpenClinica sync and Nextcloud eTMF folder management.
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
    2. Sync study to OpenClinica (if OC OID is configured)
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
