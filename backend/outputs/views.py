"""Outputs views — outputs schema ViewSets."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DatasetSnapshot, DataQualityReport
from .serializers import DatasetSnapshotSerializer, DataQualityReportSerializer

class DatasetSnapshotViewSet(viewsets.ModelViewSet):
    queryset = DatasetSnapshot.objects.select_related("study", "generated_by").all()
    serializer_class = DatasetSnapshotSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "snapshot_type"]

class DataQualityReportViewSet(viewsets.ModelViewSet):
    queryset = DataQualityReport.objects.select_related("study").all()
    serializer_class = DataQualityReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "report_type"]
