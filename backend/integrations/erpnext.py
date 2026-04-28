import logging
from django.conf import settings
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

# Config from settings (which pulls from .env)
ERPNEXT_URL = getattr(settings, "ERPNEXT_URL", "http://erpnext:8000")
API_KEY = getattr(settings, "ERPNEXT_API_KEY", "")
API_SECRET = getattr(settings, "ERPNEXT_API_SECRET", "")
ERPNEXT_SITE_NAME = "hact.localhost"


def get_headers():
    """Return headers required for all Frappe/ERPNext API calls."""
    return {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "X-Frappe-Site-Name": ERPNEXT_SITE_NAME,
        "Content-Type": "application/json",
    }


def check_availability() -> bool:
    """Check if ERPNext API is available and credentials are valid."""
    if not API_KEY or not API_SECRET:
        logger.warning("ERPNext API key/secret not configured in .env")
        return False

    try:
        response = requests.get(
            f"{ERPNEXT_URL}/api/method/ping",
            headers=get_headers(),
            timeout=10,
        )
        if response.status_code == 200:
            logger.info("ERPNext is reachable (status=200)")
            return True
        else:
            logger.warning("ERPNext responded with status %s: %s", response.status_code, response.text[:200])
            return False
    except RequestException as e:
        logger.error("ERPNext connection failed: %s", str(e))
        return False


def sync_site_to_customer(site_data: dict) -> str:
    """
    Sync a Django Site to an ERPNext Customer.
    Returns the ERPNext Customer name (ID).
    """
    try:
        payload = {
            "customer_name": site_data.get("name"),
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": "All Territories",
        }

        response = requests.post(
            f"{ERPNEXT_URL}/api/resource/Customer",
            json=payload,
            headers=get_headers(),
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("name")

    except RequestException as e:
        logger.error(f"Failed to sync site to ERPNext: {str(e)}")
        raise
