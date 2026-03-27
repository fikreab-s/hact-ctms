"""
Core — Shared Abstract Base Models
=====================================
TimeStampedModel provides audit columns for all domain models:
  - created_at, updated_at (auto timestamps)
  - created_by, updated_by (FK → User, nullable for system operations)

All HACT CTMS models inherit from TimeStampedModel to ensure
ICH-GCP and 21 CFR Part 11 auditability.
"""

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with audit tracking fields.

    Every domain model in the HACT CTMS inherits from this to ensure
    consistent audit columns across all tables.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
