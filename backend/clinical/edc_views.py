"""
EDC (Mobile) API Views — endpoints for the standalone mobile CRF app.

All views require authentication (Bearer token from Keycloak).
Supports: subject listing, enrollment, CRF submit/edit, form-visit mapping,
e-signature verification, and audit trail.
"""

import logging

from django.db.models import Prefetch
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsSiteCoordinator

from .edc_serializers import (
    EdcCrfSubmissionSerializer,
    EdcEnrollSubjectSerializer,
    EdcFormInstanceDetailSerializer,
    EdcFormSchemaSerializer,
    EdcSubjectSerializer,
)
from .models import (
    Form, FormInstance, Item, ItemResponseAudit,
    Subject, SubjectVisit, Visit, VisitForm,
)

logger = logging.getLogger(__name__)


class EdcSubjectListView(generics.ListAPIView):
    """
    GET /api/v1/edc/subjects/

    Returns subjects for the CRC's site(s).
    Query params: study_id, site_id, search, status
    """

    serializer_class = EdcSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Subject.objects.select_related(
            "study", "site"
        ).prefetch_related(
            Prefetch(
                "subject_visits",
                queryset=SubjectVisit.objects.select_related("visit").prefetch_related(
                    "form_instances"
                ),
            )
        ).filter(study__status="active")

        study_id = self.request.query_params.get("study_id")
        if study_id:
            qs = qs.filter(study_id=study_id)

        site_id = self.request.query_params.get("site_id")
        if site_id:
            qs = qs.filter(site_id=site_id)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(subject_identifier__icontains=search)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by("-created_at")


class EdcSubjectDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/edc/subjects/<id>/

    Returns a single subject with all visits and nested form completion status.
    """

    serializer_class = EdcSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subject.objects.select_related(
            "study", "site"
        ).prefetch_related(
            Prefetch(
                "subject_visits",
                queryset=SubjectVisit.objects.select_related("visit").prefetch_related(
                    "form_instances"
                ).order_by("visit__visit_order"),
            )
        )


class EdcFormSchemaView(generics.RetrieveAPIView):
    """
    GET /api/v1/edc/forms/<id>/schema/

    Returns full form definition with all items (including skip logic,
    cross-field validation, display conditions).
    """

    serializer_class = EdcFormSchemaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Form.objects.prefetch_related(
            Prefetch("items", queryset=Item.objects.order_by("order"))
        ).filter(is_active=True)


class EdcFormListView(generics.ListAPIView):
    """
    GET /api/v1/edc/forms/

    Returns all active forms for a study.
    Query params: study_id
    """

    serializer_class = EdcFormSchemaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Form.objects.prefetch_related(
            Prefetch("items", queryset=Item.objects.order_by("order"))
        ).filter(is_active=True)

        study_id = self.request.query_params.get("study_id")
        if study_id:
            qs = qs.filter(study_id=study_id)

        return qs


class EdcEnrollSubjectView(generics.CreateAPIView):
    """POST /api/v1/edc/enroll/ — Enroll a new subject."""

    serializer_class = EdcEnrollSubjectSerializer
    # Write endpoint: only roles that may enter data (site_coordinator,
    # data_manager, study_admin, admin) — read-only roles like monitor/
    # auditor/lab_manager/ops_manager must not be able to enroll subjects.
    permission_classes = [IsSiteCoordinator]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = serializer.save()

        logger.info(
            f"[EDC] Subject {subject.subject_identifier} enrolled "
            f"by {request.user.username}"
        )

        output = EdcSubjectSerializer(subject).data
        return Response(output, status=status.HTTP_201_CREATED)


class EdcSubmitCrfView(APIView):
    """
    POST /api/v1/edc/submit/

    Submit or EDIT a CRF. Handles:
    - New submission (creates FormInstance + ItemResponses)
    - Edit existing (updates values + creates audit trail)
    - Draft save (no validation required)
    - E-signature verification (password re-entry)
    - Offline UUID deduplication
    """

    # Write endpoint: restrict CRF create/edit to data-entry roles
    # (site_coordinator, data_manager, study_admin, admin).
    permission_classes = [IsSiteCoordinator]

    def post(self, request):
        serializer = EdcCrfSubmissionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        form_instance = serializer.save()

        logger.info(
            f"[EDC] CRF '{form_instance.form.name}' "
            f"{'edited' if form_instance.updated_at != form_instance.created_at else 'submitted'} "
            f"for {form_instance.subject.subject_identifier} "
            f"by {request.user.username} (status: {form_instance.status})"
        )

        return Response(
            {
                "id": form_instance.id,
                "form": form_instance.form.name,
                "subject": form_instance.subject.subject_identifier,
                "status": form_instance.status,
                "submitted_at": form_instance.submitted_at,
                "signed_at": form_instance.signed_at,
                "message": "CRF saved successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class EdcVisitFormsView(APIView):
    """
    GET /api/v1/edc/subjects/<subject_id>/visits/<visit_id>/forms/

    Returns forms for a specific visit. Uses VisitForm mapping if available,
    otherwise falls back to all active forms.
    Includes existing form instance status (for edit indicators).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, subject_id, visit_id):
        try:
            subject_visit = SubjectVisit.objects.select_related(
                "subject", "visit__study"
            ).get(pk=visit_id, subject_id=subject_id)
        except SubjectVisit.DoesNotExist:
            return Response(
                {"error": "Visit not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        study = subject_visit.visit.study

        # Gap 6: Form-to-visit mapping
        visit_form_mappings = VisitForm.objects.filter(
            visit=subject_visit.visit
        ).values_list("form_id", flat=True)

        if visit_form_mappings:
            # Use mapped forms only
            forms = Form.objects.prefetch_related(
                Prefetch("items", queryset=Item.objects.order_by("order"))
            ).filter(id__in=visit_form_mappings, is_active=True)
        else:
            # Fallback: all active forms for the study
            forms = Form.objects.prefetch_related(
                Prefetch("items", queryset=Item.objects.order_by("order"))
            ).filter(study=study, is_active=True)

        # Get existing form instances for this visit
        existing_instances = FormInstance.objects.filter(
            subject_id=subject_id,
            subject_visit=subject_visit,
        ).values_list("form_id", "status", "id")

        existing_map = {}
        for form_id, inst_status, inst_id in existing_instances:
            existing_map[form_id] = {"status": inst_status, "instance_id": inst_id}

        forms_data = []
        for form in forms:
            form_data = EdcFormSchemaSerializer(form).data
            existing = existing_map.get(form.id)
            form_data["instance_status"] = existing["status"] if existing else None
            form_data["instance_id"] = existing["instance_id"] if existing else None
            forms_data.append(form_data)

        return Response({
            "subject_visit_id": subject_visit.id,
            "visit_name": subject_visit.visit.visit_name,
            "visit_status": subject_visit.status,
            "subject_identifier": subject_visit.subject.subject_identifier,
            "forms": forms_data,
        })


class EdcFormInstanceView(APIView):
    """
    GET /api/v1/edc/form-instances/<id>/

    Returns an existing form instance with all responses — for pre-filling
    the edit form.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            instance = FormInstance.objects.select_related(
                "form", "subject"
            ).prefetch_related(
                "responses__item"
            ).get(pk=pk)
        except FormInstance.DoesNotExist:
            return Response(
                {"error": "Form instance not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = EdcFormInstanceDetailSerializer(instance).data
        return Response(data)


class EdcVerifySignatureView(APIView):
    """
    POST /api/v1/edc/verify-signature/

    21 CFR Part 11 e-signature verification.

    The frontend re-authenticates the user via Keycloak ROPC grant
    and sends the resulting fresh access token as proof.
    This endpoint validates that the token is a valid Keycloak JWT
    belonging to the authenticated user.

    Body: {"signature_token": "..."}
    Returns: {"valid": true/false}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        signature_token = request.data.get("signature_token", "")
        # Backward compat: also accept "password" for direct check
        password = request.data.get("password", "")

        if signature_token:
            # Validate the fresh Keycloak token
            try:
                from core.auth_backend import KeycloakJWTAuthentication
                auth = KeycloakJWTAuthentication()
                validated_user, decoded = auth._authenticate_token(signature_token)

                if validated_user and validated_user.pk == request.user.pk:
                    logger.info(
                        f"[EDC] E-signature verified for '{request.user.username}' "
                        f"via fresh Keycloak token"
                    )
                    return Response({"valid": True})
                else:
                    logger.warning(
                        f"[EDC] E-signature token user mismatch: "
                        f"expected={request.user.username}, "
                        f"got={validated_user.username if validated_user else 'None'}"
                    )
                    return Response({"valid": False})
            except Exception as e:
                logger.warning(f"[EDC] E-signature token validation failed: {e}")
                return Response({"valid": False})

        elif password:
            # Fallback: Django password check
            is_valid = request.user.check_password(password)
            return Response({"valid": is_valid})

        return Response(
            {"valid": False, "error": "signature_token or password is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EdcSyncStatusView(APIView):
    """
    GET /api/v1/edc/sync-status/

    Returns recent EDC submissions by the current user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        recent = FormInstance.objects.filter(
            responses__updated_by=request.user
        ).select_related(
            "form", "subject"
        ).distinct().order_by("-created_at")[:20]

        submissions = []
        for inst in recent:
            submissions.append({
                "id": inst.id,
                "form_name": inst.form.name,
                "subject_identifier": inst.subject.subject_identifier,
                "status": inst.status,
                "submitted_at": inst.submitted_at,
                "created_at": inst.created_at,
            })

        return Response({
            "total_recent": len(submissions),
            "submissions": submissions,
        })
