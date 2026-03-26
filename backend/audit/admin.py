"""Audit Admin — audit_log registered read-only in Django admin."""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "table_name", "record_id", "user", "ip_address")
    list_filter = ("action", "table_name")
    search_fields = ("table_name", "record_id")
    readonly_fields = (
        "user", "action", "table_name", "record_id",
        "old_value", "new_value", "ip_address", "user_agent", "timestamp",
    )
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
