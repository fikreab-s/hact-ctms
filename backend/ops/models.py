"""
Ops Models — ops schema (Operational & Site Management)
=========================================================
Tables: Contract, TrainingRecord, Milestone
"""

from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# Contract — Site contracts
# =============================================================================
class Contract(TimeStampedModel):
    """Contract between the sponsor/CRO and a participating site.

    Tracks contract lifecycle, budget, and links to Nextcloud for document storage.
    Supports ERPNext integration for financial tracking.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("terminated", "Terminated"),
    ]

    site = models.ForeignKey(
        "clinical.Site",
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    contract_number = models.CharField(max_length=100, unique=True, db_index=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    budget_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Contract budget in local currency.",
    )
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the contract document.",
    )

    # Integration: ERPNext
    erpnext_contract_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="ERPNext contract identifier for financial sync.",
    )

    class Meta:
        db_table = "ops_contracts"
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.contract_number} — {self.get_status_display()}"


# =============================================================================
# TrainingRecord — Site staff training records
# =============================================================================
class TrainingRecord(TimeStampedModel):
    """GCP and protocol training records for site staff.

    Tracks training completion and certificate storage in Nextcloud.
    Required for ICH-GCP compliance.
    """

    site = models.ForeignKey(
        "clinical.Site",
        on_delete=models.CASCADE,
        related_name="training_records",
    )
    staff_name = models.CharField(max_length=255)
    training_type = models.CharField(
        max_length=255,
        help_text="Type of training (e.g., GCP, Protocol, SOPs).",
    )
    training_date = models.DateField()
    certificate_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the training certificate.",
    )

    class Meta:
        db_table = "ops_training_records"
        verbose_name = "Training Record"
        verbose_name_plural = "Training Records"
        ordering = ["-training_date"]

    def __str__(self):
        return f"{self.staff_name} — {self.training_type} ({self.training_date})"


# =============================================================================
# Milestone — Study milestones (study-level or site-level)
# =============================================================================
class Milestone(TimeStampedModel):
    """Study or site-level milestone tracking.

    Milestones can be study-wide (site=NULL) or site-specific.
    """

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("delayed", "Delayed"),
    ]

    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    site = models.ForeignKey(
        "clinical.Site",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="milestones",
        help_text="NULL = study-level milestone; set = site-specific milestone.",
    )
    milestone_type = models.CharField(
        max_length=255,
        help_text="Type of milestone (e.g., First Patient In, Database Lock).",
    )
    planned_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        db_index=True,
    )

    class Meta:
        db_table = "ops_milestones"
        verbose_name = "Milestone"
        verbose_name_plural = "Milestones"
        ordering = ["planned_date"]

    def __str__(self):
        scope = f"Site {self.site.site_code}" if self.site else "Study-wide"
        return f"{self.milestone_type} ({scope}) — {self.get_status_display()}"
