"""Ops Admin — ops schema models registered in Django admin."""

from django.contrib import admin

from .models import Contract, Milestone, TrainingRecord


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "site", "status", "start_date", "end_date", "budget_amount")
    list_filter = ("status",)
    search_fields = ("contract_number",)
    autocomplete_fields = ("site",)


@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("staff_name", "site", "training_type", "training_date")
    list_filter = ("training_type",)
    search_fields = ("staff_name", "training_type")
    autocomplete_fields = ("site",)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("milestone_type", "study", "site", "status", "planned_date", "actual_date")
    list_filter = ("status",)
    search_fields = ("milestone_type",)
    autocomplete_fields = ("study", "site")
