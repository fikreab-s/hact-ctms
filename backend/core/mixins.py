"""
Core — ViewSet Mixins
=======================
Reusable mixins for HACT CTMS ViewSets.

StudyScopedMixin: Filters querysets by user's assigned studies/sites.
AuditCreateMixin: Auto-sets created_by/updated_by from request context.
"""

from rest_framework.permissions import IsAuthenticated


class AuditCreateMixin:
    """Mixin that auto-sets created_by and updated_by on save.

    Used by all ViewSets that inherit from TimeStampedModel.
    Sets created_by on create, updated_by on every update.
    """

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class StudyScopedMixin:
    """Mixin that filters querysets to only show data the user has access to.

    Site coordinators see only data from their assigned sites.
    Data managers and study admins see all data.

    Requires the model to have a study or site FK. Override
    `get_study_filter_field()` to customize the filter lookup.
    """

    study_filter_field = "study"
    site_filter_field = "site"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return qs.none()

        # Superusers and study_admin/admin/data_manager see everything
        if user.is_superuser:
            return qs
        if hasattr(user, "_cached_roles"):
            roles = user._cached_roles
        else:
            roles = set(user.user_roles.values_list("role__name", flat=True))
            user._cached_roles = roles

        unrestricted_roles = {"admin", "study_admin", "data_manager", "monitor"}
        if roles & unrestricted_roles:
            return qs

        # Site coordinators: filter by their assigned sites
        assigned_site_ids = list(
            user.site_assignments.values_list("site_id", flat=True)
        )

        if not assigned_site_ids:
            return qs.none()

        # Try site filter first, then study
        if hasattr(qs.model, self.site_filter_field):
            return qs.filter(**{f"{self.site_filter_field}__in": assigned_site_ids})
        elif hasattr(qs.model, self.study_filter_field):
            from clinical.models import Site
            study_ids = Site.objects.filter(
                id__in=assigned_site_ids
            ).values_list("study_id", flat=True)
            return qs.filter(**{f"{self.study_filter_field}__in": study_ids})

        return qs
