"""Accounts Admin — auth schema models registered in Django admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ExternalSystemIdentity, Role, SiteStaff, User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "keycloak_id")
    search_fields = ("username", "email", "first_name", "last_name", "keycloak_id")
    list_filter = ("is_active", "is_staff", "is_superuser")
    readonly_fields = ("keycloak_id", "created_at", "updated_at")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("HACT CTMS", {"fields": ("keycloak_id", "created_at", "updated_at")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")
    autocomplete_fields = ("user", "role")


@admin.register(SiteStaff)
class SiteStaffAdmin(admin.ModelAdmin):
    list_display = ("user", "site", "role_at_site", "start_date", "end_date")
    list_filter = ("role_at_site",)
    search_fields = ("user__username", "role_at_site")
    autocomplete_fields = ("user", "site")


@admin.register(ExternalSystemIdentity)
class ExternalSystemIdentityAdmin(admin.ModelAdmin):
    list_display = ("user", "system_name", "external_user_id", "external_username")
    list_filter = ("system_name",)
    search_fields = ("user__username", "external_user_id", "external_username")
    autocomplete_fields = ("user",)
