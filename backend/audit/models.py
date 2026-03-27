"""
Audit Models — audit schema (Append-Only Audit Trail)
=======================================================
Table: AuditLog

21 CFR Part 11 compliant — captures who changed what, when, and from where.
Append-only: records are never updated or deleted.
"""

from django.conf import settings
from django.db import models


# =============================================================================
# AuditLog — Central audit trail for all data changes
# =============================================================================
class AuditLog(models.Model):
    """Immutable audit log entry capturing all data changes system-wide.

    Populated automatically via Django signals (see audit/signals.py).
    Append-only — no update or delete operations allowed.

    Complies with 21 CFR Part 11 requirements for electronic records:
    - Who (user_id, ip_address, user_agent)
    - What (table_name, record_id, action, old/new values)
    - When (timestamp)
    """

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("export", "Export"),
        ("lock", "Lock"),
        ("sign", "Sign"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    table_name = models.CharField(max_length=100, db_index=True)
    record_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Primary key of the affected record.",
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="JSONB — previous state of the record (for updates/deletes).",
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="JSONB — new state of the record (for creates/updates).",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_log"
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
        ordering = ["-timestamp"]
        # Prevent Django admin from allowing edits
        default_permissions = ("add", "view")

    def __str__(self):
        return f"[{self.timestamp}] {self.action} on {self.table_name}#{self.record_id}"
