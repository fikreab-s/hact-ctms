"""Clinical views — clinical schema ViewSets with RBAC and audit."""

from rest_framework import viewsets

from core.mixins import AuditCreateMixin, StudyScopedMixin
from core.permissions import (
    IsDataManager,
    IsMonitor,
    IsReadOnlyOrDataManager,
    IsReadOnlyOrStudyAdmin,
    IsSiteCoordinator,
)

from .models import (
    Form, FormInstance, Item, ItemResponse, Query,
    Site, Study, Subject, SubjectVisit, Visit,
)
from .serializers import (
    FormInstanceSerializer, FormSerializer, ItemResponseSerializer,
    ItemSerializer, QuerySerializer, SiteSerializer, StudySerializer,
    SubjectSerializer, SubjectVisitSerializer, VisitSerializer,
)


class StudyViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["protocol_number", "name", "sponsor"]
    filterset_fields = ["status", "phase"]
    ordering_fields = ["created_at", "protocol_number", "start_date"]


class SiteViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    queryset = Site.objects.select_related("study").all()
    serializer_class = SiteSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["site_code", "name", "principal_investigator"]
    filterset_fields = ["study", "status", "country"]
    study_filter_field = "study"


class SubjectViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    queryset = Subject.objects.select_related("study", "site").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["subject_identifier", "screening_number"]
    filterset_fields = ["study", "site", "status"]


class VisitViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Visit.objects.select_related("study").all()
    serializer_class = VisitSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    filterset_fields = ["study", "is_screening", "is_baseline", "is_follow_up"]
    ordering_fields = ["visit_order"]


class SubjectVisitViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    queryset = SubjectVisit.objects.select_related("subject", "visit").all()
    serializer_class = SubjectVisitSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["subject", "visit", "status"]
    site_filter_field = "subject__site"


class FormViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Form.objects.select_related("study").all()
    serializer_class = FormSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["name"]
    filterset_fields = ["study", "is_active"]


class ItemViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Item.objects.select_related("form").all()
    serializer_class = ItemSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["field_name", "field_label"]
    filterset_fields = ["form", "field_type", "required"]


class FormInstanceViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    queryset = FormInstance.objects.select_related("form", "subject", "subject_visit").all()
    serializer_class = FormInstanceSerializer
    permission_classes = [IsSiteCoordinator]
    filterset_fields = ["form", "subject", "status"]
    site_filter_field = "subject__site"


class ItemResponseViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = ItemResponse.objects.select_related("form_instance", "item").all()
    serializer_class = ItemResponseSerializer
    permission_classes = [IsSiteCoordinator]
    filterset_fields = ["form_instance", "item"]


class QueryViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Query.objects.select_related("item_response", "raised_by", "resolved_by").all()
    serializer_class = QuerySerializer
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_fields = ["status", "raised_by", "resolved_by"]
