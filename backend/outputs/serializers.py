"""
Outputs Serializers — Enhanced with nested context
=====================================================
"""

from rest_framework import serializers

from .models import DataQualityReport, DatasetSnapshot


class DatasetSnapshotListSerializer(serializers.ModelSerializer):
    """List view — flat with study context."""

    study_protocol = serializers.CharField(source="study.protocol_number", read_only=True)
    generated_by_username = serializers.CharField(
        source="generated_by.username", read_only=True, default=""
    )

    class Meta:
        model = DatasetSnapshot
        fields = [
            "id", "study", "study_protocol",
            "snapshot_date", "snapshot_type", "file_url",
            "generated_by", "generated_by_username",
            "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "snapshot_date", "created_at", "updated_at")


class DatasetSnapshotDetailSerializer(DatasetSnapshotListSerializer):
    """Detail view — includes criteria JSON."""

    class Meta(DatasetSnapshotListSerializer.Meta):
        fields = DatasetSnapshotListSerializer.Meta.fields + ["criteria"]


class DataQualityReportListSerializer(serializers.ModelSerializer):
    """List view — flat with study context."""

    study_protocol = serializers.CharField(source="study.protocol_number", read_only=True)
    report_type_display = serializers.CharField(
        source="get_report_type_display", read_only=True
    )

    class Meta:
        model = DataQualityReport
        fields = [
            "id", "study", "study_protocol",
            "report_type", "report_type_display",
            "generated_at", "file_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "generated_at", "created_at", "updated_at")


class DataQualityReportDetailSerializer(DataQualityReportListSerializer):
    """Detail view — includes full report_data JSON."""

    class Meta(DataQualityReportListSerializer.Meta):
        fields = DataQualityReportListSerializer.Meta.fields + ["report_data"]


# =============================================================================
# Action Serializers
# =============================================================================


class ExportCSVSerializer(serializers.Serializer):
    """Request body for CSV export action."""

    study = serializers.IntegerField(help_text="Study ID to export data from.")


class ExportODMSerializer(serializers.Serializer):
    """Request body for CDISC ODM export action."""

    study = serializers.IntegerField(help_text="Study ID to export data from.")


class GenerateQualityReportSerializer(serializers.Serializer):
    """Request body for quality report generation."""

    REPORT_TYPE_CHOICES = [
        ("missing_data", "Missing Data"),
        ("query_status", "Query Status"),
        ("enrollment", "Enrollment Progress"),
        ("completion", "Form Completion"),
        ("visit_compliance", "Visit Compliance"),
        ("comprehensive", "Comprehensive (All)"),
    ]

    study = serializers.IntegerField(help_text="Study ID to generate report for.")
    report_type = serializers.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        default="comprehensive",
        help_text="Type of quality report to generate.",
    )
