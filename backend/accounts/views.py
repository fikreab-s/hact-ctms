"""Accounts views — auth schema ViewSets with RBAC."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.mixins import AuditCreateMixin
from core.permissions import IsStudyAdmin, IsReadOnlyOrStudyAdmin

from .models import ExternalSystemIdentity, Role, SiteStaff, User, UserRole
from .serializers import (
    ExternalSystemIdentitySerializer,
    RoleSerializer,
    SiteStaffSerializer,
    UserRoleSerializer,
    UserSerializer,
)


class UserViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["username", "email", "first_name", "last_name"]
    filterset_fields = ["is_active"]
    ordering_fields = ["username", "email", "created_at"]


class RoleViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    search_fields = ["name"]


class UserRoleViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = UserRole.objects.select_related("user", "role").all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsStudyAdmin]
    filterset_fields = ["user", "role"]


class SiteStaffViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = SiteStaff.objects.select_related("user", "site").all()
    serializer_class = SiteStaffSerializer
    permission_classes = [IsReadOnlyOrStudyAdmin]
    filterset_fields = ["site", "user", "role_at_site"]


class ExternalSystemIdentityViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = ExternalSystemIdentity.objects.select_related("user").all()
    serializer_class = ExternalSystemIdentitySerializer
    permission_classes = [IsStudyAdmin]
    filterset_fields = ["user", "system_name"]
