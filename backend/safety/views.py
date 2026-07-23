"""Safety views — ViewSets with RBAC, enhanced serializers, and filtering."""

import os

from django.conf import settings
from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import AuditCreateMixin
from core.permissions import IsMonitoringViewer, IsSafetyOfficer

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


# ── SAE Expedited Reporting Timeline ──

from rest_framework.views import APIView
from django.utils import timezone as tz


class SaeTimelineView(APIView):
    """GET /api/v1/safety/sae-timeline/

    Returns all SAEs that have reporting deadlines, with countdown data.
    Filterable by ?status=pending|overdue|on_time
    """

    # Read-only SAE timeline is surfaced on the monitoring dashboard too, so
    # allow the same viewer set (monitor, data_manager, safety_officer,
    # study_admin, admin) rather than every authenticated user.
    permission_classes = [IsMonitoringViewer]

    def get(self, request):
        qs = AdverseEvent.objects.filter(
            serious=True,
            reporting_deadline__isnull=False,
        ).select_related("subject", "subject__site", "study")

        # Optional filter
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(reporting_status=status_filter)

        data = []
        for sae in qs.order_by("reporting_deadline"):
            data.append({
                "id": sae.pk,
                "ae_term": sae.ae_term,
                "subject_identifier": sae.subject.subject_identifier if sae.subject else None,
                "site_code": sae.subject.site.site_code if sae.subject and sae.subject.site else None,
                "study_protocol": sae.study.protocol_number if sae.study else None,
                "severity": sae.severity,
                "serious_criteria": sae.serious_criteria,
                "reported_at": sae.reported_at,
                "reporting_deadline": sae.reporting_deadline,
                "reporting_status": sae.reporting_status,
                "reporting_status_display": sae.get_reporting_status_display(),
                "reported_to_authority_at": sae.reported_to_authority_at,
                "deadline_days_remaining": sae.deadline_days_remaining,
                "deadline_percent_elapsed": sae.deadline_percent_elapsed,
            })

        # Summary stats
        all_sae_qs = AdverseEvent.objects.filter(
            serious=True, reporting_deadline__isnull=False
        )
        summary = {
            "total": all_sae_qs.count(),
            "pending": all_sae_qs.filter(reporting_status="pending").count(),
            "overdue": all_sae_qs.filter(reporting_status="overdue").count(),
            "on_time": all_sae_qs.filter(reporting_status="on_time").count(),
        }

        return Response({"summary": summary, "results": data})


class MarkSaeReportedView(APIView):
    """POST /api/v1/safety/sae/<id>/mark-reported/

    Marks an SAE as reported to the regulatory authority.
    """

    permission_classes = [IsSafetyOfficer]

    def post(self, request, pk):
        try:
            sae = AdverseEvent.objects.get(pk=pk, serious=True)
        except AdverseEvent.DoesNotExist:
            return Response(
                {"detail": "SAE not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        now = tz.now()
        sae.reported_to_authority_at = now

        if sae.reporting_deadline and now <= sae.reporting_deadline:
            sae.reporting_status = "on_time"
        else:
            sae.reporting_status = "overdue"

        sae.save(update_fields=["reported_to_authority_at", "reporting_status"])

        return Response({
            "detail": f"SAE AE-{sae.pk} marked as reported.",
            "reporting_status": sae.reporting_status,
            "reported_to_authority_at": sae.reported_to_authority_at,
        })
