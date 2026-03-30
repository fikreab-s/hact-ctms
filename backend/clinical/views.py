"""
Clinical Views — ViewSets with RBAC, Audit, Workflows & Custom Actions
=========================================================================
Full-featured ViewSets with:
- List vs Detail serializer switching
- Custom @action endpoints for study/subject/form/query workflows
- Advanced filtering with custom FilterSets
- Study-scoped data access
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import AuditCreateMixin, StudyScopedMixin
from core.permissions import (
    IsDataManager,
    IsMonitor,
    IsReadOnlyOrDataManager,
    IsReadOnlyOrStudyAdmin,
    IsSiteCoordinator,
)

from .filters import FormInstanceFilter, QueryFilter, SubjectFilter, SubjectVisitFilter
from .models import (
    Form, FormInstance, Item, ItemResponse, Query,
    Site, Study, Subject, SubjectVisit, Visit,
)
from .serializers import (
    FormDetailSerializer, FormInstanceDetailSerializer,
    FormInstanceListSerializer, FormInstanceSignSerializer,
    FormInstanceSubmitSerializer, FormListSerializer,
    ItemResponseSerializer, ItemSerializer,
    QueryAnswerSerializer, QueryCloseSerializer,
    QueryDetailSerializer, QueryListSerializer,
    SiteDetailSerializer, SiteListSerializer,
    StudyDetailSerializer, StudyListSerializer,
    StudyTransitionSerializer,
    SubjectDetailSerializer, SubjectEnrollSerializer,
    SubjectListSerializer, SubjectVisitDetailSerializer,
    SubjectVisitListSerializer, SubjectWithdrawSerializer,
    VisitSerializer,
)


# =============================================================================
# Study ViewSet
# =============================================================================

class StudyViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Study management with status workflow transitions."""

    queryset = Study.objects.all()
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["protocol_number", "name", "sponsor"]
    filterset_fields = ["status", "phase"]
    ordering_fields = ["created_at", "protocol_number", "start_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return StudyListSerializer
        return StudyDetailSerializer

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        """Transition study status: planning → active → locked → archived.

        POST /api/v1/clinical/studies/{id}/transition/
        Body: {"status": "active", "reason": "optional"}
        """
        study = self.get_object()
        serializer = StudyTransitionSerializer(
            data=request.data,
            context={"study": study, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        old_status = study.status
        study.status = serializer.validated_data["status"]
        study.save(update_fields=["status", "updated_at"])

        return Response({
            "detail": f"Study transitioned from '{old_status}' to '{study.status}'.",
            "study": StudyDetailSerializer(study).data,
        })


# =============================================================================
# Site ViewSet
# =============================================================================

class SiteViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    """Site management with study scoping."""

    queryset = Site.objects.select_related("study").all()
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["site_code", "name", "principal_investigator"]
    filterset_fields = ["study", "status", "country"]
    study_filter_field = "study"

    def get_serializer_class(self):
        if self.action == "list":
            return SiteListSerializer
        return SiteDetailSerializer


# =============================================================================
# Subject ViewSet
# =============================================================================

class SubjectViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    """Subject management with enrollment workflow actions."""

    queryset = Subject.objects.select_related("study", "site").all()
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["subject_identifier", "screening_number"]
    filterset_class = SubjectFilter
    ordering_fields = ["created_at", "subject_identifier", "enrollment_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return SubjectListSerializer
        return SubjectDetailSerializer

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        """Enroll a screened subject. Requires consent.

        POST /api/v1/clinical/subjects/{id}/enroll/
        Body: {"consent_signed_date": "2026-02-01", "enrollment_date": "2026-02-01"}
        """
        subject = self.get_object()

        if subject.status != "screened":
            return Response(
                {"detail": f"Cannot enroll: subject is '{subject.status}', not 'screened'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if subject.study.status != "active":
            return Response(
                {"detail": f"Cannot enroll: study is '{subject.study.status}', not 'active'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubjectEnrollSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject.status = "enrolled"
        subject.consent_signed_date = serializer.validated_data["consent_signed_date"]
        subject.enrollment_date = serializer.validated_data.get(
            "enrollment_date", serializer.validated_data["consent_signed_date"]
        )
        subject.save(update_fields=[
            "status", "consent_signed_date", "enrollment_date", "updated_at",
        ])

        return Response({
            "detail": f"Subject {subject.subject_identifier} enrolled successfully.",
            "subject": SubjectDetailSerializer(subject).data,
        })

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        """Withdraw/discontinue a subject.

        POST /api/v1/clinical/subjects/{id}/withdraw/
        Body: {"reason": "Patient withdrawal of consent", "completion_date": "2026-03-15"}
        """
        subject = self.get_object()

        if subject.status != "enrolled":
            return Response(
                {"detail": f"Cannot withdraw: subject is '{subject.status}', not 'enrolled'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubjectWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from datetime import date
        subject.status = "discontinued"
        subject.completion_date = serializer.validated_data.get(
            "completion_date", date.today()
        )
        subject.save(update_fields=["status", "completion_date", "updated_at"])

        return Response({
            "detail": f"Subject {subject.subject_identifier} withdrawn.",
            "reason": serializer.validated_data["reason"],
            "subject": SubjectDetailSerializer(subject).data,
        })

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a subject as completed.

        POST /api/v1/clinical/subjects/{id}/complete/
        """
        subject = self.get_object()

        if subject.status != "enrolled":
            return Response(
                {"detail": f"Cannot complete: subject is '{subject.status}', not 'enrolled'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from datetime import date
        subject.status = "completed"
        subject.completion_date = date.today()
        subject.save(update_fields=["status", "completion_date", "updated_at"])

        return Response({
            "detail": f"Subject {subject.subject_identifier} completed the study.",
            "subject": SubjectDetailSerializer(subject).data,
        })


# =============================================================================
# Visit ViewSet
# =============================================================================

class VisitViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Visit schedule definition management."""

    queryset = Visit.objects.select_related("study").all()
    serializer_class = VisitSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    filterset_fields = ["study", "is_screening", "is_baseline", "is_follow_up"]
    ordering_fields = ["visit_order"]


# =============================================================================
# SubjectVisit ViewSet
# =============================================================================

class SubjectVisitViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    """Subject visit tracking with window validation."""

    queryset = SubjectVisit.objects.select_related(
        "subject", "subject__site", "visit"
    ).all()
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_class = SubjectVisitFilter
    site_filter_field = "subject__site"
    ordering_fields = ["visit__visit_order", "actual_date", "scheduled_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return SubjectVisitListSerializer
        return SubjectVisitDetailSerializer


# =============================================================================
# Form ViewSet
# =============================================================================

class FormViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """CRF form definition management."""

    queryset = Form.objects.select_related("study").all()
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["name"]
    filterset_fields = ["study", "is_active"]

    def get_serializer_class(self):
        if self.action == "list":
            return FormListSerializer
        return FormDetailSerializer


# =============================================================================
# Item ViewSet
# =============================================================================

class ItemViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Form item (field) management."""

    queryset = Item.objects.select_related("form").all()
    serializer_class = ItemSerializer
    permission_classes = [IsReadOnlyOrDataManager]
    search_fields = ["field_name", "field_label"]
    filterset_fields = ["form", "field_type", "required"]


# =============================================================================
# FormInstance ViewSet
# =============================================================================

class FormInstanceViewSet(AuditCreateMixin, StudyScopedMixin, viewsets.ModelViewSet):
    """Form instance management with submit/sign workflow."""

    queryset = FormInstance.objects.select_related(
        "form", "subject", "subject__site", "subject_visit", "subject_visit__visit",
    ).all()
    permission_classes = [IsSiteCoordinator]
    filterset_class = FormInstanceFilter
    site_filter_field = "subject__site"

    def get_serializer_class(self):
        if self.action == "list":
            return FormInstanceListSerializer
        return FormInstanceDetailSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a draft form instance after validating completeness.

        POST /api/v1/clinical/form-instances/{id}/submit/
        """
        form_instance = self.get_object()
        serializer = FormInstanceSubmitSerializer(
            data=request.data,
            context={"form_instance": form_instance, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        form_instance.status = "submitted"
        form_instance.submitted_at = timezone.now()
        form_instance.save(update_fields=["status", "submitted_at", "updated_at"])

        return Response({
            "detail": f"Form '{form_instance.form.name}' submitted successfully.",
            "form_instance": FormInstanceDetailSerializer(form_instance).data,
        })

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        """Sign a submitted form instance (21 CFR Part 11 e-signature).

        POST /api/v1/clinical/form-instances/{id}/sign/
        Body: {"password": "user_password", "meaning": "I confirm this data is accurate."}
        """
        form_instance = self.get_object()

        if form_instance.status != "submitted":
            return Response(
                {"detail": f"Only submitted forms can be signed. Current: {form_instance.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FormInstanceSignSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        form_instance.status = "signed"
        form_instance.signed_by = request.user
        form_instance.signed_at = timezone.now()
        form_instance.save(update_fields=[
            "status", "signed_by", "signed_at", "updated_at",
        ])

        return Response({
            "detail": f"Form signed by {request.user.username}.",
            "meaning": serializer.validated_data["meaning"],
            "form_instance": FormInstanceDetailSerializer(form_instance).data,
        })

    @action(detail=True, methods=["post"], url_path="generate-queries")
    def generate_queries(self, request, pk=None):
        """Auto-generate queries for missing required fields.

        POST /api/v1/clinical/form-instances/{id}/generate-queries/
        """
        form_instance = self.get_object()
        required_items = form_instance.form.items.filter(required=True)

        created_queries = []
        for item in required_items:
            response = form_instance.responses.filter(item=item).first()
            if not response or not response.value:
                # Create a response placeholder if it doesn't exist
                if not response:
                    response = ItemResponse.objects.create(
                        form_instance=form_instance,
                        item=item,
                        value="",
                    )

                # Check if an open query already exists
                existing = Query.objects.filter(
                    item_response=response, status="open"
                ).exists()
                if not existing:
                    query = Query.objects.create(
                        item_response=response,
                        raised_by=request.user,
                        query_text=f"Missing required field: {item.field_label or item.field_name}",
                        status="open",
                    )
                    created_queries.append(query.id)

        return Response({
            "detail": f"{len(created_queries)} queries generated.",
            "query_ids": created_queries,
            "form_instance": FormInstanceDetailSerializer(form_instance).data,
        })


# =============================================================================
# ItemResponse ViewSet
# =============================================================================

class ItemResponseViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Item response (data entry) management with field-level validation."""

    queryset = ItemResponse.objects.select_related("form_instance", "item").all()
    serializer_class = ItemResponseSerializer
    permission_classes = [IsSiteCoordinator]
    filterset_fields = ["form_instance", "item"]

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# =============================================================================
# Query ViewSet
# =============================================================================

class QueryViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Data query management with answer/close workflow."""

    queryset = Query.objects.select_related(
        "item_response", "item_response__item",
        "item_response__form_instance", "item_response__form_instance__form",
        "item_response__form_instance__subject",
        "raised_by", "resolved_by",
    ).all()
    permission_classes = [IsReadOnlyOrDataManager]
    filterset_class = QueryFilter
    ordering_fields = ["raised_at", "status", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return QueryListSerializer
        return QueryDetailSerializer

    @action(detail=True, methods=["post"])
    def answer(self, request, pk=None):
        """Answer an open query (site coordinator responds).

        POST /api/v1/clinical/queries/{id}/answer/
        Body: {"response_text": "The value has been corrected."}
        """
        query = self.get_object()

        if query.status not in ("open",):
            return Response(
                {"detail": f"Cannot answer: query is '{query.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QueryAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query.status = "answered"
        query.response_text = serializer.validated_data["response_text"]
        query.save(update_fields=["status", "response_text", "updated_at"])

        return Response({
            "detail": "Query answered successfully.",
            "query": QueryDetailSerializer(query).data,
        })

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close a query (data manager closes after review).

        POST /api/v1/clinical/queries/{id}/close/
        """
        query = self.get_object()

        if query.status not in ("open", "answered"):
            return Response(
                {"detail": f"Cannot close: query is '{query.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query.status = "closed"
        query.resolved_by = request.user
        query.resolved_at = timezone.now()
        query.save(update_fields=[
            "status", "resolved_by", "resolved_at", "updated_at",
        ])

        return Response({
            "detail": "Query closed successfully.",
            "query": QueryDetailSerializer(query).data,
        })
