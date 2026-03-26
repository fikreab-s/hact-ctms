"""Clinical Admin — clinical schema models registered in Django admin."""

from django.contrib import admin

from .models import (
    Form,
    FormInstance,
    Item,
    ItemResponse,
    Query,
    Site,
    Study,
    Subject,
    SubjectVisit,
    Visit,
)


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ("protocol_number", "name", "phase", "status", "start_date", "end_date")
    list_filter = ("status", "phase")
    search_fields = ("protocol_number", "name", "sponsor")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("site_code", "name", "study", "country", "status", "activation_date")
    list_filter = ("status", "country")
    search_fields = ("site_code", "name", "principal_investigator")
    autocomplete_fields = ("study",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_identifier", "study", "site", "status", "enrollment_date")
    list_filter = ("status",)
    search_fields = ("subject_identifier", "screening_number")
    autocomplete_fields = ("study", "site")


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("visit_name", "study", "visit_order", "planned_day", "is_screening", "is_baseline")
    list_filter = ("is_screening", "is_baseline", "is_follow_up")
    search_fields = ("visit_name",)
    autocomplete_fields = ("study",)


@admin.register(SubjectVisit)
class SubjectVisitAdmin(admin.ModelAdmin):
    list_display = ("subject", "visit", "scheduled_date", "actual_date", "status")
    list_filter = ("status",)
    search_fields = ("subject__subject_identifier", "visit__visit_name")
    autocomplete_fields = ("subject", "visit")


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("name", "study", "version", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    autocomplete_fields = ("study",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("field_name", "form", "field_type", "required", "order")
    list_filter = ("field_type", "required")
    search_fields = ("field_name", "field_label")
    autocomplete_fields = ("form",)


@admin.register(FormInstance)
class FormInstanceAdmin(admin.ModelAdmin):
    list_display = ("form", "subject", "instance_number", "status", "submitted_at", "signed_at")
    list_filter = ("status",)
    search_fields = ("subject__subject_identifier", "form__name")
    autocomplete_fields = ("form", "subject", "subject_visit", "signed_by")


@admin.register(ItemResponse)
class ItemResponseAdmin(admin.ModelAdmin):
    list_display = ("form_instance", "item", "value", "updated_at")
    search_fields = ("item__field_name", "value")
    raw_id_fields = ("form_instance", "item", "updated_by")


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ("id", "item_response", "raised_by", "status", "raised_at", "resolved_at")
    list_filter = ("status",)
    search_fields = ("query_text", "response_text")
    autocomplete_fields = ("item_response", "raised_by", "resolved_by")
