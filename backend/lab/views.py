"""Lab views — lab schema ViewSets with RBAC."""
from rest_framework import viewsets
from core.mixins import AuditCreateMixin
from core.permissions import IsLabManager
from .models import LabResult, ReferenceRange, SampleCollection
from .serializers import LabResultSerializer, ReferenceRangeSerializer, SampleCollectionSerializer


class LabResultViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = LabResult.objects.select_related("subject", "subject_visit", "imported_by").all()
    serializer_class = LabResultSerializer
    permission_classes = [IsLabManager]
    search_fields = ["test_name"]
    filterset_fields = ["subject", "flag", "test_name"]


class ReferenceRangeViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = ReferenceRange.objects.select_related("study").all()
    serializer_class = ReferenceRangeSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["study", "test_name", "gender"]


class SampleCollectionViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = SampleCollection.objects.select_related("subject").all()
    serializer_class = SampleCollectionSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["subject", "status", "sample_type"]
