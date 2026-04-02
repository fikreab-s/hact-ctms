"""Safety views — ViewSets with RBAC, enhanced serializers, and filtering."""

import os

from django.conf import settings
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import AuditCreateMixin
from core.permissions import IsSafetyOfficer

from .filters import AdverseEventFilter
from .models import AdverseEvent, CiomsForm, SafetyReview
from .serializers import (
    AdverseEventDetailSerializer, AdverseEventListSerializer,
    CiomsFormSerializer, SafetyReviewSerializer,
)


class AdverseEventViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Adverse event management with enhanced filtering."""

    queryset = AdverseEvent.objects.select_related(
        "subject", "subject__site", "study", "reported_by",
    ).all()
    permission_classes = [IsSafetyOfficer]
    search_fields = ["ae_term"]
    filterset_class = AdverseEventFilter
    ordering_fields = ["start_date", "severity", "reported_at", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AdverseEventListSerializer
        return AdverseEventDetailSerializer


class CiomsFormViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """CIOMS form tracking for serious adverse events.

    Custom actions:
    - POST /cioms-forms/{id}/generate-pdf/ — Generate CIOMS I PDF
    - GET  /cioms-forms/{id}/download/ — Download generated PDF
    """

    queryset = CiomsForm.objects.select_related(
        "adverse_event", "adverse_event__subject",
    ).all()
    serializer_class = CiomsFormSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["status", "adverse_event"]

    @action(detail=True, methods=["post"], url_path="generate-pdf")
    def generate_pdf(self, request, pk=None):
        """Generate a CIOMS I PDF for this form.

        POST /api/v1/safety/cioms-forms/{id}/generate-pdf/
        """
        cioms_form = self.get_object()

        if not cioms_form.adverse_event.serious:
            return Response(
                {"detail": "CIOMS forms are only for Serious Adverse Events (SAEs)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .cioms_pdf import generate_cioms_pdf

        file_path = generate_cioms_pdf(cioms_form)

        cioms_form.refresh_from_db()

        return Response({
            "detail": "CIOMS I PDF generated successfully.",
            "cioms_form_id": cioms_form.id,
            "file_url": cioms_form.file_url,
            "download_url": f"/api/v1/safety/cioms-forms/{cioms_form.id}/download/",
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Download the generated CIOMS PDF.

        GET /api/v1/safety/cioms-forms/{id}/download/
        """
        cioms_form = self.get_object()

        if not cioms_form.file_url:
            return Response(
                {"detail": "No PDF has been generated for this CIOMS form yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        relative_path = cioms_form.file_url.replace("/media/", "", 1)
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(file_path):
            return Response(
                {"detail": "PDF file not found on disk."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            open(file_path, "rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=os.path.basename(file_path),
        )


class SafetyReviewViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Safety review records (DSUR, DMC, quarterly)."""

    queryset = SafetyReview.objects.select_related("study").all()
    serializer_class = SafetyReviewSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["study", "review_type"]

