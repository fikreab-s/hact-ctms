"""
Django management command to test OpenClinica connectivity.
Usage: python manage.py test_openclinica
"""

from django.core.management.base import BaseCommand, CommandError

from integrations.openclinica import is_available, list_studies


class Command(BaseCommand):
    help = "Test connectivity to OpenClinica CE 3.17"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Testing OpenClinica connection..."))
        self.stdout.write(f"  URL: {__import__('os').environ.get('OPENCLINICA_URL', 'not set')}")
        self.stdout.write(f"  WS:  {__import__('os').environ.get('OPENCLINICA_WS_URL', 'not set')}")
        self.stdout.write("")

        # Health check
        if is_available():
            self.stdout.write(self.style.SUCCESS("✅ OpenClinica is REACHABLE"))
        else:
            self.stdout.write(self.style.ERROR("❌ OpenClinica is NOT reachable"))
            self.stdout.write(
                self.style.WARNING(
                    "   Hint: Start OC with 'docker compose --profile openclinica up -d'"
                )
            )
            return

        # List studies
        self.stdout.write(self.style.NOTICE("\nListing studies in OpenClinica..."))
        studies = list_studies()
        if studies:
            for s in studies:
                self.stdout.write(f"  📋 {s.get('identifier', 'N/A')}: {s.get('name', 'N/A')}")
        else:
            self.stdout.write("  No studies found (OpenClinica is empty — ready for sync)")

        self.stdout.write(self.style.SUCCESS("\n✅ OpenClinica integration test complete."))
