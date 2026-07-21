"""Lab signals — external-system provisioning.

On SampleCollection creation, push the sample to SENAITE as an AnalysisRequest so
the lab can receive/analyse it. This mirrors the OpenClinica/ERPNext/Nextcloud
signal pattern (clinical/signals.py, ops/signals.py): dispatch a Celery task with
the object id (never the object) to stay serialization-safe and non-blocking.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SampleCollection

logger = logging.getLogger("hact.lab.signals")


@receiver(post_save, sender=SampleCollection)
def sample_collection_post_save(sender, instance, created, **kwargs):
    """Register a newly collected sample in SENAITE (once, if not already linked)."""
    if not created or instance.senaite_sample_id:
        return

    try:
        from integrations.tasks import sync_sample_to_senaite

        sync_sample_to_senaite.delay(instance.id)
        logger.info(
            "Triggered SENAITE sample push for SampleCollection %s (subject %s).",
            instance.id, instance.subject_id,
        )
    except Exception as e:  # noqa: BLE001 — never block sample creation on dispatch
        logger.error(
            "Failed to trigger SENAITE sample push for SampleCollection %s: %s",
            instance.id, str(e),
        )
