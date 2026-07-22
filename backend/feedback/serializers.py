"""Serializers for the Feedback app."""

from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    """Read/write serializer for feedback.

    On create, the submitter-derived fields (user, username, roles, user_agent)
    are set server-side in the view — the client only supplies category,
    severity, message, page_url, and an optional screenshot file.
    """

    screenshot_url = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = [
            "id",
            "user",
            "username",
            "roles",
            "category",
            "severity",
            "message",
            "page_url",
            "user_agent",
            "screenshot",
            "screenshot_url",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "user", "username", "roles", "user_agent",
            "screenshot_url", "created_at", "updated_at",
        ]
        extra_kwargs = {
            # The raw file field is write-only; reads use screenshot_url.
            "screenshot": {"write_only": True, "required": False},
            "message": {"required": True},
        }

    def get_screenshot_url(self, obj):
        if not obj.screenshot:
            return None
        # Served through the authenticated download action (works regardless of
        # whether /media/ is publicly served).
        request = self.context.get("request")
        path = f"/api/v1/feedback/items/{obj.id}/screenshot/"
        return request.build_absolute_uri(path) if request else path


class FeedbackReviewSerializer(serializers.ModelSerializer):
    """Restricted serializer for the review team to update triage fields only."""

    class Meta:
        model = Feedback
        fields = ["status", "admin_notes"]
