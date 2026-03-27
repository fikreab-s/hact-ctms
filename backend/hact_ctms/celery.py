"""
HACT CTMS — Celery Application Configuration
==============================================
Auto-discovers tasks from all HACT apps.
Broker: Redis | Result Backend: Redis
"""

import os

from celery import Celery

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hact_ctms.settings")

# Create the Celery application
app = Celery("hact_ctms")

# Load config from Django settings, using the CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f"Celery debug task executed. Request: {self.request!r}")
