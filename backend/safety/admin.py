"""Safety Admin — safety schema models registered in Django admin."""

from django.contrib import admin

from .models import AdverseEvent, CiomsForm, SafetyReview


@admin.register(AdverseEvent)
class AdverseEventAdmin(admin.ModelAdmin):
    list_display = ("id", "ae_term", "subject", "severity", "serious", "causality", "outcome", "reported_at")
    list_filter = ("severity", "serious", "causality", "outcome")
    search_fields = ("ae_term",)
    autocomplete_fields = ("subject", "study", "reported_by")


@admin.register(CiomsForm)
class CiomsFormAdmin(admin.ModelAdmin):
    list_display = ("id", "adverse_event", "status", "generated_date", "submission_deadline", "submitted_date")
    list_filter = ("status",)
    autocomplete_fields = ("adverse_event",)


@admin.register(SafetyReview)
class SafetyReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "study", "review_type", "review_date")
    list_filter = ("review_type",)
    autocomplete_fields = ("study",)
