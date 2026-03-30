"""Lab views — ViewSets with RBAC, enhanced serializers, and filtering."""

from rest_framework import viewsets

from core.mixins import AuditCreateMixin
from core.permissions import IsLabManager

from .filters import LabResultFilter
from .models import LabResult, ReferenceRange, SampleCollection
from .serializers import (
    LabResultDetailSerializer, LabResultListSerializer,
    ReferenceRangeSerializer, SampleCollectionSerializer,
)


class LabResultViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Lab result management with enhanced filtering and auto-flagging."""

    queryset = LabResult.objects.select_related(
        "subject", "subject__site", "subject_visit",
        "subject_visit__visit", "imported_by",
    ).all()
    permission_classes = [IsLabManager]
    search_fields = ["test_name"]
    filterset_class = LabResultFilter
    ordering_fields = ["result_date", "test_name", "flag", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return LabResultListSerializer
        return LabResultDetailSerializer


class ReferenceRangeViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Reference range management."""

    queryset = ReferenceRange.objects.select_related("study").all()
    serializer_class = ReferenceRangeSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["study", "test_name", "gender"]


class SampleCollectionViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Sample collection tracking."""

    queryset = SampleCollection.objects.select_related("subject").all()
    serializer_class = SampleCollectionSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["subject", "status", "sample_type"]
