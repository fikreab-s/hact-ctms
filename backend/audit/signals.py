"""
Audit Signals — Automatic audit trail population
===================================================
Generic post_save / post_delete signal handlers that automatically
create AuditLog entries for all model changes.

Excludes: AuditLog itself, Session, LogEntry, Migration (internal Django tables).
"""

import json
import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger("hact_ctms.audit")

# Tables to exclude from audit logging (internal/infrastructure)
EXCLUDED_TABLES = {
    "audit_log",
    "django_session",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_celery_beat_periodictask",
    "django_celery_beat_periodictasks",
    "django_celery_beat_crontabschedule",
    "django_celery_beat_intervalschedule",
    "django_celery_beat_solarschedule",
    "django_celery_beat_clockedschedule",
}


def _model_to_dict(instance):
    """Convert a model instance to a JSON-serializable dict."""
    from django.forms.models import model_to_dict

    try:
        data = model_to_dict(instance)
        # Convert non-serializable types to strings
        for key, value in data.items():
            if hasattr(value, "isoformat"):
                data[key] = value.isoformat()
            elif hasattr(value, "__str__") and not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                data[key] = str(value)
        return data
    except Exception:
        return {"id": str(instance.pk)}


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Log create/update actions to the audit trail."""
    table_name = getattr(sender._meta, "db_table", "")
    if table_name in EXCLUDED_TABLES or not table_name:
        return

    # Avoid circular import
    from audit.models import AuditLog

    try:
        AuditLog.objects.create(
            action="create" if created else "update",
            table_name=table_name,
            record_id=str(instance.pk),
            new_value=_model_to_dict(instance),
        )
    except Exception as e:
        logger.warning(f"Audit log failed for {table_name}: {e}")


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Log delete actions to the audit trail."""
    table_name = getattr(sender._meta, "db_table", "")
    if table_name in EXCLUDED_TABLES or not table_name:
        return

    from audit.models import AuditLog

    try:
        AuditLog.objects.create(
            action="delete",
            table_name=table_name,
            record_id=str(instance.pk),
            old_value=_model_to_dict(instance),
        )
    except Exception as e:
        logger.warning(f"Audit log (delete) failed for {table_name}: {e}")
