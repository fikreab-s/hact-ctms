"""
HACT CTMS — URL Configuration
===============================
Central URL routing for the HACT Clinical Trial Management System.

Routes:
    /api/v1/         → Versioned REST API endpoints
    /api/health/     → Health check endpoints
    /api/schema/     → OpenAPI schema (Swagger/ReDoc)
    /admin/          → Django admin interface
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny


def health_check(request):
    """Simple health check endpoint for Docker/NGINX health checks."""
    return JsonResponse(
        {
            "status": "healthy",
            "service": "hact-ctms-api",
            "version": "0.1.0",
        }
    )


urlpatterns = [
    # -------------------------------------------------------------------------
    # Django Admin
    # -------------------------------------------------------------------------
    path("admin/", admin.site.urls),
    # -------------------------------------------------------------------------
    # Health Check
    # -------------------------------------------------------------------------
    path("api/health/", health_check, name="health-check"),
    path("api/health/detailed/", include("health_check.urls")),
    # -------------------------------------------------------------------------
    # OpenAPI Schema & Documentation (public — no auth required)
    # -------------------------------------------------------------------------
    path(
        "api/schema/",
        SpectacularAPIView.as_view(permission_classes=[AllowAny]),
        name="schema",
    ),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(
            url_name="schema", permission_classes=[AllowAny]
        ),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema", permission_classes=[AllowAny]
        ),
        name="redoc",
    ),
    # -------------------------------------------------------------------------
    # API v1 — Application Endpoints
    # -------------------------------------------------------------------------
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/clinical/", include("clinical.urls")),
    path("api/v1/ops/", include("ops.urls")),
    path("api/v1/safety/", include("safety.urls")),
    path("api/v1/lab/", include("lab.urls")),
    path("api/v1/outputs/", include("outputs.urls")),
    path("api/v1/audit/", include("audit.urls")),
]

# Customize Django Admin
admin.site.site_header = "HACT CTMS Administration"
admin.site.site_title = "HACT CTMS Admin"
admin.site.index_title = "Clinical Trial Management System"
