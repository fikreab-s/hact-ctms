"""Audit URL routes — audit schema (DRF Router, read-only)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "audit"
router = DefaultRouter()
router.register(r"logs", views.AuditLogViewSet)

urlpatterns = [path("", include(router.urls))]
