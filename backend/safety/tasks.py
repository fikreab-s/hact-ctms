"""
Safety Tasks — Celery Beat periodic tasks for pharmacovigilance.
================================================================
- check_sae_reporting_deadlines: Monitors SAE expedited reporting timelines
  and sends email notifications at 50% and 90% of the deadline.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger("safety.tasks")


@shared_task(name="safety.check_sae_reporting_deadlines")
def check_sae_reporting_deadlines():
    """Check all pending SAE reporting deadlines and send notifications.

    ICH-GCP E6(R2) / FDA 21 CFR 312.32 requires:
    - Fatal/life-threatening SAE → report within 7 calendar days
    - All other SAEs → report within 15 calendar days

    This task runs every 6 hours and:
    1. At 50% elapsed → sends WARNING email to safety officers
    2. At 90% elapsed → sends URGENT email to safety officers
    3. Past deadline → marks as OVERDUE + sends OVERDUE alert
    """
    from safety.models import AdverseEvent
    from accounts.models import User, UserRole

    pending_saes = AdverseEvent.objects.filter(
        serious=True,
        reporting_status="pending",
        reporting_deadline__isnull=False,
    )

    if not pending_saes.exists():
        logger.info("[SAE Deadlines] No pending SAE deadlines to check.")
        return "No pending SAEs"

    # Get safety officer emails
    safety_officer_ids = UserRole.objects.filter(
        role__name="safety_officer"
    ).values_list("user_id", flat=True)
    safety_emails = list(
        User.objects.filter(
            id__in=safety_officer_ids, email__isnull=False
        ).exclude(email="").values_list("email", flat=True)
    )

    # Fallback: also include admin users
    admin_emails = list(
        User.objects.filter(
            is_superuser=True, email__isnull=False
        ).exclude(email="").values_list("email", flat=True)
    )
    recipient_emails = list(set(safety_emails + admin_emails))

    if not recipient_emails:
        logger.warning("[SAE Deadlines] No safety officers or admins with email found.")
        recipient_emails = []  # Will still log but not send

    now = timezone.now()
    notifications_sent = 0
    overdue_count = 0

    for sae in pending_saes:
        pct = sae.deadline_percent_elapsed
        days_remaining = sae.deadline_days_remaining

        if pct is None:
            continue

        subject_id = sae.subject.subject_identifier if sae.subject else "Unknown"
        study_name = sae.study.name if sae.study else "Unknown"

        # ── OVERDUE: Past 100% ──
        if pct >= 100:
            sae.reporting_status = "overdue"
            sae.save(update_fields=["reporting_status"])
            overdue_count += 1

            _send_sae_notification(
                level="OVERDUE",
                sae=sae,
                subject_id=subject_id,
                study_name=study_name,
                days_remaining=days_remaining,
                recipients=recipient_emails,
            )
            notifications_sent += 1
            logger.warning(
                f"[SAE Deadlines] OVERDUE: AE-{sae.pk} ({sae.ae_term[:40]}) "
                f"for {subject_id} — deadline was {sae.reporting_deadline}"
            )

        # ── 90% threshold ──
        elif pct >= 90 and not sae.notified_at_90_pct:
            sae.notified_at_90_pct = True
            sae.save(update_fields=["notified_at_90_pct"])

            _send_sae_notification(
                level="URGENT",
                sae=sae,
                subject_id=subject_id,
                study_name=study_name,
                days_remaining=days_remaining,
                recipients=recipient_emails,
            )
            notifications_sent += 1
            logger.info(
                f"[SAE Deadlines] URGENT (90%): AE-{sae.pk} — "
                f"{days_remaining} days remaining"
            )

        # ── 50% threshold ──
        elif pct >= 50 and not sae.notified_at_50_pct:
            sae.notified_at_50_pct = True
            sae.save(update_fields=["notified_at_50_pct"])

            _send_sae_notification(
                level="WARNING",
                sae=sae,
                subject_id=subject_id,
                study_name=study_name,
                days_remaining=days_remaining,
                recipients=recipient_emails,
            )
            notifications_sent += 1
            logger.info(
                f"[SAE Deadlines] WARNING (50%): AE-{sae.pk} — "
                f"{days_remaining} days remaining"
            )

    result = (
        f"Checked {pending_saes.count()} pending SAEs. "
        f"Notifications sent: {notifications_sent}. "
        f"Overdue: {overdue_count}."
    )
    logger.info(f"[SAE Deadlines] {result}")
    return result


def _send_sae_notification(level, sae, subject_id, study_name, days_remaining, recipients):
    """Send an SAE deadline notification email.

    Args:
        level: 'WARNING', 'URGENT', or 'OVERDUE'
        sae: AdverseEvent instance
        subject_id: Subject identifier string
        study_name: Study name string
        days_remaining: Days remaining (negative = overdue)
        recipients: List of email addresses
    """
    emoji = {"WARNING": "⚠️", "URGENT": "🚨", "OVERDUE": "❌"}.get(level, "ℹ️")
    deadline_str = sae.reporting_deadline.strftime("%Y-%m-%d %H:%M UTC") if sae.reporting_deadline else "N/A"

    if days_remaining is not None and days_remaining < 0:
        time_str = f"{abs(days_remaining):.1f} days OVERDUE"
    elif days_remaining is not None:
        time_str = f"{days_remaining:.1f} days remaining"
    else:
        time_str = "Unknown"

    subject_line = f"{emoji} [{level}] SAE Reporting Deadline — AE-{sae.pk} ({subject_id})"

    body = f"""
{level}: SAE Expedited Reporting Deadline

Adverse Event: AE-{sae.pk} — {sae.ae_term}
Subject: {subject_id}
Study: {study_name}
Seriousness Criteria: {sae.serious_criteria or 'Not specified'}
Severity: {sae.get_severity_display()}

Reported At: {sae.reported_at.strftime('%Y-%m-%d %H:%M UTC') if sae.reported_at else 'N/A'}
Deadline: {deadline_str}
Time Remaining: {time_str}

{"This SAE has EXCEEDED its regulatory reporting deadline. Immediate action required." if level == "OVERDUE" else "Please ensure this SAE is reported to the regulatory authority before the deadline."}

---
HACT Clinical Trial Management System
This is an automated notification per ICH-GCP E6(R2) requirements.
""".strip()

    if recipients:
        try:
            send_mail(
                subject=subject_line,
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@hact-ctms.local"),
                recipient_list=recipients,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"[SAE Deadlines] Failed to send email: {e}")

    # Always log the notification content
    logger.info(f"[SAE Notification] {subject_line}\n{body[:200]}...")
