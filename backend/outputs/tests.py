"""
Outputs Tests — Export & Quality Report Verification
=======================================================
Tests for:
- CSV export generation
- CDISC ODM XML export
- Data quality report generation
- Study lock with auto-snapshot
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
    Visit,
)
from outputs.models import DataQualityReport, DatasetSnapshot

User = get_user_model()


class OutputsBaseTestCase(TestCase):
    """Base with test data for outputs tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username="exportuser",
            password="TestPass@2026!",
            email="export@hact.org",
        )

        cls.study = Study.objects.create(
            name="Export Test Study",
            protocol_number="EXP-001",
            phase="Phase III",
            sponsor="HACT Foundation",
            status="active",
            start_date=date.today() - timedelta(days=30),
        )

        cls.site = Site.objects.create(
            study=cls.study,
            site_code="EXP-SITE-001",
            name="Export Hospital",
            country="Ethiopia",
            status="active",
        )

        cls.visit = Visit.objects.create(
            study=cls.study,
            visit_name="Baseline",
            visit_order=1,
            planned_day=0,
            is_baseline=True,
            window_before=0,
            window_after=1,
        )

        cls.form = Form.objects.create(
            study=cls.study,
            name="Demographics",
            version="1.0",
            is_active=True,
        )
        cls.item = Item.objects.create(
            form=cls.form,
            field_name="age",
            field_label="Age (years)",
            field_type="number",
            required=True,
            order=1,
        )

        cls.subject = Subject.objects.create(
            study=cls.study, site=cls.site,
            subject_identifier="EXP-001-001",
            status="enrolled",
            consent_signed_date=date.today() - timedelta(days=10),
            enrollment_date=date.today() - timedelta(days=10),
        )

        cls.fi = FormInstance.objects.create(
            form=cls.form, subject=cls.subject, status="submitted",
        )
        cls.ir = ItemResponse.objects.create(
            form_instance=cls.fi, item=cls.item, value="35",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class CSVExportTests(OutputsBaseTestCase):
    """Test CSV export generation."""

    def test_export_csv_zip(self):
        """Test CSV ZIP export creates file and snapshot."""
        response = self.client.post(
            "/api/v1/outputs/snapshots/export-csv/",
            {"study": self.study.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("snapshot_id", response.data)
        self.assertIn("file_url", response.data)

        # Verify snapshot record created
        snapshot = DatasetSnapshot.objects.get(pk=response.data["snapshot_id"])
        self.assertEqual(snapshot.study, self.study)
        self.assertEqual(snapshot.snapshot_type, "raw")
        self.assertIn(".zip", snapshot.file_url)

    def test_export_csv_invalid_study(self):
        """Test CSV export with non-existent study."""
        response = self.client.post(
            "/api/v1/outputs/snapshots/export-csv/",
            {"study": 99999},
            format="json",
        )
        self.assertEqual(response.status_code, 404)


class ODMExportTests(OutputsBaseTestCase):
    """Test CDISC ODM XML export."""

    def test_export_odm(self):
        """Test ODM XML export creates file and snapshot."""
        response = self.client.post(
            "/api/v1/outputs/snapshots/export-odm/",
            {"study": self.study.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("snapshot_id", response.data)
        self.assertIn("file_url", response.data)

        snapshot = DatasetSnapshot.objects.get(pk=response.data["snapshot_id"])
        self.assertEqual(snapshot.snapshot_type, "SDTM")
        self.assertIn(".xml", snapshot.file_url)


class QualityReportTests(OutputsBaseTestCase):
    """Test data quality report generation."""

    def test_generate_comprehensive_report(self):
        """Test comprehensive quality report generation."""
        response = self.client.post(
            "/api/v1/outputs/quality-reports/generate/",
            {"study": self.study.id, "report_type": "comprehensive"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("report_id", response.data)
        self.assertIn("report_data", response.data)

        # Verify report structure
        report_data = response.data["report_data"]
        self.assertEqual(report_data["report_type"], "comprehensive")
        self.assertIn("sections", report_data)
        self.assertIn("summary", report_data)
        self.assertIn("missing_data", report_data["sections"])
        self.assertIn("query_status", report_data["sections"])
        self.assertIn("enrollment", report_data["sections"])

    def test_generate_missing_data_report(self):
        """Test missing data report generation."""
        response = self.client.post(
            "/api/v1/outputs/quality-reports/generate/",
            {"study": self.study.id, "report_type": "missing_data"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_generate_report_invalid_study(self):
        """Test report generation with non-existent study."""
        response = self.client.post(
            "/api/v1/outputs/quality-reports/generate/",
            {"study": 99999, "report_type": "comprehensive"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)


class StudyLockTests(OutputsBaseTestCase):
    """Test study lock auto-generates snapshot and quality report."""

    def test_lock_creates_snapshot_and_report(self):
        """Test that locking study creates snapshot + quality report + locks forms."""
        # Need no open queries for lock to succeed
        response = self.client.post(
            f"/api/v1/clinical/studies/{self.study.id}/transition/",
            {"status": "locked"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        # Verify snapshot created
        self.assertIn("snapshot_id", response.data)
        snapshot = DatasetSnapshot.objects.get(pk=response.data["snapshot_id"])
        self.assertEqual(snapshot.study, self.study)

        # Verify quality report created
        self.assertIn("quality_report_id", response.data)
        report = DataQualityReport.objects.get(pk=response.data["quality_report_id"])
        self.assertEqual(report.study, self.study)

        # Verify form instances locked
        self.assertIn("form_instances_locked", response.data)
