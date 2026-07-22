"""
Feedback — In-app user feedback (UAT).
======================================
A lightweight, first-party feedback channel so users can report bugs, ask
questions, or make suggestions from any page — optionally with a screenshot of
what they were looking at. Everything is stored in the HACT database (the
screenshot as a file in MEDIA_ROOT), so no clinical data ever leaves the
platform to a third-party feedback service.
"""

from django.conf import settings
from django.db import models


class Feedback(models.Model):
    """A single piece of user feedback, optionally with a screenshot."""

    CATEGORY_CHOICES = [
        ("bug", "Bug"),
        ("question", "Question"),
        ("suggestion", "Suggestion"),
        ("other", "Other"),
    ]
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATUS_CHOICES = [
        ("new", "New"),
        ("in_review", "In Review"),
        ("resolved", "Resolved"),
        ("wont_fix", "Won't Fix"),
    ]

    # Who submitted it (kept nullable so feedback survives user deletion).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_items",
    )
    # Snapshots so the record stays meaningful even if the user/roles change.
    username = models.CharField(max_length=150, blank=True, default="")
    roles = models.CharField(
        max_length=255, blank=True, default="",
        help_text="Comma-separated snapshot of the submitter's roles.",
    )

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="bug")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    message = models.TextField()

    # Context captured automatically by the widget.
    page_url = models.CharField(max_length=1000, blank=True, default="")
    user_agent = models.CharField(max_length=500, blank=True, default="")

    # Screenshot stored as a file (FileField, not ImageField, to avoid a hard
    # Pillow dependency). May be empty if the user opted out.
    screenshot = models.FileField(upload_to="feedback/%Y/%m/", null=True, blank=True)

    # Triage fields for the review team.
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", db_index=True
    )
    admin_notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feedback_items"
        ordering = ["-created_at"]
        verbose_name = "Feedback item"
        verbose_name_plural = "Feedback items"

    def __str__(self):
        who = self.username or (self.user_id and str(self.user_id)) or "anon"
        return f"[{self.get_category_display()}] {who}: {self.message[:50]}"
