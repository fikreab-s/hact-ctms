"""Safety views — safety schema ViewSets with RBAC."""
from rest_framework import viewsets
from core.mixins import AuditCreateMixin
from core.permissions import IsSafetyOfficer, IsReadOnlyOrDataManager
from .models import AdverseEvent, CiomsForm, SafetyReview
from .serializers import AdverseEventSerializer, CiomsFormSerializer, SafetyReviewSerializer


class AdverseEventViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = AdverseEvent.objects.select_related("subject", "study", "reported_by").all()
    serializer_class = AdverseEventSerializer
    permission_classes = [IsSafetyOfficer]
    search_fields = ["ae_term"]
    filterset_fields = ["study", "subject", "severity", "serious", "causality", "outcome"]


class CiomsFormViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = CiomsForm.objects.select_related("adverse_event").all()
    serializer_class = CiomsFormSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["status", "adverse_event"]


class SafetyReviewViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = SafetyReview.objects.select_related("study").all()
    serializer_class = SafetyReviewSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["study", "review_type"]
