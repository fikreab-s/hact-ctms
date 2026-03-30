"""
Clinical Models — clinical schema
=====================================
Tables: Study, Site, Subject, Visit, SubjectVisit,
        Form, Item, FormInstance, ItemResponse, Query

This is the core of the CTMS — study setup, data collection, and query management.
"""

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


# =============================================================================
# Study — Clinical study/trial metadata
# =============================================================================
class Study(TimeStampedModel):
    """Top-level clinical study/trial entity.

    All data in the system ultimately belongs to a study.
    """

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("active", "Active"),
        ("locked", "Locked"),
        ("archived", "Archived"),
    ]

    PHASE_CHOICES = [
        ("I", "Phase I"),
        ("II", "Phase II"),
        ("III", "Phase III"),
        ("IV", "Phase IV"),
        ("I/II", "Phase I/II"),
        ("II/III", "Phase II/III"),
        ("NA", "Not Applicable"),
    ]

    name = models.CharField(max_length=255)
    protocol_number = models.CharField(max_length=100, unique=True, db_index=True)
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, blank=True, default="")
    sponsor = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        db_index=True,
    )

    # Integration: OpenClinica
    openclinica_study_oid = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="OpenClinica Study OID (if using OC as complementary EDC).",
    )

    class Meta:
        db_table = "clinical_studies"
        verbose_name = "Study"
        verbose_name_plural = "Studies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.protocol_number} — {self.name}"


