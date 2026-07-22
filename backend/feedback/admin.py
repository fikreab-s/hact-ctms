"""Django admin for reviewing UAT feedback."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id", "created_at", "category", "severity", "status",
        "username", "short_message", "has_screenshot",
    )
    list_filter = ("category", "severity", "status", "created_at")
    search_fields = ("message", "username", "page_url", "roles")
    list_editable = ("status",)
    readonly_fields = (
        "user", "username", "roles", "category", "severity", "message",
        "page_url", "user_agent", "created_at", "updated_at", "screenshot_preview",
    )
    fields = (
        "created_at", "status", "admin_notes",
        "category", "severity", "message",
        "username", "roles", "user", "page_url", "user_agent",
        "screenshot", "screenshot_preview",
    )
    ordering = ("-created_at",)

    @admin.display(description="Message")
    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else obj.message

    @admin.display(boolean=True, description="Shot")
    def has_screenshot(self, obj):
        return bool(obj.screenshot)

    @admin.display(description="Screenshot preview")
    def screenshot_preview(self, obj):
        if not obj.screenshot:
            return "—"
        return format_html(
            '<a href="/api/v1/feedback/items/{}/screenshot/" target="_blank">'
            '<img src="/api/v1/feedback/items/{}/screenshot/" '
            'style="max-width:600px;border:1px solid #ccc;border-radius:6px;" /></a>',
            obj.id, obj.id,
        )
