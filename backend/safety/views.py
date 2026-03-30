"""Safety views — ViewSets with RBAC, enhanced serializers, and filtering."""

from rest_framework import viewsets

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
    """CIOMS form tracking for serious adverse events."""

    queryset = CiomsForm.objects.select_related(
        "adverse_event", "adverse_event__subject",
    ).all()
    serializer_class = CiomsFormSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["status", "adverse_event"]


class SafetyReviewViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Safety review records (DSUR, DMC, quarterly)."""

    queryset = SafetyReview.objects.select_related("study").all()
    serializer_class = SafetyReviewSerializer
    permission_classes = [IsSafetyOfficer]
    filterset_fields = ["study", "review_type"]
