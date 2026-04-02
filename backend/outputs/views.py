"""
Outputs Views — Export & Quality Report endpoints
=====================================================
Provides:
- DatasetSnapshot CRUD + CSV/ODM export actions
- DataQualityReport CRUD + generate action
- File download endpoint
"""

import os

from django.http import FileResponse, Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from clinical.models import Study
from core.mixins import AuditCreateMixin
from core.permissions import IsReadOnlyOrDataManager

from .models import DataQualityReport, DatasetSnapshot
from .serializers import (
    DataQualityReportDetailSerializer,
    DataQualityReportListSerializer,
    DatasetSnapshotDetailSerializer,
    DatasetSnapshotListSerializer,
    ExportCSVSerializer,
    ExportODMSerializer,
    GenerateQualityReportSerializer,
)


# =============================================================================
# DatasetSnapshot ViewSet
# =============================================================================


class DatasetSnapshotViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Dataset snapshots with export actions.

    List: GET /api/v1/outputs/snapshots/
    Detail: GET /api/v1/outputs/snapshots/{id}/
    Export CSV: POST /api/v1/outputs/snapshots/export-csv/
    Export ODM: POST /api/v1/outputs/snapshots/export-odm/
    Download: GET /api/v1/outputs/snapshots/{id}/download/
    """

    queryset = DatasetSnapshot.objects.select_related("study", "generated_by").all()
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["study", "snapshot_type"]
    ordering_fields = ["snapshot_date", "created_at"]
    search_fields = ["description", "study__protocol_number"]

    def get_serializer_class(self):
        if self.action == "list":
            return DatasetSnapshotListSerializer
        if self.action in ("export_csv", "export_odm"):
            return None  # Handled by action serializers
        return DatasetSnapshotDetailSerializer

    @action(detail=False, methods=["post"], url_path="export-csv")
    def export_csv(self, request):
        """Generate a CSV ZIP export of all study data.

        POST /api/v1/outputs/snapshots/export-csv/
        Body: {"study": 5}
        """
        serializer = ExportCSVSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        study_id = serializer.validated_data["study"]
        try:
            study = Study.objects.get(pk=study_id)
        except Study.DoesNotExist:
            return Response(
                {"detail": f"Study {study_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from .services import export_study_zip

        file_path, snapshot = export_study_zip(study, user=request.user)

        return Response(
            {
                "detail": "CSV export generated successfully.",
                "snapshot_id": snapshot.id,
                "file_url": snapshot.file_url,
                "download_url": f"/api/v1/outputs/snapshots/{snapshot.id}/download/",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="export-odm")
    def export_odm(self, request):
        """Generate a CDISC ODM 1.3.2 XML export.

        POST /api/v1/outputs/snapshots/export-odm/
        Body: {"study": 5}
        """
        serializer = ExportODMSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        study_id = serializer.validated_data["study"]
        try:
            study = Study.objects.get(pk=study_id)
        except Study.DoesNotExist:
            return Response(
                {"detail": f"Study {study_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from .odm_export import export_study_odm

        file_path, snapshot = export_study_odm(study, user=request.user)

        return Response(
            {
                "detail": "CDISC ODM export generated successfully.",
                "snapshot_id": snapshot.id,
                "file_url": snapshot.file_url,
                "download_url": f"/api/v1/outputs/snapshots/{snapshot.id}/download/",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Download a generated export file.

        GET /api/v1/outputs/snapshots/{id}/download/
        """
        snapshot = self.get_object()

        if not snapshot.file_url:
            return Response(
                {"detail": "No file available for this snapshot."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Convert relative URL to filesystem path
        # file_url format: /media/exports/PROTOCOL/filename.zip
        from django.conf import settings

        relative_path = snapshot.file_url.replace("/media/", "", 1)
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        if not os.path.exists(file_path):
            return Response(
                {"detail": "Export file not found on disk."},
                status=status.HTTP_404_NOT_FOUND,
            )

        filename = os.path.basename(file_path)
        content_type = (
            "application/xml" if filename.endswith(".xml")
            else "application/zip" if filename.endswith(".zip")
            else "application/octet-stream"
        )

        return FileResponse(
            open(file_path, "rb"),
            content_type=content_type,
            as_attachment=True,
            filename=filename,
        )


# =============================================================================
# DataQualityReport ViewSet
# =============================================================================


class DataQualityReportViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Data quality reports with generation action.

    List: GET /api/v1/outputs/quality-reports/
    Detail: GET /api/v1/outputs/quality-reports/{id}/
    Generate: POST /api/v1/outputs/quality-reports/generate/
    """

    queryset = DataQualityReport.objects.select_related("study").all()
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["study", "report_type"]
    ordering_fields = ["generated_at", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return DataQualityReportListSerializer
        if self.action == "generate":
            return None
        return DataQualityReportDetailSerializer

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """Generate a data quality report for a study.

        POST /api/v1/outputs/quality-reports/generate/
        Body: {"study": 5, "report_type": "comprehensive"}
        """
        serializer = GenerateQualityReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        study_id = serializer.validated_data["study"]
        report_type = serializer.validated_data["report_type"]

        try:
            study = Study.objects.get(pk=study_id)
        except Study.DoesNotExist:
            return Response(
                {"detail": f"Study {study_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from .quality import generate_quality_report

        report_data = generate_quality_report(study, report_type=report_type)

        # Map report_type to model choices (comprehensive → query_status for storage)
        db_report_type = report_type if report_type in ("missing_data", "out_of_range", "query_status") else "query_status"

        report = DataQualityReport.objects.create(
            study=study,
            report_type=db_report_type,
            report_data=report_data,
        )

        return Response(
            {
                "detail": f"Quality report ({report_type}) generated successfully.",
                "report_id": report.id,
                "report_data": report_data,
            },
            status=status.HTTP_201_CREATED,
        )
