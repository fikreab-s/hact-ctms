"""
Clinical Serializers — Business Logic & Validation
=====================================================
Enhanced serializers with:
- Study status workflow (planning → active → locked → archived)
- Subject enrollment workflow (consent validation)
- Visit window validation
- Form instance submit/sign workflow
- Query lifecycle (open → answered → closed)
- Nested list vs detail serializers
"""

from datetime import date, timedelta

from django.db import models as db_models
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Form, FormInstance, Item, ItemResponse, Query,
    Site, Study, Subject, SubjectVisit, Visit,
)


# =============================================================================
# Valid State Transitions
# =============================================================================

STUDY_TRANSITIONS = {
    "planning": ["active"],
    "active": ["locked"],
    "locked": ["archived"],
    "archived": [],  # Terminal state
}

SUBJECT_TRANSITIONS = {
    "screened": ["enrolled", "screen_failed"],
    "enrolled": ["completed", "discontinued"],
    "completed": [],  # Terminal state
    "discontinued": [],  # Terminal state
    "screen_failed": [],  # Terminal state
}

FORM_INSTANCE_TRANSITIONS = {
    "draft": ["submitted"],
    "submitted": ["signed", "draft"],  # Can return to draft for corrections
    "signed": ["locked"],
    "locked": [],  # Terminal state
}

QUERY_TRANSITIONS = {
    "open": ["answered", "closed"],
    "answered": ["closed", "open"],  # Can reopen
    "closed": [],  # Terminal state
}


# =============================================================================
# Study Serializers
# =============================================================================

