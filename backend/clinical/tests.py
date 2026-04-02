"""
Clinical Tests — Day 3 Business Logic Verification
=====================================================
Tests for:
- Study status workflow transitions
- Subject enrollment/withdrawal
- Form instance submit/sign lifecycle
- Query management lifecycle
- Visit window calculation
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from clinical.models import (
    Form,
    FormInstance,
    Item,
    ItemResponse,
    Query,
    Site,
    Study,
    Subject,
    SubjectVisit,
    Visit,
)

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common test data setup."""

    @classmethod
    def setUpTestData(cls):
        # Create user (superuser to bypass RBAC — tests focus on business logic)
        cls.user = User.objects.create_superuser(
            username="testuser",
            password="TestPass@2026!",
            email="test@hact.org",
        )

        # Create study
        cls.study = Study.objects.create(
            name="Test Study",
            protocol_number="TEST-001",
            phase="Phase III",
            sponsor="HACT Foundation",
            status="active",
            start_date=date.today() - timedelta(days=30),
        )

        # Create site
        cls.site = Site.objects.create(
            study=cls.study,
            site_code="TEST-SITE-001",
            name="Test Hospital",
            country="Ethiopia",
            status="active",
        )

        # Create visits
        cls.screening_visit = Visit.objects.create(
            study=cls.study,
            visit_name="Screening",
            visit_order=1,
            planned_day=-14,
            is_screening=True,
            window_before=14,
            window_after=0,
        )
        cls.baseline_visit = Visit.objects.create(
            study=cls.study,
            visit_name="Baseline",
            visit_order=2,
            planned_day=0,
            is_baseline=True,
            window_before=0,
            window_after=1,
        )
        cls.day7_visit = Visit.objects.create(
            study=cls.study,
            visit_name="Day 7",
            visit_order=3,
            planned_day=7,
            window_before=1,
            window_after=1,
        )

        # Create form + items
        cls.form = Form.objects.create(
            study=cls.study,
            name="Vital Signs",
            version="1.0",
            is_active=True,
        )
        cls.item_hr = Item.objects.create(
            form=cls.form,
            field_name="heart_rate",
            field_label="Heart Rate (bpm)",
            field_type="number",
            required=True,
            order=1,
        )
        cls.item_temp = Item.objects.create(
            form=cls.form,
            field_name="temperature",
            field_label="Temperature (C)",
            field_type="number",
            required=True,
            order=2,
        )
        cls.item_notes = Item.objects.create(
            form=cls.form,
            field_name="notes",
            field_label="Notes",
            field_type="text",
            required=False,
            order=3,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


# =============================================================================
# Study Workflow Tests
# =============================================================================


class StudyTransitionTests(BaseTestCase):
    """Test study status workflow transitions."""

    def test_valid_transition_planning_to_active(self):
        """Test valid transition: planning -> active."""
        study = Study.objects.create(
            name="New Study", protocol_number="NEW-001",
            phase="Phase I", status="planning",
        )
        response = self.client.post(
            f"/api/v1/clinical/studies/{study.id}/transition/",
            {"status": "active"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        study.refresh_from_db()
        self.assertEqual(study.status, "active")

    def test_invalid_transition_planning_to_locked(self):
        """Test invalid skip: planning -> locked (should fail)."""
        study = Study.objects.create(
            name="New Study 2", protocol_number="NEW-002",
            phase="Phase I", status="planning",
        )
        response = self.client.post(
            f"/api/v1/clinical/studies/{study.id}/transition/",
            {"status": "locked"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_transition_active_to_archived(self):
        """Test invalid skip: active -> archived (must go via locked)."""
        response = self.client.post(
            f"/api/v1/clinical/studies/{self.study.id}/transition/",
            {"status": "archived"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_lock_blocked_with_open_queries(self):
        """Test that locking is blocked when open queries exist."""
        subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="LOCK-TEST-001", status="enrolled",
        )
        fi = FormInstance.objects.create(
            form=self.form, subject=subject, status="submitted",
        )
        ir = ItemResponse.objects.create(
            form_instance=fi, item=self.item_hr, value="72",
        )
        Query.objects.create(
            item_response=ir, raised_by=self.user,
            query_text="Please verify", status="open",
        )

        response = self.client.post(
            f"/api/v1/clinical/studies/{self.study.id}/transition/",
            {"status": "locked"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)


# =============================================================================
# Subject Enrollment Tests
# =============================================================================


class SubjectEnrollmentTests(BaseTestCase):
    """Test subject enrollment workflow."""

    def test_enroll_screened_subject(self):
        """Test enrolling a screened subject with consent."""
        subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="ENROLL-001", status="screened",
        )
        response = self.client.post(
            f"/api/v1/clinical/subjects/{subject.id}/enroll/",
            {
                "consent_signed_date": "2026-03-25",
                "enrollment_date": "2026-03-25",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        subject.refresh_from_db()
        self.assertEqual(subject.status, "enrolled")
        self.assertEqual(str(subject.consent_signed_date), "2026-03-25")

    def test_enroll_without_consent_fails(self):
        """Test that enrollment without consent date fails."""
        subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="ENROLL-002", status="screened",
        )
        response = self.client.post(
            f"/api/v1/clinical/subjects/{subject.id}/enroll/",
            {"enrollment_date": "2026-03-25"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_enroll_already_enrolled_fails(self):
        """Test that re-enrolling an enrolled subject fails."""
        subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="ENROLL-003", status="enrolled",
            consent_signed_date=date.today(),
        )
        response = self.client.post(
            f"/api/v1/clinical/subjects/{subject.id}/enroll/",
            {"consent_signed_date": "2026-03-25"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_withdraw_enrolled_subject(self):
        """Test withdrawing an enrolled subject."""
        subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="WITHDRAW-001", status="enrolled",
            consent_signed_date=date.today(),
        )
        response = self.client.post(
            f"/api/v1/clinical/subjects/{subject.id}/withdraw/",
            {"reason": "Consent withdrawn"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        subject.refresh_from_db()
        self.assertEqual(subject.status, "discontinued")


# =============================================================================
# Form Instance Tests
# =============================================================================


class FormInstanceTests(BaseTestCase):
    """Test form instance submit/sign workflow."""

    def setUp(self):
        super().setUp()
        self.subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="FORM-001", status="enrolled",
            consent_signed_date=date.today(),
        )
        self.fi = FormInstance.objects.create(
            form=self.form, subject=self.subject, status="draft",
        )

    def test_submit_incomplete_form_fails(self):
        """Test that submitting an incomplete form fails."""
        response = self.client.post(
            f"/api/v1/clinical/form-instances/{self.fi.id}/submit/",
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_complete_form_succeeds(self):
        """Test that submitting a complete form succeeds."""
        ItemResponse.objects.create(
            form_instance=self.fi, item=self.item_hr, value="72",
        )
        ItemResponse.objects.create(
            form_instance=self.fi, item=self.item_temp, value="36.8",
        )

        response = self.client.post(
            f"/api/v1/clinical/form-instances/{self.fi.id}/submit/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.fi.refresh_from_db()
        self.assertEqual(self.fi.status, "submitted")

    def test_sign_submitted_form(self):
        """Test signing a submitted form with password."""
        self.fi.status = "submitted"
        self.fi.save()

        response = self.client.post(
            f"/api/v1/clinical/form-instances/{self.fi.id}/sign/",
            {
                "password": "TestPass@2026!",
                "meaning": "I confirm this data is accurate.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.fi.refresh_from_db()
        self.assertEqual(self.fi.status, "signed")
        self.assertEqual(self.fi.signed_by, self.user)

    def test_sign_with_wrong_password_fails(self):
        """Test that signing with wrong password fails."""
        self.fi.status = "submitted"
        self.fi.save()

        response = self.client.post(
            f"/api/v1/clinical/form-instances/{self.fi.id}/sign/",
            {
                "password": "WrongPassword!",
                "meaning": "I confirm this data is accurate.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)


# =============================================================================
# Query Lifecycle Tests
# =============================================================================


class QueryLifecycleTests(BaseTestCase):
    """Test query management lifecycle."""

    def setUp(self):
        super().setUp()
        self.subject = Subject.objects.create(
            study=self.study, site=self.site,
            subject_identifier="QUERY-001", status="enrolled",
        )
        self.fi = FormInstance.objects.create(
            form=self.form, subject=self.subject, status="submitted",
        )
        self.ir = ItemResponse.objects.create(
            form_instance=self.fi, item=self.item_hr, value="72",
        )
        self.query = Query.objects.create(
            item_response=self.ir,
            raised_by=self.user,
            query_text="Please verify heart rate.",
            status="open",
        )

    def test_answer_open_query(self):
        """Test answering an open query."""
        response = self.client.post(
            f"/api/v1/clinical/queries/{self.query.id}/answer/",
            {"response_text": "Verified. Value is correct."},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.query.refresh_from_db()
        self.assertEqual(self.query.status, "answered")
        self.assertEqual(self.query.response_text, "Verified. Value is correct.")

    def test_close_answered_query(self):
        """Test closing an answered query."""
        self.query.status = "answered"
        self.query.response_text = "Verified."
        self.query.save()

        response = self.client.post(
            f"/api/v1/clinical/queries/{self.query.id}/close/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.query.refresh_from_db()
        self.assertEqual(self.query.status, "closed")
        self.assertIsNotNone(self.query.resolved_at)

    def test_close_already_closed_query_fails(self):
        """Test closing an already-closed query fails."""
        self.query.status = "closed"
        self.query.save()

        response = self.client.post(
            f"/api/v1/clinical/queries/{self.query.id}/close/",
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_auto_generate_queries(self):
        """Test auto-generation of queries for missing required fields."""
        fi2 = FormInstance.objects.create(
            form=self.form, subject=self.subject, status="draft",
        )
        ItemResponse.objects.create(
            form_instance=fi2, item=self.item_hr, value="72",
        )

        response = self.client.post(
            f"/api/v1/clinical/form-instances/{fi2.id}/generate-queries/",
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        queries = Query.objects.filter(
            item_response__form_instance=fi2,
        )
        self.assertGreaterEqual(queries.count(), 1)


# =============================================================================
# Visit Window Tests
# =============================================================================


class VisitWindowTests(BaseTestCase):
    """Test visit window calculation logic."""

    def test_get_window_range(self):
        """Test window range calculation for Day 7 visit."""
        baseline_date = date(2026, 3, 1)
        result = self.day7_visit.get_window_range(baseline_date)
        self.assertIsNotNone(result)
        earliest, latest = result
        # Day 7 +/- 1: Day 6 to Day 8
        self.assertEqual(earliest, date(2026, 3, 7))  # baseline + 7 - 1
        self.assertEqual(latest, date(2026, 3, 9))  # baseline + 7 + 1

    def test_screening_window_range(self):
        """Test window range for screening visit (Day -14, window_before=14)."""
        baseline_date = date(2026, 3, 15)
        result = self.screening_visit.get_window_range(baseline_date)
        self.assertIsNotNone(result)
        earliest, latest = result
        self.assertEqual(earliest, date(2026, 2, 15))
        self.assertEqual(latest, date(2026, 3, 1))

    def test_within_window(self):
        """Test that a visit within window is correctly identified."""
        baseline_date = date(2026, 3, 1)
        result = self.day7_visit.get_window_range(baseline_date)
        earliest, latest = result

        visit_date = date(2026, 3, 8)  # Day 7 -- within +/-1
        self.assertTrue(earliest <= visit_date <= latest)

    def test_outside_window(self):
        """Test that a visit outside window is correctly identified."""
        baseline_date = date(2026, 3, 1)
        result = self.day7_visit.get_window_range(baseline_date)
        earliest, latest = result

        visit_date = date(2026, 3, 15)  # Day 14 -- way outside +/-1
        self.assertFalse(earliest <= visit_date <= latest)
