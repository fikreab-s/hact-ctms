"""
HACT CTMS — SENAITE LIMS Integration Client
=============================================
REST client for the SENAITE JSON API (@@API/senaite/v1/).
Handles sample creation, result fetching, and health checks.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

logger = logging.getLogger("hact.integrations.senaite")

# Config from settings (which pulls from .env)
SENAITE_URL = getattr(settings, "SENAITE_URL", "http://senaite:8080")
SENAITE_USER = getattr(settings, "SENAITE_API_USER", "")
SENAITE_PASSWORD = getattr(settings, "SENAITE_API_PASSWORD", "")

API_BASE = f"{SENAITE_URL}/@@API/senaite/v1"


def _auth():
    """Return HTTP Basic Auth for SENAITE API calls."""
    return HTTPBasicAuth(SENAITE_USER, SENAITE_PASSWORD)


def check_availability() -> bool:
    """Check if SENAITE API is available and credentials are valid."""
    if not SENAITE_USER or not SENAITE_PASSWORD:
        logger.warning("SENAITE API user/password not configured in .env")
        return False

    try:
        response = requests.get(
            f"{API_BASE}/",
            auth=_auth(),
            timeout=10,
        )
        if response.status_code == 200:
            logger.info("SENAITE is reachable (status=200)")
            return True
        else:
            logger.warning(
                "SENAITE responded with status %s: %s",
                response.status_code,
                response.text[:200],
            )
            return False
    except RequestException as e:
        logger.error("SENAITE connection failed: %s", str(e))
        return False


def create_sample(sample_data: dict) -> dict:
    """
    Create an AnalysisRequest (sample) in SENAITE.

    Args:
        sample_data: dict with keys:
            - client_title: str (SENAITE Client name)
            - sample_type: str (e.g., 'Blood', 'Urine')
            - contact_name: str (lab contact)
            - subject_identifier: str (patient/subject ID)
            - analyses: list of analysis service titles

    Returns:
        dict with 'success', 'senaite_id', 'url' keys
    """
    try:
        # First, find the Client UID
        client_resp = requests.get(
            f"{API_BASE}/Client",
            params={"title": sample_data.get("client_title", "HACT Clinical Trials")},
            auth=_auth(),
            timeout=10,
        )
        client_resp.raise_for_status()
        clients = client_resp.json().get("items", [])

        if not clients:
            logger.error("No SENAITE Client found with title: %s", sample_data.get("client_title"))
            return {"success": False, "error": "Client not found in SENAITE"}

        client_uid = clients[0].get("uid")

        # Find SampleType UID
        st_resp = requests.get(
            f"{API_BASE}/SampleType",
            params={"title": sample_data.get("sample_type", "Blood")},
            auth=_auth(),
            timeout=10,
        )
        st_resp.raise_for_status()
        sample_types = st_resp.json().get("items", [])

        if not sample_types:
            logger.error("SampleType not found: %s", sample_data.get("sample_type"))
            return {"success": False, "error": "SampleType not found in SENAITE"}

        sample_type_uid = sample_types[0].get("uid")

        # Create the AnalysisRequest
        payload = {
            "Client": client_uid,
            "SampleType": sample_type_uid,
            "ClientSampleID": sample_data.get("subject_identifier", ""),
            "Contact": sample_data.get("contact_name", ""),
        }

        create_resp = requests.post(
            f"{API_BASE}/AnalysisRequest",
            json=payload,
            auth=_auth(),
            timeout=15,
        )
        create_resp.raise_for_status()

        result = create_resp.json()
        items = result.get("items", [])

        if items:
            senaite_id = items[0].get("id", "")
            logger.info("Sample created in SENAITE: %s", senaite_id)
            return {
                "success": True,
                "senaite_id": senaite_id,
                "uid": items[0].get("uid", ""),
                "url": items[0].get("url", ""),
            }
        else:
            return {"success": False, "error": "No items returned from SENAITE"}

    except RequestException as e:
        logger.error("Failed to create sample in SENAITE: %s", str(e))
        return {"success": False, "error": str(e)}


def fetch_published_results(client_title: str = None, limit: int = 50) -> list:
    """
    Fetch published/verified analysis results from SENAITE.

    Args:
        client_title: Optional filter by SENAITE Client name
        limit: Max number of results to fetch

    Returns:
        List of dicts with analysis result data
    """
    try:
        params = {
            "portal_type": "AnalysisRequest",
            "review_state": "published",
            "sort_on": "created",
            "sort_order": "descending",
            "limit": limit,
            "complete": "yes",
        }
        if client_title:
            params["getClientTitle"] = client_title

        response = requests.get(
            f"{API_BASE}/search",
            params=params,
            auth=_auth(),
            timeout=15,
        )
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        results = []
        for item in items:
            # Extract analyses (individual test results) from the sample
            analyses = item.get("Analyses", [])
            client_sample_id = item.get("ClientSampleID", "")
            sample_id = item.get("id", "")

            for analysis in analyses:
                if isinstance(analysis, dict):
                    results.append({
                        "senaite_sample_id": sample_id,
                        "subject_identifier": client_sample_id,
                        "test_name": analysis.get("title", analysis.get("id", "")),
                        "result_value": str(analysis.get("Result", "")),
                        "unit": analysis.get("Unit", ""),
                        "result_date": item.get("DatePublished", item.get("created", "")),
                    })

        logger.info("Fetched %d results from SENAITE", len(results))
        return results

    except RequestException as e:
        logger.error("Failed to fetch results from SENAITE: %s", str(e))
        return []


def fetch_sample_status(senaite_sample_id: str) -> dict:
    """
    Get the current status of a sample in SENAITE.

    Args:
        senaite_sample_id: The SENAITE sample ID

    Returns:
        dict with 'status', 'review_state' keys
    """
    try:
        response = requests.get(
            f"{API_BASE}/AnalysisRequest",
            params={"id": senaite_sample_id, "complete": "yes"},
            auth=_auth(),
            timeout=10,
        )
        response.raise_for_status()

        items = response.json().get("items", [])
        if items:
            return {
                "found": True,
                "status": items[0].get("review_state", "unknown"),
                "title": items[0].get("title", ""),
                "sample_type": items[0].get("SampleTypeTitle", ""),
            }
        return {"found": False}

    except RequestException as e:
        logger.error("Failed to fetch sample status from SENAITE: %s", str(e))
        return {"found": False, "error": str(e)}
