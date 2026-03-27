"""
Accounts Models — auth schema
================================
Tables: User, Role, UserRole, SiteStaff, ExternalSystemIdentity

Custom User model extends Django's AbstractUser with Keycloak UUID mapping.
All models include audit columns via TimeStampedModel.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# User — Custom user model linked to Keycloak
# =============================================================================
class User(AbstractUser):
    """Custom user extending Django's AbstractUser.

    Adds keycloak_id for SSO mapping. All authentication flows
    resolve to this model via Keycloak OIDC or local auth.
    """

    keycloak_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Keycloak user UUID for OIDC SSO mapping.",
    )
    # Override email to make it required and unique
    email = models.EmailField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.email})"


# =============================================================================
# Role — Role definitions (data_manager, site_coordinator, etc.)
# =============================================================================
class Role(TimeStampedModel):
    """Role definitions for RBAC (Role-Based Access Control).

    Examples: data_manager, site_coordinator, monitor, principal_investigator,
    sponsor_admin, safety_officer, lab_manager, auditor.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        db_table = "auth_roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# UserRole — Many-to-many mapping of users to roles
# =============================================================================
class UserRole(TimeStampedModel):
    """Maps users to roles (many-to-many through table).

    A user can have multiple roles; a role can be assigned to many users.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users",
    )

    class Meta:
        db_table = "auth_user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user.username} → {self.role.name}"


# =============================================================================
# SiteStaff — Links users to sites with a role
# =============================================================================
class SiteStaff(TimeStampedModel):
    """Associates a user with a clinical site and their role at that site.

    A user can be staff at multiple sites; a site can have many staff.
    """

    site = models.ForeignKey(
        "clinical.Site",
        on_delete=models.CASCADE,
        related_name="staff_assignments",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="site_assignments",
    )
    role_at_site = models.CharField(
        max_length=100,
        help_text="Role at this specific site (e.g., Sub-Investigator, Study Nurse).",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "auth_site_staff"
        verbose_name = "Site Staff Assignment"
        verbose_name_plural = "Site Staff Assignments"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user.username} @ Site {self.site_id} ({self.role_at_site})"


# =============================================================================
# ExternalSystemIdentity — Maps local users to external system IDs
# =============================================================================
class ExternalSystemIdentity(TimeStampedModel):
    """Maps a local user to their identity in external systems.

    Supports OpenClinica, Nextcloud, SENAITE, ERPNext, and future integrations.
    """

    SYSTEM_CHOICES = [
        ("openclinica", "OpenClinica"),
        ("nextcloud", "Nextcloud"),
        ("senaite", "SENAITE LIMS"),
        ("erpnext", "ERPNext"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="external_identities",
    )
    system_name = models.CharField(max_length=50, choices=SYSTEM_CHOICES)
    external_user_id = models.CharField(max_length=255)
    external_username = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "auth_external_system_identities"
        verbose_name = "External System Identity"
        verbose_name_plural = "External System Identities"
        unique_together = [("user", "system_name")]

    def __str__(self):
        return f"{self.user.username} → {self.system_name}:{self.external_user_id}"
