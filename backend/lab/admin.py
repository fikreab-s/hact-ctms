"""Lab Admin — lab schema models registered in Django admin."""

from django.contrib import admin

from .models import LabResult, ReferenceRange, SampleCollection


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "test_name", "result_value", "unit", "flag", "result_date")
    list_filter = ("flag", "test_name")
    search_fields = ("test_name",)
    raw_id_fields = ("subject", "subject_visit", "imported_by")


@admin.register(ReferenceRange)
class ReferenceRangeAdmin(admin.ModelAdmin):
    list_display = ("test_name", "study", "gender", "range_low", "range_high")
    list_filter = ("gender",)
    search_fields = ("test_name",)
    autocomplete_fields = ("study",)


@admin.register(SampleCollection)
class SampleCollectionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "sample_type", "collection_date", "status", "senaite_sample_id")
    list_filter = ("status", "sample_type")
    search_fields = ("senaite_sample_id",)
    autocomplete_fields = ("subject",)
