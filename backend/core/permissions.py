"""
Core — RBAC Permission Classes
=================================
Role-based permission classes for HACT CTMS API endpoints.

Each permission class checks the user's roles via the UserRole table.
ViewSets apply these as permission_classes to enforce authorization.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


def _user_has_role(user, role_name):
    """Check if a user has a specific role (cached on the user object)."""
    if not user or not user.is_authenticated:
        return False
    # Superusers bypass role checks
    if user.is_superuser:
        return True
    # Cache roles on the user object to avoid repeated DB queries per request
    if not hasattr(user, "_cached_roles"):
        user._cached_roles = set(
            user.user_roles.values_list("role__name", flat=True)
        )
    return role_name in user._cached_roles


def _user_has_any_role(user, *role_names):
    """Check if a user has ANY of the specified roles."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not hasattr(user, "_cached_roles"):
        user._cached_roles = set(
            user.user_roles.values_list("role__name", flat=True)
        )
    return bool(user._cached_roles & set(role_names))


# =============================================================================
# Study-Level Permissions
# =============================================================================

class IsStudyAdmin(BasePermission):
    """Full access to study configuration (create/edit/archive studies)."""
    message = "Study Admin role required."

    def has_permission(self, request, view):
        return _user_has_any_role(request.user, "study_admin", "admin")


class IsDataManager(BasePermission):
    """Can manage forms, queries, subjects, and data cleaning workflows."""
    message = "Data Manager role required."

    def has_permission(self, request, view):
        return _user_has_any_role(
            request.user, "data_manager", "study_admin", "admin"
        )


class IsSiteCoordinator(BasePermission):
    """Can enter data, manage visits at their assigned sites."""
    message = "Site Coordinator role required."

    def has_permission(self, request, view):
        return _user_has_any_role(
            request.user,
            "site_coordinator", "data_manager", "study_admin", "admin",
        )


class IsMonitor(BasePermission):
    """Read-only access to clinical data for monitoring."""
    message = "Monitor role required."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return _user_has_any_role(
                request.user,
                "monitor", "data_manager", "study_admin", "admin",
            )
        return _user_has_any_role(
            request.user, "data_manager", "study_admin", "admin"
        )


class IsSafetyOfficer(BasePermission):
    """Full access to safety module (AE, SAE, CIOMS)."""
    message = "Safety Officer role required."

    def has_permission(self, request, view):
        return _user_has_any_role(
            request.user, "safety_officer", "study_admin", "admin"
        )


class IsLabManager(BasePermission):
    """Full access to laboratory data and sample tracking."""
    message = "Lab Manager role required."

    def has_permission(self, request, view):
        return _user_has_any_role(
            request.user, "lab_manager", "study_admin", "admin"
        )


class IsAuditor(BasePermission):
    """Read-only access to audit logs."""
    message = "Auditor role required."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return _user_has_any_role(
                request.user, "auditor", "study_admin", "admin"
            )
        return False  # Auditors can never write


class IsOpsManager(BasePermission):
    """Access to operational data (contracts, training, milestones)."""
    message = "Ops Manager role required."

    def has_permission(self, request, view):
        return _user_has_any_role(
            request.user, "ops_manager", "study_admin", "admin"
        )


# =============================================================================
# Composite Permissions — for commonly used combinations
# =============================================================================

class IsReadOnlyOrDataManager(BasePermission):
    """Any authenticated user can read; only DataManagers+ can write."""
    message = "Data Manager role required for write operations."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return _user_has_any_role(
            request.user, "data_manager", "study_admin", "admin"
        )


class IsReadOnlyOrStudyAdmin(BasePermission):
    """Any authenticated user can read; only StudyAdmins+ can write."""
    message = "Study Admin role required for write operations."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return _user_has_any_role(request.user, "study_admin", "admin")
