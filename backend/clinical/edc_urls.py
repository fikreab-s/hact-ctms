"""EDC (Mobile) URL routes — /api/v1/edc/..."""

from django.urls import path

from . import edc_views

app_name = "edc"

urlpatterns = [
    # Subject list (GET)
    path("subjects/", edc_views.EdcSubjectListView.as_view(), name="subject-list"),
    # Subject detail (GET) — returns single subject with visits
    path("subjects/<int:pk>/", edc_views.EdcSubjectDetailView.as_view(), name="subject-detail"),

    # Enroll new subject (POST)
    path("enroll/", edc_views.EdcEnrollSubjectView.as_view(), name="enroll"),

    # Form definitions (GET)
    path("forms/", edc_views.EdcFormListView.as_view(), name="form-list"),
    path("forms/<int:pk>/schema/", edc_views.EdcFormSchemaView.as_view(), name="form-schema"),

    # Visit forms — what forms are available for a visit (GET)
    path(
        "subjects/<int:subject_id>/visits/<int:visit_id>/forms/",
        edc_views.EdcVisitFormsView.as_view(),
        name="visit-forms",
    ),

    # Existing form instance (GET — for edit pre-fill)
    path(
        "form-instances/<int:pk>/",
        edc_views.EdcFormInstanceView.as_view(),
        name="form-instance-detail",
    ),

    # Submit / Edit CRF (POST)
    path("submit/", edc_views.EdcSubmitCrfView.as_view(), name="submit"),

    # E-signature verification (POST)
    path("verify-signature/", edc_views.EdcVerifySignatureView.as_view(), name="verify-signature"),

    # Sync status (GET)
    path("sync-status/", edc_views.EdcSyncStatusView.as_view(), name="sync-status"),
]
