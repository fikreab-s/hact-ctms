"""
Outputs Models — outputs schema (Reporting & Data Exports)
============================================================
Tables: DatasetSnapshot, DataQualityReport
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# DatasetSnapshot — Exported dataset snapshots
# =============================================================================
class DatasetSnapshot(TimeStampedModel):
    """Immutable snapshot of an exported dataset.

    Supports SDTM, ADaM, and raw data exports with JSONB criteria
    for reproducing the export parameters. Documents stored in Nextcloud.
    """

    SNAPSHOT_TYPE_CHOICES = [
        ("SDTM", "SDTM (Study Data Tabulation Model)"),
        ("ADaM", "ADaM (Analysis Data Model)"),
        ("raw", "Raw Data Export"),
    ]

    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="dataset_snapshots",
    )
    snapshot_date = models.DateTimeField(auto_now_add=True)
    snapshot_type = models.CharField(max_length=10, choices=SNAPSHOT_TYPE_CHOICES)
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the exported dataset file.",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_snapshots",
    )
    description = models.TextField(blank=True, default="")
    criteria = models.JSONField(
        null=True,
        blank=True,
        help_text="JSONB — export parameters and filters used to generate this snapshot.",
    )

    class Meta:
        db_table = "outputs_dataset_snapshots"
        verbose_name = "Dataset Snapshot"
        verbose_name_plural = "Dataset Snapshots"
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"{self.get_snapshot_type_display()} — {self.snapshot_date.strftime('%Y-%m-%d')}"


# =============================================================================
# DataQualityReport — Data quality report logs
# =============================================================================
class DataQualityReport(TimeStampedModel):
    """Data quality report tracking missing data, out-of-range values,
    and query status summaries.

    Report data stored as JSONB for flexibility; full document in Nextcloud.
    """

    REPORT_TYPE_CHOICES = [
        ("missing_data", "Missing Data Report"),
        ("out_of_range", "Out-of-Range Values Report"),
        ("query_status", "Query Status Report"),
    ]

    study = models.ForeignKey(
        "clinical.Study",
        on_delete=models.CASCADE,
        related_name="data_quality_reports",
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField(
        null=True,
        blank=True,
        help_text="JSONB — structured report data (summaries, counts, details).",
    )
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="Nextcloud URL to the full report document.",
    )

    class Meta:
        db_table = "outputs_data_quality_reports"
        verbose_name = "Data Quality Report"
        verbose_name_plural = "Data Quality Reports"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} — {self.study.protocol_number}"
