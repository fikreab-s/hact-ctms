"""Accounts URL routes — auth schema (DRF Router + Auth endpoints)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from . import views_auth

app_name = "accounts"

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"roles", views.RoleViewSet)
router.register(r"user-roles", views.UserRoleViewSet)
router.register(r"site-staff", views.SiteStaffViewSet)
router.register(r"external-identities", views.ExternalSystemIdentityViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Auth endpoints
    path("auth/me/", views_auth.me, name="auth-me"),
    path("auth/status/", views_auth.auth_status, name="auth-status"),
]
