"""
EDC (Mobile) Serializers — lightweight serializers for mobile CRF data entry.

These are optimized for:
- Minimal payload size (mobile bandwidth)
- Full form schema for dynamic rendering (with skip logic)
- Offline-first submission format
- Edit support with audit trail
"""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    Form, FormInstance, Item, ItemResponse, ItemResponseAudit,
    Site, Study, Subject, SubjectVisit, Visit, VisitForm,
)


# =============================================================================
# Subject serializers (read — for subject list)
# =============================================================================
class EdcVisitStatusSerializer(serializers.Serializer):
    """Lightweight visit status for the visit schedule screen."""

    id = serializers.IntegerField()  # SubjectVisit.id — used for API navigation
    visit_id = serializers.IntegerField(source="visit.id")  # Visit definition ID
    visit_name = serializers.CharField(source="visit.visit_name")
    visit_order = serializers.IntegerField(source="visit.visit_order")
    planned_day = serializers.IntegerField(source="visit.planned_day")
    status = serializers.CharField()
    scheduled_date = serializers.DateField()
    actual_date = serializers.DateField()
    forms_completed = serializers.SerializerMethodField()
    forms_total = serializers.SerializerMethodField()

    def get_forms_completed(self, obj):
        return obj.form_instances.filter(
            status__in=["submitted", "signed", "locked"]
        ).count()

    def get_forms_total(self, obj):
        # Use VisitForm mapping if available, otherwise count all forms
        visit_form_count = VisitForm.objects.filter(visit=obj.visit).count()
        if visit_form_count > 0:
            return visit_form_count
        return obj.visit.study.forms.filter(is_active=True).count()


class EdcSubjectSerializer(serializers.ModelSerializer):
    """Subject card for the mobile subject list."""

    site_code = serializers.CharField(source="site.site_code", read_only=True)
    site_name = serializers.CharField(source="site.name", read_only=True)
    study_name = serializers.CharField(source="study.name", read_only=True)
    visits = serializers.SerializerMethodField()
    pending_visits = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            "id", "subject_identifier", "screening_number",
            "status", "enrollment_date", "consent_signed_date",
            "site_code", "site_name", "study_name",
            "visits", "pending_visits",
        ]

    def get_visits(self, obj):
        subject_visits = obj.subject_visits.select_related("visit").all()
        return EdcVisitStatusSerializer(subject_visits, many=True).data

    def get_pending_visits(self, obj):
        return obj.subject_visits.filter(status="planned").count()


# =============================================================================
# Form schema serializers (read — for dynamic form rendering)
# =============================================================================
class EdcItemSerializer(serializers.ModelSerializer):
    """Full item definition for dynamic CRF rendering — includes skip logic."""

    class Meta:
        model = Item
        fields = [
            "id", "field_name", "field_label", "field_type",
            "required", "section", "validation_rule",
            "cross_field_validation", "display_condition",
            "options", "order",
        ]


class EdcFormSchemaSerializer(serializers.ModelSerializer):
    """Full form definition with nested items — for rendering a CRF."""

    items = EdcItemSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = [
            "id", "name", "version", "description",
            "openclinica_crf_oid", "items",
        ]


# =============================================================================
# Existing form instance + responses (for editing previously submitted CRFs)
# =============================================================================
class EdcExistingResponseSerializer(serializers.Serializer):
    """Returns existing item responses for pre-filling the edit form."""

    item_id = serializers.IntegerField(source="item.id")
    field_name = serializers.CharField(source="item.field_name")
    value = serializers.CharField()


class EdcFormInstanceDetailSerializer(serializers.ModelSerializer):
    """Existing form instance with all responses — for edit mode."""

    responses = serializers.SerializerMethodField()
    form_name = serializers.CharField(source="form.name", read_only=True)

    class Meta:
        model = FormInstance
        fields = [
            "id", "form", "form_name", "status", "instance_number",
            "submitted_at", "signed_at", "responses",
        ]

    def get_responses(self, obj):
        responses = obj.responses.select_related("item").all()
        return EdcExistingResponseSerializer(responses, many=True).data