# =============================================================================
# Site — Participating clinical sites
# =============================================================================
class Site(TimeStampedModel):
    """A participating site within a study.

    Sites host subjects and have associated staff, contracts, and milestones.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("closed", "Closed"),
        ("suspended", "Suspended"),
    ]

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="sites",
    )
    site_code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, default="")
    country = models.CharField(max_length=100, default="Ethiopia")
    principal_investigator = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    activation_date = models.DateField(null=True, blank=True)

    # Integration: ERPNext
    erpnext_site_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="ERPNext site identifier for operational sync.",
    )

    class Meta:
        db_table = "clinical_sites"
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        unique_together = [("study", "site_code")]
        ordering = ["site_code"]

    def __str__(self):
        return f"{self.site_code} — {self.name}"


# =============================================================================
# Subject — Enrolled trial subjects
# =============================================================================
class Subject(TimeStampedModel):
    """A subject/participant enrolled in a clinical study at a specific site."""

    STATUS_CHOICES = [
        ("screened", "Screened"),
        ("enrolled", "Enrolled"),
        ("completed", "Completed"),
        ("discontinued", "Discontinued"),
        ("screen_failed", "Screen Failed"),
    ]

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    subject_identifier = models.CharField(max_length=100, db_index=True)
    screening_number = models.CharField(max_length=100, blank=True, default="")
    enrollment_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="screened",
        db_index=True,
    )
    consent_signed_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "clinical_subjects"
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        unique_together = [("study", "subject_identifier")]
        ordering = ["subject_identifier"]

    def __str__(self):
        return f"{self.subject_identifier} ({self.get_status_display()})"


# =============================================================================
# Visit — Visit definitions per study (schedule template)
# =============================================================================
class Visit(TimeStampedModel):
    """Visit definition within a study protocol.

    Defines the planned visit schedule — each subject will get
    SubjectVisit instances based on these templates.
    """

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="visits",
    )
    visit_name = models.CharField(max_length=255)
    visit_order = models.PositiveIntegerField(
        help_text="Order of this visit in the study schedule."
    )
    planned_day = models.IntegerField(
        default=0,
        help_text="Planned day relative to baseline (Day 0).",
    )
    window_before = models.PositiveIntegerField(
        default=2,
        help_text="Days before planned_day that the visit is allowed.",
    )
    window_after = models.PositiveIntegerField(
        default=2,
        help_text="Days after planned_day that the visit is allowed.",
    )
    is_screening = models.BooleanField(default=False)
    is_baseline = models.BooleanField(default=False)
    is_follow_up = models.BooleanField(default=False)

    # Integration: OpenClinica
    openclinica_event_definition_oid = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="OpenClinica Event Definition OID.",
    )

    class Meta:
        db_table = "clinical_visits"
        verbose_name = "Visit Definition"
        verbose_name_plural = "Visit Definitions"
        unique_together = [("study", "visit_order")]
        ordering = ["visit_order"]

    def __str__(self):
        return f"{self.visit_name} (Day {self.planned_day})"

    def get_window_range(self, baseline_date):
        """Return (earliest_date, latest_date) for this visit window.

        Args:
            baseline_date: The subject's baseline/enrollment date (Day 0).

        Returns:
            Tuple of (earliest_date, latest_date) as datetime.date objects.
        """
        from datetime import timedelta

        target_date = baseline_date + timedelta(days=self.planned_day)
        earliest = target_date - timedelta(days=self.window_before)
        latest = target_date + timedelta(days=self.window_after)
        return earliest, latest


# =============================================================================
# SubjectVisit — Subject-specific visit schedule (actual dates)
# =============================================================================
class SubjectVisit(TimeStampedModel):
    """A specific subject's scheduled/actual visit.

    Links a Subject to a Visit definition with actual dates and status.
    """

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("completed", "Completed"),
        ("missed", "Missed"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_visits",
    )
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="subject_visits",
    )
    scheduled_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        db_index=True,
    )

    class Meta:
        db_table = "clinical_subject_visits"
        verbose_name = "Subject Visit"
        verbose_name_plural = "Subject Visits"
        unique_together = [("subject", "visit")]
        ordering = ["visit__visit_order"]

    def __str__(self):
        return f"{self.subject.subject_identifier} → {self.visit.visit_name}"


# =============================================================================
# Form — Case Report Form (CRF) definitions
# =============================================================================
class Form(TimeStampedModel):
    """CRF (Case Report Form) definition within a study.

    A form is a collection of items (fields) that capture clinical data.
    """

    study = models.ForeignKey(
        Study,
        on_delete=models.CASCADE,
        related_name="forms",
    )
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=20, default="1.0")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    # Integration: OpenClinica
    openclinica_crf_oid = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="OpenClinica CRF OID.",
    )

    class Meta:
        db_table = "clinical_forms"
        verbose_name = "Form (CRF)"
        verbose_name_plural = "Forms (CRFs)"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} v{self.version}"


# =============================================================================
# Item — Individual form fields (questions/data points)
# =============================================================================
class Item(TimeStampedModel):
    """An individual form field/question within a CRF.

    Defines the data point structure — field_type, validation rules,
    and JSONB options for dropdowns/radio/checkboxes.
    """

    FIELD_TYPE_CHOICES = [
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("datetime", "DateTime"),
        ("dropdown", "Dropdown"),
        ("radio", "Radio"),
        ("checkbox", "Checkbox"),
        ("textarea", "Textarea"),
        ("file", "File Upload"),
    ]

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="items",
    )
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=500)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default="text")
    required = models.BooleanField(default=False)
    validation_rule = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Regex or custom validation rule.",
    )
    options = models.JSONField(
        null=True,
        blank=True,
        help_text="JSONB — dropdown/radio/checkbox options, e.g. [{\"value\": \"1\", \"label\": \"Yes\"}].",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "clinical_items"
        verbose_name = "Form Item (Field)"
        verbose_name_plural = "Form Items (Fields)"
        unique_together = [("form", "field_name")]
        ordering = ["order"]

    def __str__(self):
        return f"{self.field_name} ({self.field_type})"


# =============================================================================
# FormInstance — A filled/submitted CRF for a subject
# =============================================================================
class FormInstance(TimeStampedModel):
    """An instance of a filled CRF for a specific subject and optional visit.

    Tracks the form submission workflow: draft → submitted → signed → locked.
    Supports 21 CFR Part 11 electronic signature compliance.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("signed", "Signed"),
        ("locked", "Locked"),
    ]

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="instances",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="form_instances",
    )
    subject_visit = models.ForeignKey(
        SubjectVisit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="form_instances",
    )
    instance_number = models.PositiveIntegerField(
        default=1,
        help_text="For repeating forms — instance number.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_form_instances",
    )
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clinical_form_instances"
        verbose_name = "Form Instance"
        verbose_name_plural = "Form Instances"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.form.name} — {self.subject.subject_identifier} (#{self.instance_number})"


# =============================================================================
# ItemResponse — Data values entered for each CRF item
# =============================================================================
class ItemResponse(models.Model):
    """Value entered for a specific item within a form instance.

    Stores all clinical data as text — typed validation happens
    at the item/form level. Includes its own updated_at/updated_by
    for field-level audit compliance.
    """

    form_instance = models.ForeignKey(
        FormInstance,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    value = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="item_responses",
    )

    class Meta:
        db_table = "clinical_item_responses"
        verbose_name = "Item Response"
        verbose_name_plural = "Item Responses"
        unique_together = [("form_instance", "item")]

    def __str__(self):
        return f"{self.item.field_name} = {self.value[:50]}"


# =============================================================================
# Query — Data discrepancy queries for data cleaning
# =============================================================================
class Query(TimeStampedModel):
    """Data query/discrepancy raised against an item response.

    Supports the clinical data cleaning process:
    open → answered → closed.
    """

    STATUS_CHOICES = [
        ("open", "Open"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    ]

    item_response = models.ForeignKey(
        ItemResponse,
        on_delete=models.CASCADE,
        related_name="queries",
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="queries_raised",
    )
    raised_at = models.DateTimeField(auto_now_add=True)
    query_text = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        db_index=True,
    )
    response_text = models.TextField(blank=True, default="")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="queries_resolved",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clinical_queries"
        verbose_name = "Data Query"
        verbose_name_plural = "Data Queries"
        ordering = ["-raised_at"]

    def __str__(self):
        return f"Q-{self.pk}: {self.query_text[:60]}..."
