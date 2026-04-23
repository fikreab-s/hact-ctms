"""Integration URL routes — document upload, eTMF listing, status."""

from django.urls import path

from . import views

app_name = "integrations"

urlpatterns = [
    # Document Upload to Nextcloud eTMF
    path(
        "documents/upload/",
        views.upload_document,
        name="document-upload",
    ),
    # List eTMF documents for a study
    path(
        "etmf/<str:protocol_number>/",
        views.list_etmf,
        name="etmf-list",
    ),
    # List valid eTMF categories
    path(
        "etmf-categories/",
        views.list_etmf_categories,
        name="etmf-categories",
    ),
    # Integration health status
    path(
        "status/",
        views.integration_status,
        name="integration-status",
    ),
]
