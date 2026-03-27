"""
Safety Models — safety schema (Pharmacovigilance)
====================================================
Tables: AdverseEvent, CiomsForm, SafetyReview
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# AdverseEvent — Adverse event records
# =============================================================================
class AdverseEvent(TimeStampedModel):
    """Records adverse events experienced by subjects during the study.

    Supports ICH-GCP E6 safety reporting requirements including
    severity, seriousness criteria, causality, and outcome tracking.
    """

    SEVERITY_CHOICES = [
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
    ]

    CAUSALITY_CHOICES = [
        ("not_related", "Not Related"),
        ("unlikely", "Unlikely"),
        ("possible", "Possible"),
        ("probable", "Probable"),
        ("definite", "Definite"),
    ]

    OUTCOME_CHOICES = [
        ("recovered", "Recovered/Resolved"),
        ("recovering", "Recovering/Resolving"),
        ("not_recovered", "Not Recovered/Not Resolved"),
        ("recovered_with_sequelae", "Recovered/Resolved with Sequelae"),
        ("fatal", "Fatal"),
        ("unknown", "Unknown"),
    ]

    subject = models.ForeignKey(
        "clinical.Subject",
        on_delete=models.CASCADE,
        related_name="adverse_events",
    )
    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="adverse_events",
    )
    ae_term = models.CharField(max_length=500, help_text="Adverse event term/description.")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    serious = models.BooleanField(
        default=False,
        help_text="Is this a Serious Adverse Event (SAE)?",
    )
    serious_criteria = models.TextField(
        blank=True,
        default="",
        help_text="Criteria for seriousness (death, hospitalization, etc.).",
    )
    causality = models.CharField(
        max_length=30,
        choices=CAUSALITY_CHOICES,
        blank=True,
        default="",
    )
    outcome = models.CharField(
        max_length=30,
        choices=OUTCOME_CHOICES,
        blank=True,
        default="",
    )
    action_taken = models.TextField(
        blank=True,
        default="",
        help_text="Action taken regarding study treatment.",
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_adverse_events",
    )

    class Meta:
        db_table = "safety_adverse_events"
        verbose_name = "Adverse Event"
        verbose_name_plural = "Adverse Events"
        ordering = ["-reported_at"]

    def __str__(self):
        sae_flag = " [SAE]" if self.serious else ""
        return f"AE-{self.pk}: {self.ae_term[:50]}{sae_flag}"


# =============================================================================
# CiomsForm — CIOMS form tracking for serious AEs
# =============================================================================
class CiomsForm(TimeStampedModel):
    """CIOMS (Council for International Organizations of Medical Sciences) form.

    Generated for Serious Adverse Events requiring regulatory reporting.
    Actual document stored in Nextcloud; this tracks metadata and status.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
    ]

    adverse_event = models.ForeignKey(
        AdverseEvent,
        on_delete=models.CASCADE,
        related_name="cioms_forms",
    )
    form_version = models.CharField(max_length=20, default="1.0")
    generated_date = models.DateField(auto_now_add=True)
    submission_deadline = models.DateField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    regulatory_authority = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Target regulatory authority (e.g., EFDA, FDA).",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the CIOMS PDF document.",
    )

    class Meta:
        db_table = "safety_cioms_forms"
        verbose_name = "CIOMS Form"
        verbose_name_plural = "CIOMS Forms"
        ordering = ["-generated_date"]

    def __str__(self):
        return f"CIOMS-{self.pk} for AE-{self.adverse_event_id} ({self.get_status_display()})"


# =============================================================================
# SafetyReview — Safety committee reviews
# =============================================================================
class SafetyReview(TimeStampedModel):
    """Safety committee review records (DSUR, DMC, quarterly reviews).

    Documents stored in Nextcloud with URL reference here.
    """

    REVIEW_TYPE_CHOICES = [
        ("DSUR", "Development Safety Update Report"),
        ("DMC", "Data Monitoring Committee"),
        ("quarterly", "Quarterly Safety Report"),
    ]

    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="safety_reviews",
    )
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES)
    review_date = models.DateField()
    summary = models.TextField(blank=True, default="")
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the review document.",
    )

    class Meta:
        db_table = "safety_reviews"
        verbose_name = "Safety Review"
        verbose_name_plural = "Safety Reviews"
        ordering = ["-review_date"]

    def __str__(self):
        return f"{self.get_review_type_display()} — {self.review_date}"
