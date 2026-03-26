"""Clinical views — clinical schema ViewSets."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    Form, FormInstance, Item, ItemResponse, Query,
    Site, Study, Subject, SubjectVisit, Visit,
)
from .serializers import (
    FormInstanceSerializer, FormSerializer, ItemResponseSerializer,
    ItemSerializer, QuerySerializer, SiteSerializer, StudySerializer,
    SubjectSerializer, SubjectVisitSerializer, VisitSerializer,
)


class StudyViewSet(viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["protocol_number", "name", "sponsor"]
    filterset_fields = ["status", "phase"]
    ordering_fields = ["created_at", "protocol_number", "start_date"]


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.select_related("study").all()
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["site_code", "name", "principal_investigator"]
    filterset_fields = ["study", "status", "country"]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related("study", "site").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["subject_identifier", "screening_number"]
    filterset_fields = ["study", "site", "status"]


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.select_related("study").all()
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "is_screening", "is_baseline", "is_follow_up"]
    ordering_fields = ["visit_order"]


class SubjectVisitViewSet(viewsets.ModelViewSet):
    queryset = SubjectVisit.objects.select_related("subject", "visit").all()
    serializer_class = SubjectVisitSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["subject", "visit", "status"]


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.select_related("study").all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    filterset_fields = ["study", "is_active"]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related("form").all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["field_name", "field_label"]
    filterset_fields = ["form", "field_type", "required"]


class FormInstanceViewSet(viewsets.ModelViewSet):
    queryset = FormInstance.objects.select_related("form", "subject", "subject_visit").all()
    serializer_class = FormInstanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["form", "subject", "status"]


class ItemResponseViewSet(viewsets.ModelViewSet):
    queryset = ItemResponse.objects.select_related("form_instance", "item").all()
    serializer_class = ItemResponseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["form_instance", "item"]


class QueryViewSet(viewsets.ModelViewSet):
    queryset = Query.objects.select_related("item_response", "raised_by", "resolved_by").all()
    serializer_class = QuerySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "raised_by", "resolved_by"]