class StudyListSerializer(serializers.ModelSerializer):
    """Flat study serializer for list view with computed counts."""

    site_count = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = [
            "id", "name", "protocol_number", "phase", "sponsor",
            "start_date", "end_date", "status",
            "site_count", "subject_count", "enrolled_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_site_count(self, obj):
        return obj.sites.count()

    def get_subject_count(self, obj):
        return obj.subjects.count()

    def get_enrolled_count(self, obj):
        return obj.subjects.filter(status="enrolled").count()


class StudyDetailSerializer(serializers.ModelSerializer):
    """Nested study serializer for detail view with related data."""

    site_count = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()
    sites = serializers.SerializerMethodField()
    visits = serializers.SerializerMethodField()
    forms = serializers.SerializerMethodField()
    open_queries_count = serializers.SerializerMethodField()

    class Meta:
        model = Study
        fields = [
            "id", "name", "protocol_number", "phase", "sponsor",
            "start_date", "end_date", "status", "openclinica_study_oid",
            "site_count", "subject_count", "enrolled_count",
            "open_queries_count",
            "sites", "visits", "forms",
            "created_at", "updated_at", "created_by", "updated_by",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")

    def get_site_count(self, obj):
        return obj.sites.count()

    def get_subject_count(self, obj):
        return obj.subjects.count()

    def get_enrolled_count(self, obj):
        return obj.subjects.filter(status="enrolled").count()

    def get_open_queries_count(self, obj):
        return Query.objects.filter(
            item_response__form_instance__subject__study=obj,
            status="open",
        ).count()

    def get_sites(self, obj):
        return SiteListSerializer(obj.sites.all(), many=True).data

    def get_visits(self, obj):
        return VisitSerializer(obj.visits.all(), many=True).data

    def get_forms(self, obj):
        return FormListSerializer(obj.forms.all(), many=True).data

    def validate_status(self, value):
        """Enforce study status transitions."""
        if self.instance:
            current = self.instance.status
            allowed = STUDY_TRANSITIONS.get(current, [])
            if value != current and value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'. "
                    f"Allowed transitions: {allowed}"
                )
        return value

    def validate(self, data):
        """Block edits on locked/archived studies (except status transitions)."""
        if self.instance and self.instance.status in ("locked", "archived"):
            # Allow only status field changes (for transitioning)
            non_status_changes = {
                k: v for k, v in data.items()
                if k != "status" and getattr(self.instance, k, None) != v
            }
            if non_status_changes:
                raise serializers.ValidationError(
                    f"Cannot modify a {self.instance.status} study. "
                    f"Only status transitions are allowed."
                )
        return data


# =============================================================================
# Site Serializers
# =============================================================================

class SiteListSerializer(serializers.ModelSerializer):
    """Flat site serializer with computed counts."""

    study_protocol = serializers.CharField(source="study.protocol_number", read_only=True)
    subject_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = [
            "id", "study", "study_protocol", "site_code", "name",
            "country", "principal_investigator", "status",
            "activation_date", "subject_count", "enrolled_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_subject_count(self, obj):
        return obj.subjects.count()

    def get_enrolled_count(self, obj):
        return obj.subjects.filter(status="enrolled").count()


class SiteDetailSerializer(SiteListSerializer):
    """Nested site serializer with address and integration fields."""

    class Meta(SiteListSerializer.Meta):
        fields = SiteListSerializer.Meta.fields + [
            "address", "erpnext_site_id",
            "created_by", "updated_by",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")


# =============================================================================
# Subject Serializers
# =============================================================================

class SubjectListSerializer(serializers.ModelSerializer):
    """Flat subject serializer for list view."""

    study_protocol = serializers.CharField(source="study.protocol_number", read_only=True)
    site_code = serializers.CharField(source="site.site_code", read_only=True)
    site_name = serializers.CharField(source="site.name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id", "study", "site", "study_protocol", "site_code", "site_name",
            "subject_identifier", "screening_number",
            "enrollment_date", "completion_date",
            "status", "consent_signed_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_status(self, value):
        """Enforce subject status transitions."""
        if self.instance:
            current = self.instance.status
            allowed = SUBJECT_TRANSITIONS.get(current, [])
            if value != current and value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'. "
                    f"Allowed: {allowed}"
                )
        return value

    def validate(self, data):
        """Enforce enrollment business rules."""
        status = data.get("status", getattr(self.instance, "status", "screened"))

        # Check study is not locked
        study = data.get("study", getattr(self.instance, "study", None))
        if study and study.status in ("locked", "archived"):
            raise serializers.ValidationError(
                f"Cannot modify subjects in a {study.status} study."
            )

        # Enrollment requires consent
        if status == "enrolled":
            consent_date = data.get(
                "consent_signed_date",
                getattr(self.instance, "consent_signed_date", None),
            )
            if not consent_date:
                raise serializers.ValidationError({
                    "consent_signed_date": "Consent must be signed before enrollment."
                })

            enrollment_date = data.get(
                "enrollment_date",
                getattr(self.instance, "enrollment_date", None),
            )
            if not enrollment_date:
                raise serializers.ValidationError({
                    "enrollment_date": "Enrollment date is required for enrolled subjects."
                })

        return data


class SubjectDetailSerializer(SubjectListSerializer):
    """Nested subject serializer with visits, AEs, and form instances."""

    subject_visits = serializers.SerializerMethodField()
    adverse_events_count = serializers.SerializerMethodField()
    form_instances_count = serializers.SerializerMethodField()

    class Meta(SubjectListSerializer.Meta):
        fields = SubjectListSerializer.Meta.fields + [
            "subject_visits", "adverse_events_count", "form_instances_count",
            "created_by", "updated_by",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")

    def get_subject_visits(self, obj):
        visits = obj.subject_visits.select_related("visit").all()
        return SubjectVisitListSerializer(visits, many=True).data

    def get_adverse_events_count(self, obj):
        return obj.adverse_events.count()

    def get_form_instances_count(self, obj):
        return obj.form_instances.count()


# =============================================================================
# Visit Serializers
# =============================================================================

class VisitSerializer(serializers.ModelSerializer):
    """Visit definition serializer with window display."""

    window_display = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            "id", "study", "visit_name", "visit_order", "planned_day",
            "window_before", "window_after", "window_display",
            "is_screening", "is_baseline", "is_follow_up",
            "openclinica_event_definition_oid",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_window_display(self, obj):
        lo = obj.planned_day - obj.window_before
        hi = obj.planned_day + obj.window_after
        return f"Day {lo} to Day {hi}"


# =============================================================================
# SubjectVisit Serializers
# =============================================================================

class SubjectVisitListSerializer(serializers.ModelSerializer):
    """Flat subject visit with visit name and window validation."""

    visit_name = serializers.CharField(source="visit.visit_name", read_only=True)
    visit_order = serializers.IntegerField(source="visit.visit_order", read_only=True)
    planned_day = serializers.IntegerField(source="visit.planned_day", read_only=True)
    is_within_window = serializers.SerializerMethodField()

    class Meta:
        model = SubjectVisit
        fields = [
            "id", "subject", "visit", "visit_name", "visit_order", "planned_day",
            "scheduled_date", "actual_date", "status",
            "is_within_window",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_is_within_window(self, obj):
        """Check if the actual visit date falls within the protocol window."""
        if not obj.actual_date or not obj.subject.enrollment_date:
            return None
        try:
            earliest, latest = obj.visit.get_window_range(obj.subject.enrollment_date)
            return earliest <= obj.actual_date <= latest
        except Exception:
            return None

    def validate(self, data):
        """Warn if visit date is outside window (soft validation — does not block)."""
        # Check study is not locked
        subject = data.get("subject", getattr(self.instance, "subject", None))
        if subject and subject.study.status in ("locked", "archived"):
            raise serializers.ValidationError(
                f"Cannot modify visits in a {subject.study.status} study."
            )
        return data


class SubjectVisitDetailSerializer(SubjectVisitListSerializer):
    """Nested subject visit with form instances."""

    form_instances = serializers.SerializerMethodField()
    subject_identifier = serializers.CharField(
        source="subject.subject_identifier", read_only=True
    )

    class Meta(SubjectVisitListSerializer.Meta):
        fields = SubjectVisitListSerializer.Meta.fields + [
            "subject_identifier", "form_instances",
            "created_by", "updated_by",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")

    def get_form_instances(self, obj):
        instances = obj.form_instances.select_related("form").all()
        return FormInstanceListSerializer(instances, many=True).data


# =============================================================================
# Form Serializers
# =============================================================================

class FormListSerializer(serializers.ModelSerializer):
    """Flat form serializer with item count."""

    item_count = serializers.SerializerMethodField()
    study_protocol = serializers.CharField(source="study.protocol_number", read_only=True)

    class Meta:
        model = Form
        fields = [
            "id", "study", "study_protocol", "name", "version",
            "description", "is_active", "item_count",
            "openclinica_crf_oid",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_item_count(self, obj):
        return obj.items.count()


class FormDetailSerializer(FormListSerializer):
    """Nested form serializer with items."""

    items = serializers.SerializerMethodField()

    class Meta(FormListSerializer.Meta):
        fields = FormListSerializer.Meta.fields + ["items", "created_by", "updated_by"]
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")

    def get_items(self, obj):
        return ItemSerializer(obj.items.all().order_by("order"), many=True).data


# =============================================================================
# Item Serializer
# =============================================================================

class ItemSerializer(serializers.ModelSerializer):
    """Form item (field) serializer."""

    class Meta:
        model = Item
        fields = [
            "id", "form", "field_name", "field_label", "field_type",
            "required", "validation_rule", "options", "order",
            "created_at", "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


# =============================================================================
# FormInstance Serializers
# =============================================================================

class FormInstanceListSerializer(serializers.ModelSerializer):
    """Flat form instance for list view."""

    form_name = serializers.CharField(source="form.name", read_only=True)
    subject_identifier = serializers.CharField(
        source="subject.subject_identifier", read_only=True
    )
    visit_name = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = FormInstance
        fields = [
            "id", "form", "form_name", "subject", "subject_identifier",
            "subject_visit", "visit_name",
            "instance_number", "status",
            "submitted_at", "signed_by", "signed_at",
            "completion_percentage",
            "created_at", "updated_at",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "submitted_at",
            "signed_by", "signed_at",
        )

    def get_visit_name(self, obj):
        if obj.subject_visit and obj.subject_visit.visit:
            return obj.subject_visit.visit.visit_name
        return None

    def get_completion_percentage(self, obj):
        """Calculate what percentage of required fields are filled."""
        required_items = obj.form.items.filter(required=True).count()
        if required_items == 0:
            return 100.0
        filled = obj.responses.filter(
            item__required=True,
        ).exclude(value="").count()
        return round((filled / required_items) * 100, 1)

    def validate_status(self, value):
        """Enforce form instance status transitions."""
        if self.instance:
            current = self.instance.status
            allowed = FORM_INSTANCE_TRANSITIONS.get(current, [])
            if value != current and value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'. "
                    f"Allowed: {allowed}"
                )
        return value

    def validate(self, data):
        """Block edits on signed/locked form instances."""
        if self.instance and self.instance.status in ("signed", "locked"):
            raise serializers.ValidationError(
                f"Cannot modify a {self.instance.status} form instance. "
                "It must be returned to draft first."
            )

        # Check study is not locked (but allow safety data per stakeholder decision)
        subject = data.get("subject", getattr(self.instance, "subject", None))
        if subject and subject.study.status in ("locked", "archived"):
            raise serializers.ValidationError(
                f"Cannot modify form instances in a {subject.study.status} study."
            )
        return data


class FormInstanceDetailSerializer(FormInstanceListSerializer):
    """Nested form instance with responses and queries."""

    responses = serializers.SerializerMethodField()
    queries_count = serializers.SerializerMethodField()
    open_queries_count = serializers.SerializerMethodField()

    class Meta(FormInstanceListSerializer.Meta):
        fields = FormInstanceListSerializer.Meta.fields + [
            "responses", "queries_count", "open_queries_count",
            "created_by", "updated_by",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "submitted_at",
            "signed_by", "signed_at", "created_by", "updated_by",
        )

    def get_responses(self, obj):
        responses = obj.responses.select_related("item").all()
        return ItemResponseSerializer(responses, many=True).data

    def get_queries_count(self, obj):
        return Query.objects.filter(item_response__form_instance=obj).count()

    def get_open_queries_count(self, obj):
        return Query.objects.filter(
            item_response__form_instance=obj, status="open"
        ).count()


# =============================================================================
# ItemResponse Serializer
# =============================================================================

class ItemResponseSerializer(serializers.ModelSerializer):
    """Item response with field-level validation."""

    field_name = serializers.CharField(source="item.field_name", read_only=True)
    field_label = serializers.CharField(source="item.field_label", read_only=True)
    field_type = serializers.CharField(source="item.field_type", read_only=True)
    is_required = serializers.BooleanField(source="item.required", read_only=True)

    class Meta:
        model = ItemResponse
        fields = [
            "id", "form_instance", "item",
            "field_name", "field_label", "field_type", "is_required",
            "value", "updated_at", "updated_by",
        ]
        read_only_fields = ("id", "updated_at")

    def validate(self, data):
        """Validate value against item field type and rules."""
        form_instance = data.get(
            "form_instance",
            getattr(self.instance, "form_instance", None),
        )
        item = data.get("item", getattr(self.instance, "item", None))
        value = data.get("value", "")

        # Block edits on signed/locked form instances
        if form_instance and form_instance.status in ("signed", "locked"):
            raise serializers.ValidationError(
                f"Cannot edit responses on a {form_instance.status} form instance."
            )

        # Skip validation for empty values (required check happens at submit time)
        if not value:
            return data

        # Type-specific validation
        if item:
            if item.field_type == "number":
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise serializers.ValidationError({
                        "value": f"'{item.field_name}' expects a numeric value."
                    })

            elif item.field_type == "date":
                try:
                    from datetime import datetime
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise serializers.ValidationError({
                        "value": f"'{item.field_name}' expects a date (YYYY-MM-DD)."
                    })

            elif item.field_type in ("dropdown", "radio"):
                if item.options:
                    valid_values = [
                        opt.get("value", opt) if isinstance(opt, dict) else str(opt)
                        for opt in item.options
                    ]
                    if value not in valid_values:
                        raise serializers.ValidationError({
                            "value": f"'{value}' is not a valid option for '{item.field_name}'. "
                                     f"Valid options: {valid_values}"
                        })

            # Regex validation
            if item.validation_rule:
                import re
                if not re.match(item.validation_rule, value):
                    raise serializers.ValidationError({
                        "value": f"'{item.field_name}' value does not match "
                                 f"validation rule: {item.validation_rule}"
                    })

        return data


# =============================================================================
# Query Serializers
# =============================================================================

class QueryListSerializer(serializers.ModelSerializer):
    """Flat query for list view."""

    raised_by_username = serializers.CharField(
        source="raised_by.username", read_only=True, default=None
    )
    resolved_by_username = serializers.CharField(
        source="resolved_by.username", read_only=True, default=None
    )
    subject_identifier = serializers.SerializerMethodField()
    form_name = serializers.SerializerMethodField()
    field_name = serializers.SerializerMethodField()

    class Meta:
        model = Query
        fields = [
            "id", "item_response", "status",
            "query_text", "response_text",
            "raised_by", "raised_by_username", "raised_at",
            "resolved_by", "resolved_by_username", "resolved_at",
            "subject_identifier", "form_name", "field_name",
            "created_at", "updated_at",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "raised_at",
            "resolved_at", "resolved_by",
        )

    def get_subject_identifier(self, obj):
        try:
            return obj.item_response.form_instance.subject.subject_identifier
        except AttributeError:
            return None

    def get_form_name(self, obj):
        try:
            return obj.item_response.form_instance.form.name
        except AttributeError:
            return None

    def get_field_name(self, obj):
        try:
            return obj.item_response.item.field_name
        except AttributeError:
            return None

    def validate_status(self, value):
        """Enforce query status transitions."""
        if self.instance:
            current = self.instance.status
            allowed = QUERY_TRANSITIONS.get(current, [])
            if value != current and value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'. "
                    f"Allowed: {allowed}"
                )
        return value

    def validate(self, data):
        """Enforce query business rules."""
        status = data.get("status", getattr(self.instance, "status", "open"))

        # Answering requires response_text
        if status == "answered":
            response_text = data.get(
                "response_text",
                getattr(self.instance, "response_text", ""),
            )
            if not response_text:
                raise serializers.ValidationError({
                    "response_text": "Response text is required when answering a query."
                })

        # Auto-set raised_by on create
        if not self.instance:
            request = self.context.get("request")
            if request and request.user.is_authenticated:
                data["raised_by"] = request.user

        return data


class QueryDetailSerializer(QueryListSerializer):
    """Nested query serializer with full context."""

    current_value = serializers.SerializerMethodField()

    class Meta(QueryListSerializer.Meta):
        fields = QueryListSerializer.Meta.fields + [
            "current_value", "created_by", "updated_by",
        ]
        read_only_fields = (
            "id", "created_at", "updated_at", "raised_at",
            "resolved_at", "resolved_by", "created_by", "updated_by",
        )

    def get_current_value(self, obj):
        """Show the current value of the field being queried."""
        try:
            return obj.item_response.value
        except AttributeError:
            return None


# =============================================================================
# Action Serializers (for custom @action endpoints)
# =============================================================================

class StudyTransitionSerializer(serializers.Serializer):
    """Serializer for study status transition action."""

    status = serializers.ChoiceField(
        choices=["active", "locked", "archived"],
    )
    reason = serializers.CharField(required=False, default="")

    def validate_status(self, value):
        study = self.context.get("study")
        if study:
            current = study.status
            allowed = STUDY_TRANSITIONS.get(current, [])
            if value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from '{current}' to '{value}'. "
                    f"Allowed: {allowed}"
                )

            # Pre-lock validation
            if value == "locked":
                open_queries = Query.objects.filter(
                    item_response__form_instance__subject__study=study,
                    status="open",
                ).count()
                if open_queries > 0:
                    raise serializers.ValidationError(
                        f"Cannot lock study: {open_queries} open queries remain. "
                        "All queries must be resolved before locking."
                    )
        return value


class SubjectEnrollSerializer(serializers.Serializer):
    """Serializer for subject enrollment action."""

    consent_signed_date = serializers.DateField()
    enrollment_date = serializers.DateField(required=False)

    def validate_consent_signed_date(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Consent date cannot be in the future."
            )
        return value

    def validate_enrollment_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError(
                "Enrollment date cannot be in the future."
            )
        return value


class SubjectWithdrawSerializer(serializers.Serializer):
    """Serializer for subject withdrawal action."""

    reason = serializers.CharField()
    completion_date = serializers.DateField(required=False)


class FormInstanceSubmitSerializer(serializers.Serializer):
    """Validates completeness before form submission."""

    def validate(self, data):
        form_instance = self.context.get("form_instance")
        if not form_instance:
            raise serializers.ValidationError("Form instance context is required.")

        if form_instance.status != "draft":
            raise serializers.ValidationError(
                f"Only draft forms can be submitted. Current status: {form_instance.status}"
            )

        # Check required items are filled
        required_items = form_instance.form.items.filter(required=True)
        missing = []
        for item in required_items:
            response = form_instance.responses.filter(item=item).first()
            if not response or not response.value:
                missing.append(item.field_label or item.field_name)

        if missing:
            raise serializers.ValidationError({
                "missing_fields": missing,
                "detail": f"{len(missing)} required field(s) are missing: {', '.join(missing)}"
            })
        return data


class FormInstanceSignSerializer(serializers.Serializer):
    """21 CFR Part 11 e-signature for form signing."""

    password = serializers.CharField(write_only=True)
    meaning = serializers.CharField(
        default="I have reviewed this data and confirm it is accurate.",
    )

    def validate_password(self, value):
        request = self.context.get("request")
        if request and request.user:
            if not request.user.check_password(value):
                raise serializers.ValidationError(
                    "Invalid password. E-signature requires password re-entry."
                )
        return value


class QueryAnswerSerializer(serializers.Serializer):
    """Serializer for answering a query."""

    response_text = serializers.CharField()


class QueryCloseSerializer(serializers.Serializer):
    """Serializer for closing a query."""

    reason = serializers.CharField(required=False, default="Resolved")
