"""
Accounts Auth Views — Authentication API endpoints
=====================================================
/api/v1/auth/me/     — Current user profile with roles & sites
/api/v1/auth/token/  — Exchange Keycloak token for session (optional)
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import User


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return the current authenticated user's profile, roles, and site assignments.

    This is the primary endpoint for the frontend to know WHO is logged in
    and WHAT they can access.
    """
    user = request.user

    # Get user roles
    roles = list(
        user.user_roles.select_related("role").values_list("role__name", flat=True)
    )

    # Get site assignments
    site_assignments = list(
        user.site_assignments.select_related("site").values(
            "site_id",
            "site__site_code",
            "site__name",
            "role_at_site",
        )
    )

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "keycloak_id": str(user.keycloak_id),
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "roles": roles,
        "site_assignments": [
            {
                "site_id": sa["site_id"],
                "site_code": sa["site__site_code"],
                "site_name": sa["site__name"],
                "role_at_site": sa["role_at_site"],
            }
            for sa in site_assignments
        ],
        "date_joined": user.date_joined,
        "last_login": user.last_login,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_status(request):
    """Check if the current request is authenticated. Public endpoint."""
    if request.user and request.user.is_authenticated:
        return Response({
            "authenticated": True,
            "username": request.user.username,
        })
    return Response({
        "authenticated": False,
        "message": "Send a Bearer token in the Authorization header.",
    })
