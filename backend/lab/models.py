"""
Lab Models — lab schema (Laboratory & Biomarker Data)
=======================================================
Tables: LabResult, ReferenceRange, SampleCollection
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# LabResult — Laboratory test results
# =============================================================================
class LabResult(TimeStampedModel):
    """Individual laboratory test result for a subject.

    Results are imported from SENAITE LIMS or entered manually.
    Includes H/L/N flagging based on reference ranges.
    """

    FLAG_CHOICES = [
        ("H", "High"),
        ("L", "Low"),
        ("N", "Normal"),
    ]

    subject = models.ForeignKey(
        "clinical.Subject",
        on_delete=models.CASCADE,
        related_name="lab_results",
    )
    subject_visit = models.ForeignKey(
        "clinical.SubjectVisit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lab_results",
    )
    test_name = models.CharField(max_length=255, db_index=True)
    result_value = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True, default="")
    reference_range_low = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    reference_range_high = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    flag = models.CharField(
        max_length=1,
        choices=FLAG_CHOICES,
        blank=True,
        default="",
        help_text="H=High, L=Low, N=Normal relative to reference range.",
    )
    result_date = models.DateField()
    imported_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_lab_results",
    )

    class Meta:
        db_table = "lab_results"
        verbose_name = "Lab Result"
        verbose_name_plural = "Lab Results"
        ordering = ["-result_date"]

    def __str__(self):
        return f"{self.test_name}: {self.result_value} {self.unit}"


# =============================================================================
# ReferenceRange — Reference ranges per study/test/demographics
# =============================================================================
class ReferenceRange(TimeStampedModel):
    """Reference ranges for lab tests, stratified by study, gender, and age.

    Used to automatically flag lab results as H/L/N.
    """

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("all", "All"),
    ]

    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="reference_ranges",
    )
    test_name = models.CharField(max_length=255, db_index=True)
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default="all")
    age_lower = models.PositiveIntegerField(
        null=True, blank=True, help_text="Minimum age (inclusive)."
    )
    age_upper = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum age (inclusive)."
    )
    range_low = models.DecimalField(max_digits=10, decimal_places=4)
    range_high = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        db_table = "lab_reference_ranges"
        verbose_name = "Reference Range"
        verbose_name_plural = "Reference Ranges"
        ordering = ["test_name"]

    def __str__(self):
        return f"{self.test_name} ({self.gender}): {self.range_low}–{self.range_high}"


# =============================================================================
# SampleCollection — Sample tracking (SENAITE integration)
# =============================================================================
class SampleCollection(TimeStampedModel):
    """Biological sample collection tracking.

    Integrates with SENAITE LIMS via senaite_sample_id for
    end-to-end sample lifecycle management.
    """

    STATUS_CHOICES = [
        ("collected", "Collected"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    subject = models.ForeignKey(
        "clinical.Subject",
        on_delete=models.CASCADE,
        related_name="sample_collections",
    )
    senaite_sample_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="SENAITE LIMS sample identifier.",
        db_index=True,
    )
    collection_date = models.DateField()
    sample_type = models.CharField(
        max_length=100,
        help_text="Type of sample (e.g., Blood, Urine, Tissue).",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="collected",
        db_index=True,
    )

    class Meta:
        db_table = "lab_sample_collections"
        verbose_name = "Sample Collection"
        verbose_name_plural = "Sample Collections"
        ordering = ["-collection_date"]

    def __str__(self):
        return f"{self.sample_type} — {self.subject_id} ({self.collection_date})"
