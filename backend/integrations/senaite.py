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
# Plone site id that SENAITE lives under (public URL is https://.../senaite/...).
SENAITE_SITE_ID = getattr(settings, "SENAITE_SITE_ID", "senaite")


def _api_base(url: str, site_id: str) -> str:
    """
    Build the SENAITE JSON API base.

    The REST API lives *inside* the Plone site, at ``<host>/<site_id>/@@API/...``.
    If ``SENAITE_URL`` is configured as a bare host (e.g. ``http://senaite:8080``)
    with no path, we append the site id — otherwise a search hits Zope's root
    catalog and silently returns zero items (while ``/@@API/senaite/v1/`` still
    answers 200, so health checks look fine).
    """
    from urllib.parse import urlparse

    base = (url or "").rstrip("/")
    path = urlparse(base).path.strip("/")
    if not path and site_id:
        base = f"{base}/{site_id}"
    return f"{base}/@@API/senaite/v1"


API_BASE = _api_base(SENAITE_URL, SENAITE_SITE_ID)


def _auth():
    """Return HTTP Basic Auth for SENAITE API calls."""
    return HTTPBasicAuth(SENAITE_USER, SENAITE_PASSWORD)


def parse_senaite_date(value: str):
    """
    Parse a SENAITE/Plone date string into a ``date``.

    SENAITE returns values in several shapes depending on the field/version, e.g.
    ``2026-07-16``, ``2026-07-16 13:55``, ``2026-07-16T13:55:00`` or the odd
    ``2026-07-16 13:55 PM``. Returns ``None`` if nothing usable is found so the
    caller can fall back to "today".
    """
    from datetime import datetime

    if not value:
        return None
    text = str(value).strip()
    # Drop a stray AM/PM that Plone sometimes appends to a 24h time.
    for suffix in (" AM", " PM", " am", " pm"):
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    # Normalise the ISO 'T' separator.
    text = text.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[: len(fmt) + 4], fmt).date()
        except ValueError:
            continue
    # Last resort: first 10 chars look like a date?
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


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

    Uses the senaite.jsonapi ``/create`` endpoint (``POST /AnalysisRequest`` is
    *not* allowed and returns a 405 wrapped in a 200 body). The AR is created
    under the Client folder via ``parent_path`` and needs at least
    Client + SampleType + DateSampled; we also attach the lab's analysis
    services so the lab has tests to receive/run.

    Args:
        sample_data: dict with keys:
            - client_title: str (SENAITE Client name)
            - sample_type: str (e.g., 'Blood', 'Urine')
            - subject_identifier: str (patient/subject ID -> ClientSampleID)
            - date_sampled: str 'YYYY-MM-DD' (optional; defaults to today)
            - contact_name: str (optional lab contact UID)
            - analyses: list of AnalysisService UIDs/keywords (optional; when
              omitted, all active services are attached)

    Returns:
        dict with 'success', 'senaite_id', 'uid', 'url' keys
    """
    from datetime import date

    try:
        # Find the Client (need both UID and path for the create call).
        client_resp = requests.get(
            f"{API_BASE}/Client",
            params={
                "title": sample_data.get("client_title", "HACT Clinical Trials"),
                "complete": "yes",
            },
            auth=_auth(),
            timeout=10,
        )
        client_resp.raise_for_status()
        clients = client_resp.json().get("items", [])

        if not clients:
            logger.error("No SENAITE Client found with title: %s", sample_data.get("client_title"))
            return {"success": False, "error": "Client not found in SENAITE"}

        client_uid = clients[0].get("uid")
        client_path = clients[0].get("path")

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

        # Analyses: use caller-supplied list, else attach all active services so
        # the sample is actionable for the lab.
        analyses = sample_data.get("analyses")
        if not analyses:
            svc_resp = requests.get(
                f"{API_BASE}/AnalysisService",
                params={"limit": 100},
                auth=_auth(),
                timeout=10,
            )
            if svc_resp.ok:
                analyses = [s.get("uid") for s in svc_resp.json().get("items", []) if s.get("uid")]

        # Build the create payload for the jsonapi /create endpoint.
        payload = {
            "portal_type": "AnalysisRequest",
            "parent_path": client_path,
            "Client": client_uid,
            "SampleType": sample_type_uid,
            "DateSampled": sample_data.get("date_sampled") or date.today().isoformat(),
            "ClientSampleID": sample_data.get("subject_identifier", ""),
        }
        if sample_data.get("contact_name"):
            payload["Contact"] = sample_data["contact_name"]
        if analyses:
            payload["Analyses"] = analyses

        create_resp = requests.post(
            f"{API_BASE}/create",
            json=payload,
            auth=_auth(),
            timeout=20,
        )
        create_resp.raise_for_status()

        result = create_resp.json()
        items = result.get("items", [])

        # jsonapi can answer HTTP 200 with success=false in the body (e.g. a 405
        # or a validation error) — treat that as a failure.
        if result.get("success") is False or not items:
            msg = result.get("message", "No items returned from SENAITE")
            logger.error("SENAITE AR create failed: %s", msg)
            return {"success": False, "error": msg}

        item = items[0]
        senaite_id = item.get("id") or item.get("getId") or item.get("title", "")
        logger.info("Sample created in SENAITE: %s", senaite_id)
        return {
            "success": True,
            "senaite_id": senaite_id,
            "uid": item.get("uid", ""),
            "url": item.get("url", ""),
        }

    except RequestException as e:
        logger.error("Failed to create sample in SENAITE: %s", str(e))
        return {"success": False, "error": str(e)}


def fetch_published_results(client_title: str = None, limit: int = 50) -> list:
    """
    Fetch published analysis results from SENAITE.

    NOTE: An AnalysisRequest's ``Analyses`` field, as returned by the SENAITE
    JSON API, contains only *reference stubs* (``{url, uid, api_url}``) — it does
    NOT embed the result value/title/unit. We therefore query the ``Analysis``
    objects directly (which expose ``getResult``, ``title``, ``getUnit`` and the
    parent ``getRequestID``) and join them back to their published sample to
    recover the ``ClientSampleID`` used for CTMS subject mapping.

    Args:
        client_title: Optional filter by SENAITE Client name
        limit: Max number of samples to consider

    Returns:
        List of dicts with analysis result data
    """
    try:
        # 1) Published samples -> {request_id: {subject_identifier, result_date}}
        ar_params = {
            "portal_type": "AnalysisRequest",
            "review_state": "published",
            "sort_on": "created",
            "sort_order": "descending",
            "limit": limit,
            "complete": "yes",
        }
        if client_title:
            ar_params["getClientTitle"] = client_title

        ar_resp = requests.get(
            f"{API_BASE}/search", params=ar_params, auth=_auth(), timeout=15
        )
        ar_resp.raise_for_status()
        ar_items = ar_resp.json().get("items", [])

        sample_map = {}
        for ar in ar_items:
            request_id = ar.get("id", "")
            if request_id:
                sample_map[request_id] = {
                    "subject_identifier": ar.get("ClientSampleID", "") or "",
                    "result_date": ar.get("DatePublished", ar.get("created", "")),
                }

        if not sample_map:
            logger.info("No published samples found in SENAITE.")
            return []

        # 2) Published analyses (the actual results), joined to the sample above.
        an_params = {
            "portal_type": "Analysis",
            "review_state": "published",
            "limit": limit * 20,
            "complete": "yes",
        }
        an_resp = requests.get(
            f"{API_BASE}/search", params=an_params, auth=_auth(), timeout=15
        )
        an_resp.raise_for_status()
        an_items = an_resp.json().get("items", [])

        results = []
        for an in an_items:
            request_id = an.get("getRequestID", "")
            meta = sample_map.get(request_id)
            if not meta:
                continue  # analysis belongs to a sample outside our filter

            result_value = an.get("getResult", "")
            if result_value in (None, ""):
                continue

            # Prefer the per-analysis result-capture date; fall back to the
            # sample's publish/created date so the CTMS row reflects reality.
            result_date = (
                an.get("getResultCaptureDate")
                or an.get("getDateVerified")
                or meta["result_date"]
            )

            results.append({
                "senaite_sample_id": request_id,
                "senaite_analysis_uid": an.get("uid", ""),
                "subject_identifier": meta["subject_identifier"],
                "test_name": an.get("title", an.get("getKeyword", "")),
                "result_value": str(result_value),
                "unit": an.get("getUnit", an.get("Unit", "")),
                "result_date": result_date,
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
