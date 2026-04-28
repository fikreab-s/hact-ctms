import logging
import json
from django.core.management.base import BaseCommand
from integrations.erpnext import check_availability, sync_site_to_customer
from clinical.models import Site
from django.test import RequestFactory
from integrations.views import erpnext_webhook

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Test ERPNext connectivity and integrations"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Testing ERPNext connection..."))
        
        is_up = check_availability()
        if not is_up:
            self.stdout.write(self.style.ERROR("❌ ERPNext is UNREACHABLE or invalid credentials."))
            self.stdout.write(self.style.WARNING("  ⚠️ Continuing to test Webhook logic anyway..."))
        else:
            self.stdout.write(self.style.SUCCESS("✅ ERPNext is REACHABLE"))
        
        # Test Webhook
        self.stdout.write(self.style.SUCCESS("\nTesting Contract Signed Webhook..."))
        
        from clinical.models import Study
        study, _ = Study.objects.get_or_create(
            protocol_number="HACT-ERP-TEST",
            defaults={"name": "ERPNext Test Study", "phase": "II"}
        )
        
        # Create a test site
        site, created = Site.objects.get_or_create(
            site_code="TEST-ERP",
            defaults={"name": "ERPNext Test Site", "status": "planned", "study": study}
        )
        if created:
            self.stdout.write(f"  Created test site: {site.name}")
            
        # Give it an ERPNext ID directly for the webhook test
        site.erpnext_site_id = "Customer-ERP-Test"
        site.status = "planned"
        site.save()
        
        # Simulate webhook call
        factory = RequestFactory()
        request = factory.post(
            '/api/v1/integrations/erpnext/webhook/contract-signed/',
            data=json.dumps({
                "erpnext_site_id": "Customer-ERP-Test",
                "contract_status": "Signed"
            }),
            content_type='application/json'
        )
        
        # Bypass authentication for the local test call
        request.user = None
        
        # We need to call it without the @permission_classes decorator for this simple test,
        # or we just mock the logic. Since it's decorated, let's just check the DB logic directly.
        from rest_framework.test import APIRequestFactory, force_authenticate
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        test_user, _ = User.objects.get_or_create(username="erpnext_tester")
        
        api_factory = APIRequestFactory()
        api_request = api_factory.post(
            '/api/v1/integrations/erpnext/webhook/contract-signed/',
            {"erpnext_site_id": "Customer-ERP-Test", "contract_status": "Signed"},
            format='json'
        )
        force_authenticate(api_request, user=test_user)
        
        response = erpnext_webhook(api_request)
        
        if response.status_code == 200:
            site.refresh_from_db()
            if site.status == 'active':
                self.stdout.write(self.style.SUCCESS("✅ Webhook executed successfully. Site is now active."))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Webhook returned 200 but site status is {site.status}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Webhook failed with status {response.status_code}: {response.data}"))
            
        # Cleanup
        site.delete()
        self.stdout.write("  Test site deleted.")
        
        self.stdout.write(self.style.SUCCESS("\n✅ ERPNext integration test COMPLETE."))
