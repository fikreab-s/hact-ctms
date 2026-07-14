import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from clinical.models import Site

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Site)
def site_post_save(sender, instance, created, **kwargs):
    """
    On Site save: sync the site to ERPNext (create/update Customer).
    On Site creation: also provision the per-site eTMF subfolder tree in Nextcloud
    under eTMF/{protocol}/06_SiteDocuments/{site_code}/.
    """
    try:
        from integrations.tasks import sync_site_to_erpnext

        # Dispatch to Celery task
        # Pass the ID, not the object, to avoid serialization issues
        sync_site_to_erpnext.delay(str(instance.id))

        logger.info(f"{'Created' if created else 'Updated'} Site {instance.name}. Triggered ERPNext sync.")

    except Exception as e:
        logger.error(f"Failed to trigger ERPNext sync for Site {instance.id}: {str(e)}")

    if created:
        try:
            from integrations.tasks import create_site_etmf

            protocol_number = instance.study.protocol_number
            create_site_etmf.delay(protocol_number, instance.site_code)

            logger.info(
                f"Triggered eTMF site-folder creation for {protocol_number} / {instance.site_code}."
            )

        except Exception as e:
            logger.error(f"Failed to trigger eTMF site-folder creation for Site {instance.id}: {str(e)}")
