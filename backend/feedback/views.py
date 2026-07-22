"""
Feedback views (UAT).

Any authenticated user can SUBMIT feedback. Only Study Admins / Admins can
LIST, review (update status/notes), download screenshots, or delete.

The whole surface is gated by settings.UAT_FEEDBACK_ENABLED so it can be
switched off the moment UAT finishes without removing code.
"""

import os

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsStudyAdmin

from .models import Feedback
from .serializers import FeedbackReviewSerializer, FeedbackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """Submit + review in-app UAT feedback."""

    queryset = Feedback.objects.select_related("user").all()
    serializer_class = FeedbackSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["category", "severity", "status"]
    search_fields = ["message", "username", "page_url"]
    ordering_fields = ["created_at", "severity", "status"]

    def _check_enabled(self):
        if not getattr(settings, "UAT_FEEDBACK_ENABLED", False):
            raise Http404("UAT feedback is disabled.")

    def initial(self, request, *args, **kwargs):
        self._check_enabled()
        return super().initial(request, *args, **kwargs)

    def get_permissions(self):
        # Anyone signed in can submit; only study admins can read/manage.
        if self.action == "create":
            return [IsAuthenticated()]
        return [IsStudyAdmin()]

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return FeedbackReviewSerializer
        return FeedbackSerializer

    def perform_create(self, serializer):
        user = self.request.user
        roles = []
        try:
            roles = list(user.user_roles.values_list("role__name", flat=True))
        except Exception:
            roles = []
        serializer.save(
            user=user if user and user.is_authenticated else None,
            username=getattr(user, "username", "") or "",
            roles=",".join(roles),
            user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:500],
        )

    @action(detail=True, methods=["get"], url_path="screenshot")
    def screenshot(self, request, pk=None):
        """Stream the screenshot file for a feedback item (review team only)."""
        obj = self.get_object()
        if not obj.screenshot:
            raise Http404("No screenshot for this feedback item.")
        path = obj.screenshot.path
        if not os.path.exists(path):
            raise Http404("Screenshot file missing.")
        return FileResponse(open(path, "rb"))
