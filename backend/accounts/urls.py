"""Accounts URL routes — auth schema (DRF Router)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "accounts"

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"roles", views.RoleViewSet)
router.register(r"user-roles", views.UserRoleViewSet)
router.register(r"site-staff", views.SiteStaffViewSet)
router.register(r"external-identities", views.ExternalSystemIdentityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
