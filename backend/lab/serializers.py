"""Lab serializers — Enhanced with nested fields and auto-flagging."""

from rest_framework import serializers

from .models import LabResult, ReferenceRange, SampleCollection


class LabResultListSerializer(serializers.ModelSerializer):
    """Flat lab result with subject and flag display."""

    subject_identifier = serializers.CharField(
        source="subject.subject_identifier", read_only=True
    )
    site_code = serializers.CharField(
        source="subject.site.site_code", read_only=True
    )
    flag_display = serializers.CharField(
        source="get_flag_display", read_only=True
    )
    visit_name = serializers.SerializerMethodField()

    class Meta:
        model = LabResult
        fields = [
            "id", "subject", "subject_identifier", "site_code",
            "subject_visit", "visit_name",
            "test_name", "result_value", "unit",
            "reference_range_low", "reference_range_high",
            "flag", "flag_display",
            "result_date", "imported_at", "imported_by",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "imported_at")

    def get_visit_name(self, obj):
        if obj.subject_visit and obj.subject_visit.visit:
            return obj.subject_visit.visit.visit_name
        return None

    def validate(self, data):
        """Auto-flag results based on reference ranges."""
        result_value = data.get("result_value", "")
        ref_low = data.get("reference_range_low")
        ref_high = data.get("reference_range_high")

        if result_value and ref_low is not None and ref_high is not None:
            try:
                val = float(result_value)
                if val < float(ref_low):
                    data["flag"] = "L"
                elif val > float(ref_high):
                    data["flag"] = "H"
                else:
                    data["flag"] = "N"
            except (ValueError, TypeError):
                pass  # Non-numeric results are not flagged

        return data


class LabResultDetailSerializer(LabResultListSerializer):
    """Nested lab result with audit fields."""

    class Meta(LabResultListSerializer.Meta):
        fields = LabResultListSerializer.Meta.fields + [
            "created_by", "updated_by",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "imported_at",
            "created_by", "updated_by",
        )


class ReferenceRangeSerializer(serializers.ModelSerializer):
    """Reference range serializer."""

    study_protocol = serializers.CharField(
        source="study.protocol_number", read_only=True
    )

    class Meta:
        model = ReferenceRange
        fields = [
            "id", "study", "study_protocol",
            "test_name", "gender", "age_lower", "age_upper",
            "range_low", "range_high",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class SampleCollectionSerializer(serializers.ModelSerializer):
    """Sample collection serializer."""

    subject_identifier = serializers.CharField(
        source="subject.subject_identifier", read_only=True
    )

    class Meta:
        model = SampleCollection
        fields = [
            "id", "subject", "subject_identifier",
            "sample_type",
            "collection_date", "status",
            "senaite_sample_id",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")
