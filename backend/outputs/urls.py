"""Outputs URL routes — outputs schema (DRF Router)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "outputs"
router = DefaultRouter()
router.register(r"snapshots", views.DatasetSnapshotViewSet)
router.register(r"quality-reports", views.DataQualityReportViewSet)

urlpatterns = [path("", include(router.urls))]
