"""
Management command to test SENAITE LIMS integration end-to-end.

Usage:
    docker exec hact-django-api python manage.py test_senaite
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test SENAITE LIMS API connectivity, sample sync, and webhook logic."

    def handle(self, *args, **options):
        self.stdout.write("Testing SENAITE connection...")

        # ----------------------------------------------------------
        # Step 1: Test API connectivity
        # ----------------------------------------------------------
        from integrations.senaite import check_availability

        is_available = check_availability()
        if is_available:
            self.stdout.write(self.style.SUCCESS("✅ SENAITE is REACHABLE"))
        else:
            self.stdout.write(self.style.ERROR("❌ SENAITE is UNREACHABLE or invalid credentials."))
            self.stdout.write("  ⚠️ Continuing to test Webhook logic anyway...\n")

        # ----------------------------------------------------------
        # Step 2: Test Webhook (results-published)
        # ----------------------------------------------------------
        self.stdout.write("\nTesting Results Published Webhook...")

        from django.test import RequestFactory
        from django.contrib.auth import get_user_model
        from lab.models import SampleCollection
        from clinical.models import Study, Site, Subject

        User = get_user_model()

        # Get or create a test user
        user, _ = User.objects.get_or_create(
            username="senaite_test_user",
            defaults={"email": "senaite_test@hact.local", "is_active": True},
        )

        # Get or create test study/site/subject
        study, _ = Study.objects.get_or_create(
            protocol_number="SENAITE-TEST-001",
            defaults={
                "name": "SENAITE Test Study",
                "phase": "Phase I",
                "status": "active",
            },
        )

        site, _ = Site.objects.get_or_create(
            name="SENAITE Test Site",
            study=study,
            defaults={
                "site_code": "STEST-01",
                "status": "active",
            },
        )

        subject, _ = Subject.objects.get_or_create(
            subject_identifier="SENAITE-SUBJ-001",
            study=study,
            defaults={
                "site": site,
                "status": "enrolled",
            },
        )

        # Create a test sample
        sample = SampleCollection.objects.create(
            subject=subject,
            senaite_sample_id="TEST-SENAITE-001",
            collection_date="2026-05-01",
            sample_type="Blood",
            status="collected",
        )
        self.stdout.write(f"  Created test sample: {sample.senaite_sample_id}")

        # Simulate the webhook
        from integrations.views import senaite_webhook

        factory = RequestFactory()
        request = factory.post(
            "/api/v1/integrations/senaite/webhook/results-published/",
            data={
                "senaite_sample_id": "TEST-SENAITE-001",
                "status": "published",
            },
            content_type="application/json",
        )
        request.user = user
        # Bypass CSRF for test
        request.META["HTTP_X_CSRFTOKEN"] = "test"
        request._dont_enforce_csrf_checks = True

        response = senaite_webhook(request)

        if response.status_code == 200:
            # Verify the sample was updated
            sample.refresh_from_db()
            if sample.status == "completed":
                self.stdout.write(self.style.SUCCESS("✅ Webhook executed successfully. Sample is now completed."))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sample status is '{sample.status}', expected 'completed'."))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Webhook returned {response.status_code}: {response.data}"))

        # Cleanup
        sample.delete()
        subject.delete()
        site.delete()
        study.delete()
        user.delete()
        self.stdout.write("  Test data cleaned up.")

        self.stdout.write(self.style.SUCCESS("\n✅ SENAITE integration test COMPLETE."))
