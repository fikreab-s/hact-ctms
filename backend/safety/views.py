"""Safety views — safety schema ViewSets."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AdverseEvent, CiomsForm, SafetyReview
from .serializers import AdverseEventSerializer, CiomsFormSerializer, SafetyReviewSerializer

class AdverseEventViewSet(viewsets.ModelViewSet):
    queryset = AdverseEvent.objects.select_related("subject", "study", "reported_by").all()
    serializer_class = AdverseEventSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["ae_term"]
    filterset_fields = ["study", "subject", "severity", "serious", "causality", "outcome"]

class CiomsFormViewSet(viewsets.ModelViewSet):
    queryset = CiomsForm.objects.select_related("adverse_event").all()
    serializer_class = CiomsFormSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "adverse_event"]

class SafetyReviewViewSet(viewsets.ModelViewSet):
    queryset = SafetyReview.objects.select_related("study").all()
    serializer_class = SafetyReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "review_type"]