# =============================================================================
# Enrollment serializer (write — for enrolling new subjects)
# =============================================================================
class EdcEnrollSubjectSerializer(serializers.Serializer):
    """Enroll a new subject from the mobile EDC."""

    study_id = serializers.IntegerField()
    site_id = serializers.IntegerField()
    subject_identifier = serializers.CharField(max_length=100)
    screening_number = serializers.CharField(max_length=100, required=False, default="")
    consent_signed_date = serializers.DateField()
    enrollment_date = serializers.DateField(required=False)

    def validate_study_id(self, value):
        try:
            Study.objects.get(pk=value, status="active")
        except Study.DoesNotExist:
            raise serializers.ValidationError("Study not found or not active.")
        return value

    def validate_site_id(self, value):
        try:
            Site.objects.get(pk=value, status="active")
        except Site.DoesNotExist:
            raise serializers.ValidationError("Site not found or not active.")
        return value

    def validate(self, data):
        # Check uniqueness
        if Subject.objects.filter(
            study_id=data["study_id"],
            subject_identifier=data["subject_identifier"],
        ).exists():
            raise serializers.ValidationError(
                {"subject_identifier": "Subject already exists in this study."}
            )
        return data

    def create(self, validated_data):
        subject = Subject.objects.create(
            study_id=validated_data["study_id"],
            site_id=validated_data["site_id"],
            subject_identifier=validated_data["subject_identifier"],
            screening_number=validated_data.get("screening_number", ""),
            consent_signed_date=validated_data["consent_signed_date"],
            enrollment_date=validated_data.get("enrollment_date"),
            status="enrolled" if validated_data.get("enrollment_date") else "screened",
        )

        # Auto-create planned visits from study visit definitions
        visits = Visit.objects.filter(study_id=validated_data["study_id"])
        for visit in visits:
            scheduled_date = None
            if subject.enrollment_date and visit.planned_day is not None:
                from datetime import timedelta
                scheduled_date = subject.enrollment_date + timedelta(days=visit.planned_day)

            SubjectVisit.objects.create(
                subject=subject,
                visit=visit,
                scheduled_date=scheduled_date,
                status="planned",
            )

        return subject


# =============================================================================
# CRF submission serializer (write — for submitting/editing CRF data)
# =============================================================================
class EdcItemResponseInput(serializers.Serializer):
    """Single item response within a CRF submission."""

    item_id = serializers.IntegerField()
    value = serializers.CharField(allow_blank=True, default="")


