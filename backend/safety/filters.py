"""Safety Filters — Advanced FilterSets for pharmacovigilance data."""

import django_filters

from .models import AdverseEvent


class AdverseEventFilter(django_filters.FilterSet):
    """Advanced filtering for adverse events."""

    subject_identifier = django_filters.CharFilter(
        field_name="subject__subject_identifier",
        lookup_expr="icontains",
    )
    site = django_filters.NumberFilter(
        field_name="subject__site_id",
    )
    start_date_after = django_filters.DateFilter(
        field_name="start_date", lookup_expr="gte",
    )
    start_date_before = django_filters.DateFilter(
        field_name="start_date", lookup_expr="lte",
    )
    ae_term_contains = django_filters.CharFilter(
        field_name="ae_term", lookup_expr="icontains",
    )

    class Meta:
        model = AdverseEvent
        fields = ["study", "severity", "serious", "causality", "outcome"]
