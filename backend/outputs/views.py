"""Outputs views — outputs schema ViewSets with RBAC."""
from rest_framework import viewsets
from core.mixins import AuditCreateMixin
from core.permissions import IsReadOnlyOrDataManager
from .models import DatasetSnapshot, DataQualityReport
from .serializers import DatasetSnapshotSerializer, DataQualityReportSerializer


class DatasetSnapshotViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = DatasetSnapshot.objects.select_related("study", "generated_by").all()
    serializer_class = DatasetSnapshotSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["study", "snapshot_type"]


class DataQualityReportViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = DataQualityReport.objects.select_related("study").all()
    serializer_class = DataQualityReportSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["study", "report_type"]
