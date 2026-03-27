"""Outputs Admin — outputs schema models registered in Django admin."""

from django.contrib import admin

from .models import DataQualityReport, DatasetSnapshot


@admin.register(DatasetSnapshot)
class DatasetSnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "study", "snapshot_type", "snapshot_date", "generated_by")
    list_filter = ("snapshot_type",)
    autocomplete_fields = ("study", "generated_by")


@admin.register(DataQualityReport)
class DataQualityReportAdmin(admin.ModelAdmin):
    list_display = ("id", "study", "report_type", "generated_at")
    list_filter = ("report_type",)
    autocomplete_fields = ("study",)
