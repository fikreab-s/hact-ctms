"""Safety serializers — Enhanced with nested fields."""

from rest_framework import serializers

from .models import AdverseEvent, CiomsForm, SafetyReview


class AdverseEventListSerializer(serializers.ModelSerializer):
    """Flat AE serializer with related data for list view."""

    subject_identifier = serializers.CharField(
        source="subject.subject_identifier", read_only=True
    )
    site_code = serializers.CharField(
        source="subject.site.site_code", read_only=True
    )
    study_protocol = serializers.CharField(
        source="study.protocol_number", read_only=True
    )
    severity_display = serializers.CharField(
        source="get_severity_display", read_only=True
    )
    causality_display = serializers.CharField(
        source="get_causality_display", read_only=True
    )
    outcome_display = serializers.CharField(
        source="get_outcome_display", read_only=True
    )
    days_open = serializers.SerializerMethodField()

    class Meta:
        model = AdverseEvent
        fields = [
            "id", "subject", "subject_identifier", "site_code",
            "study", "study_protocol",
            "ae_term", "start_date", "end_date",
            "severity", "severity_display",
            "serious", "serious_criteria",
            "causality", "causality_display",
            "outcome", "outcome_display",
            "action_taken",
            "days_open",
            "reported_at", "reported_by",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "reported_at")

    def get_days_open(self, obj):
        """Calculate days the AE has been open."""
        if obj.end_date:
            return (obj.end_date - obj.start_date).days
        from datetime import date
        return (date.today() - obj.start_date).days

    def validate(self, data):
        """Validate AE business rules."""
        # SAEs require serious_criteria
        serious = data.get("serious", getattr(self.instance, "serious", False))
        if serious:
            criteria = data.get(
                "serious_criteria",
                getattr(self.instance, "serious_criteria", ""),
            )
            if not criteria:
                raise serializers.ValidationError({
                    "serious_criteria": "Seriousness criteria required for SAEs "
                    "(death, hospitalization, etc.)."
                })

        # end_date must be after start_date
        start = data.get("start_date", getattr(self.instance, "start_date", None))
        end = data.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        return data


class AdverseEventDetailSerializer(AdverseEventListSerializer):
    """Nested AE serializer with CIOMS forms."""

    cioms_forms = serializers.SerializerMethodField()

    class Meta(AdverseEventListSerializer.Meta):
        fields = AdverseEventListSerializer.Meta.fields + [
            "cioms_forms", "created_by", "updated_by",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "reported_at",
            "created_by", "updated_by",
        )

    def get_cioms_forms(self, obj):
        return CiomsFormSerializer(obj.cioms_forms.all(), many=True).data


class CiomsFormSerializer(serializers.ModelSerializer):
    """CIOMS form serializer."""

    ae_term = serializers.CharField(
        source="adverse_event.ae_term", read_only=True
    )
    subject_identifier = serializers.SerializerMethodField()

    class Meta:
        model = CiomsForm
        fields = [
            "id", "adverse_event", "ae_term", "subject_identifier",
            "form_version", "generated_date",
            "submission_deadline", "submitted_date",
            "regulatory_authority", "status", "file_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "generated_date")

    def get_subject_identifier(self, obj):
        try:
            return obj.adverse_event.subject.subject_identifier
        except AttributeError:
            return None


class SafetyReviewSerializer(serializers.ModelSerializer):
    """Safety review serializer."""

    study_protocol = serializers.CharField(
        source="study.protocol_number", read_only=True
    )
    review_type_display = serializers.CharField(
        source="get_review_type_display", read_only=True
    )

    class Meta:
        model = SafetyReview
        fields = [
            "id", "study", "study_protocol",
            "review_type", "review_type_display",
            "review_date", "summary", "file_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")
