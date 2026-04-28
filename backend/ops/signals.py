import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from clinical.models import Site

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Site)
def site_post_save(sender, instance, created, **kwargs):
    """
    Trigger site synchronization to ERPNext when a site is created or updated.
    """
    try:
        from integrations.tasks import sync_site_to_erpnext
        
        # Dispatch to Celery task
        # Pass the ID, not the object, to avoid serialization issues
        sync_site_to_erpnext.delay(str(instance.id))
        
        logger.info(f"{'Created' if created else 'Updated'} Site {instance.name}. Triggered ERPNext sync.")
        
    except Exception as e:
        logger.error(f"Failed to trigger ERPNext sync for Site {instance.id}: {str(e)}")
