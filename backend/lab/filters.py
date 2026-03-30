"""Lab Filters — Advanced FilterSets for laboratory data."""

import django_filters

from .models import LabResult


class LabResultFilter(django_filters.FilterSet):
    """Advanced filtering for lab results."""

    subject_identifier = django_filters.CharFilter(
        field_name="subject__subject_identifier",
        lookup_expr="icontains",
    )
    site = django_filters.NumberFilter(
        field_name="subject__site_id",
    )
    study = django_filters.NumberFilter(
        field_name="subject__study_id",
    )
    result_date_after = django_filters.DateFilter(
        field_name="result_date", lookup_expr="gte",
    )
    result_date_before = django_filters.DateFilter(
        field_name="result_date", lookup_expr="lte",
    )
    test_name_contains = django_filters.CharFilter(
        field_name="test_name", lookup_expr="icontains",
    )

    class Meta:
        model = LabResult
        fields = ["subject", "test_name", "flag"]