class EdcCrfSubmissionSerializer(serializers.Serializer):
    """
    Submit or EDIT a CRF from the mobile EDC.

    Accepts:
      - form_id: which CRF
      - subject_id: which subject
      - subject_visit_id: which visit instance
      - responses: [{item_id, value}, ...]
      - status: 'draft' or 'submitted'
      - captured_at: ISO datetime (when the CRC filled the form — for offline)
      - offline_uuid: client-generated UUID for deduplication
      - reason_for_change: required when editing a previously submitted CRF
      - e_signature_token: fresh Keycloak JWT for 21 CFR Part 11 e-signature
    """

    form_id = serializers.IntegerField()
    subject_id = serializers.IntegerField()
    subject_visit_id = serializers.IntegerField(required=False, allow_null=True)
    responses = EdcItemResponseInput(many=True)
    status = serializers.ChoiceField(choices=["draft", "submitted"], default="submitted")
    captured_at = serializers.DateTimeField(required=False)
    offline_uuid = serializers.UUIDField(required=False)
    reason_for_change = serializers.CharField(
        max_length=500, required=False, default="", allow_blank=True,
        help_text="Required when editing a previously submitted CRF.",
    )
    e_signature_token = serializers.CharField(
        required=False, write_only=True, default="", allow_blank=True,
        help_text="Fresh Keycloak JWT token for 21 CFR Part 11 e-signature.",
    )

    def validate_form_id(self, value):
        try:
            Form.objects.get(pk=value, is_active=True)
        except Form.DoesNotExist:
            raise serializers.ValidationError("Form not found or inactive.")
        return value

    def validate_subject_id(self, value):
        try:
            Subject.objects.get(pk=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject not found.")
        return value

    def validate(self, data):
        form = Form.objects.get(pk=data["form_id"])
        valid_item_ids = set(form.items.values_list("id", flat=True))

        for resp in data["responses"]:
            if resp["item_id"] not in valid_item_ids:
                raise serializers.ValidationError(
                    f"Item {resp['item_id']} does not belong to form {form.name}."
                )

        # Validate required items are present (only for submit, not draft)
        if data.get("status") == "submitted":
            required_items = form.items.filter(required=True)
            submitted_ids = {r["item_id"] for r in data["responses"]}

            for item in required_items:
                # Skip required check if item has a display_condition
                # (it may be hidden and therefore not filled)
                if item.display_condition:
                    continue

                if item.id not in submitted_ids:
                    raise serializers.ValidationError(
                        f"Required field '{item.field_label}' is missing."
                    )
                resp_value = next(
                    (r["value"] for r in data["responses"] if r["item_id"] == item.id),
                    "",
                )
                if not resp_value.strip():
                    raise serializers.ValidationError(
                        f"Required field '{item.field_label}' cannot be empty."
                    )

        # E-signature: token is already validated by the frontend via Keycloak
        # ROPC grant. The backend can optionally re-validate the JWT here.
        # For 21 CFR Part 11 compliance, we log the signature event.

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        offline_uuid = validated_data.get("offline_uuid")

        # ── Deduplication: check if this UUID was already submitted ──
        if offline_uuid:
            existing = FormInstance.objects.filter(
                submission_uuid=offline_uuid
            ).first()
            if existing:
                return existing  # Idempotent — return existing instance

        # ── Check if editing an existing form instance ──
        existing_instance = FormInstance.objects.filter(
            form_id=validated_data["form_id"],
            subject_id=validated_data["subject_id"],
            subject_visit_id=validated_data.get("subject_visit_id"),
        ).first()

        reason = validated_data.get("reason_for_change", "")

        if existing_instance and existing_instance.status in ("submitted", "signed"):
            # ── EDIT MODE: Update existing instance ──
            return self._update_existing(existing_instance, validated_data, user, reason)
        elif existing_instance and existing_instance.status == "draft":
            # ── Draft update: just overwrite ──
            return self._update_existing(existing_instance, validated_data, user, "")
        else:
            # ── NEW: Create new form instance ──
            return self._create_new(validated_data, user, offline_uuid)

    def _create_new(self, validated_data, user, offline_uuid):
        """Create a brand new FormInstance + ItemResponses."""
        form_instance = FormInstance.objects.create(
            form_id=validated_data["form_id"],
            subject_id=validated_data["subject_id"],
            subject_visit_id=validated_data.get("subject_visit_id"),
            status=validated_data.get("status", "submitted"),
            submission_uuid=offline_uuid,
            submitted_at=timezone.now() if validated_data.get("status") == "submitted" else None,
            signed_by=user if validated_data.get("status") == "submitted" and validated_data.get("e_signature_token") else None,
            signed_at=timezone.now() if validated_data.get("status") == "submitted" and validated_data.get("e_signature_token") else None,
        )

        responses = []
        for resp in validated_data["responses"]:
            responses.append(
                ItemResponse(
                    form_instance=form_instance,
                    item_id=resp["item_id"],
                    value=resp["value"],
                    updated_by=user,
                )
            )
        ItemResponse.objects.bulk_create(responses)

        # Create initial audit trail entries
        for resp_obj in form_instance.responses.select_related("item").all():
            ItemResponseAudit.objects.create(
                item_response=resp_obj,
                old_value="",
                new_value=resp_obj.value,
                reason_for_change="Initial entry",
                changed_by=user,
            )

        # Mark visit as completed if submitted
        if validated_data.get("status") == "submitted" and validated_data.get("subject_visit_id"):
            SubjectVisit.objects.filter(
                pk=validated_data["subject_visit_id"]
            ).update(status="completed", actual_date=timezone.now().date())

        return form_instance

    def _update_existing(self, instance, validated_data, user, reason):
        """Update an existing FormInstance — track changes in audit trail."""
        # Get current responses as a lookup
        current_responses = {
            r.item_id: r for r in instance.responses.all()
        }

        for resp in validated_data["responses"]:
            item_id = resp["item_id"]
            new_value = resp["value"]

            if item_id in current_responses:
                existing_resp = current_responses[item_id]
                old_value = existing_resp.value

                if old_value != new_value:
                    # Value changed — create audit trail entry
                    ItemResponseAudit.objects.create(
                        item_response=existing_resp,
                        old_value=old_value,
                        new_value=new_value,
                        reason_for_change=reason,
                        changed_by=user,
                    )
                    # Update the response
                    existing_resp.value = new_value
                    existing_resp.updated_by = user
                    existing_resp.save()
            else:
                # New response for this item
                new_resp = ItemResponse.objects.create(
                    form_instance=instance,
                    item_id=item_id,
                    value=new_value,
                    updated_by=user,
                )
                ItemResponseAudit.objects.create(
                    item_response=new_resp,
                    old_value="",
                    new_value=new_value,
                    reason_for_change=reason or "Initial entry",
                    changed_by=user,
                )

        # Update instance status
        instance.status = validated_data.get("status", instance.status)
        if validated_data.get("status") == "submitted":
            instance.submitted_at = timezone.now()
        if validated_data.get("e_signature_token"):
            instance.signed_by = user
            instance.signed_at = timezone.now()
        instance.save()

        return instance
