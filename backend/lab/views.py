"""Lab views — lab schema ViewSets."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LabResult, ReferenceRange, SampleCollection
from .serializers import LabResultSerializer, ReferenceRangeSerializer, SampleCollectionSerializer

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.select_related("subject", "subject_visit", "imported_by").all()
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["test_name"]
    filterset_fields = ["subject", "flag", "test_name"]

class ReferenceRangeViewSet(viewsets.ModelViewSet):
    queryset = ReferenceRange.objects.select_related("study").all()
    serializer_class = ReferenceRangeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "test_name", "gender"]

class SampleCollectionViewSet(viewsets.ModelViewSet):
    queryset = SampleCollection.objects.select_related("subject").all()
    serializer_class = SampleCollectionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["subject", "status", "sample_type"]
