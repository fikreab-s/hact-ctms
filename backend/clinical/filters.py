"""
Clinical Filters — Advanced FilterSets
==========================================
Custom FilterSets with date ranges, status filtering,
and cross-model lookups for clinical data.
"""

import django_filters

from .models import (
    FormInstance, Query, Subject, SubjectVisit,
)


class SubjectFilter(django_filters.FilterSet):
    """Advanced filtering for subjects."""

    # Date range filters
    enrollment_date_after = django_filters.DateFilter(
        field_name="enrollment_date", lookup_expr="gte",
        label="Enrolled on or after",
    )
    enrollment_date_before = django_filters.DateFilter(
        field_name="enrollment_date", lookup_expr="lte",
        label="Enrolled on or before",
    )
    consent_date_after = django_filters.DateFilter(
        field_name="consent_signed_date", lookup_expr="gte",
    )

    # Related model filters
    site_country = django_filters.CharFilter(
        field_name="site__country", lookup_expr="iexact",
        label="Site country",
    )
    site_code = django_filters.CharFilter(
        field_name="site__site_code", lookup_expr="iexact",
    )

    # Search
    identifier = django_filters.CharFilter(
        field_name="subject_identifier", lookup_expr="icontains",
        label="Subject ID (partial)",
    )

    class Meta:
        model = Subject
        fields = ["study", "site", "status"]


class SubjectVisitFilter(django_filters.FilterSet):
    """Advanced filtering for subject visits."""

    actual_date_after = django_filters.DateFilter(
        field_name="actual_date", lookup_expr="gte",
    )
    actual_date_before = django_filters.DateFilter(
        field_name="actual_date", lookup_expr="lte",
    )
    visit_type = django_filters.CharFilter(
        method="filter_visit_type",
        label="Visit type (screening, baseline, follow_up)",
    )
    subject_identifier = django_filters.CharFilter(
        field_name="subject__subject_identifier", lookup_expr="icontains",
    )
    site = django_filters.NumberFilter(
        field_name="subject__site_id",
    )

    class Meta:
        model = SubjectVisit
        fields = ["subject", "visit", "status"]

    def filter_visit_type(self, queryset, name, value):
        if value == "screening":
            return queryset.filter(visit__is_screening=True)
        elif value == "baseline":
            return queryset.filter(visit__is_baseline=True)
        elif value == "follow_up":
            return queryset.filter(visit__is_follow_up=True)
        return queryset


class FormInstanceFilter(django_filters.FilterSet):
    """Advanced filtering for form instances."""

    form_name = django_filters.CharFilter(
        field_name="form__name", lookup_expr="icontains",
    )
    subject_identifier = django_filters.CharFilter(
        field_name="subject__subject_identifier", lookup_expr="icontains",
    )
    site = django_filters.NumberFilter(
        field_name="subject__site_id",
    )
    study = django_filters.NumberFilter(
        field_name="subject__study_id",
    )
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte",
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte",
    )

    class Meta:
        model = FormInstance
        fields = ["form", "subject", "status"]


class QueryFilter(django_filters.FilterSet):
    """Advanced filtering for data queries."""

    subject = django_filters.CharFilter(
        field_name="item_response__form_instance__subject__subject_identifier",
        lookup_expr="icontains",
        label="Subject identifier (partial)",
    )
    form = django_filters.NumberFilter(
        field_name="item_response__form_instance__form_id",
    )
    site = django_filters.NumberFilter(
        field_name="item_response__form_instance__subject__site_id",
    )
    study = django_filters.NumberFilter(
        field_name="item_response__form_instance__subject__study_id",
    )
    raised_after = django_filters.DateTimeFilter(
        field_name="raised_at", lookup_expr="gte",
    )
    raised_before = django_filters.DateTimeFilter(
        field_name="raised_at", lookup_expr="lte",
    )

    class Meta:
        model = Query
        fields = ["status", "raised_by", "resolved_by"]
