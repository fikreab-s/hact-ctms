"""Accounts serializers — auth schema."""

from rest_framework import serializers

from .models import ExternalSystemIdentity, Role, SiteStaff, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_active", "keycloak_id", "created_at", "updated_at")
        read_only_fields = ("id", "keycloak_id", "created_at", "updated_at")


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class SiteStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStaff
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ExternalSystemIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalSystemIdentity
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
