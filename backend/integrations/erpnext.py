"""ERPNext (Frappe) integration client.

Supports two authentication modes so the deployment works whether or not
API keys have been generated in ERPNext:

1. **Token auth** — used when ``ERPNEXT_API_KEY`` and ``ERPNEXT_API_SECRET``
   are configured (preferred for production).
2. **Session login fallback** — when no API keys are set, log in with
   ``ERPNEXT_USERNAME`` / ``ERPNEXT_PASSWORD`` via ``/api/method/login`` and
   reuse the session cookie.

The previous implementation only ever used token auth and its health check
pinged an *unauthenticated* endpoint, so a misconfigured deployment reported
"healthy" while every write (site → Customer sync) silently failed.
"""

import logging
import threading

import requests
from django.conf import settings
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

# Config from settings (which pulls from .env)
ERPNEXT_URL = getattr(settings, "ERPNEXT_URL", None) or "http://erpnext:8000"
API_KEY = getattr(settings, "ERPNEXT_API_KEY", "") or ""
API_SECRET = getattr(settings, "ERPNEXT_API_SECRET", "") or ""
USERNAME = getattr(settings, "ERPNEXT_USERNAME", "") or ""
PASSWORD = getattr(settings, "ERPNEXT_PASSWORD", "") or ""
# Internal Frappe multi-tenant site name (used for Host resolution).
ERPNEXT_SITE_NAME = getattr(settings, "ERPNEXT_SITE_NAME", "") or "hact.local"

_SITE_HEADERS = {
    "Host": ERPNEXT_SITE_NAME,
    "X-Frappe-Site-Name": ERPNEXT_SITE_NAME,
    "Accept": "application/json",
}

_session = None
_session_lock = threading.Lock()


def _configured() -> bool:
    return bool((API_KEY and API_SECRET) or (USERNAME and PASSWORD))


def _build_session() -> requests.Session:
    """Create and authenticate a requests session against ERPNext."""
    s = requests.Session()
    s.headers.update(_SITE_HEADERS)

    if API_KEY and API_SECRET:
        s.headers["Authorization"] = f"token {API_KEY}:{API_SECRET}"
        return s

    if USERNAME and PASSWORD:
        resp = s.post(
            f"{ERPNEXT_URL}/api/method/login",
            data={"usr": USERNAME, "pwd": PASSWORD},
            headers=_SITE_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return s

    raise RuntimeError(
        "ERPNext is not configured: set ERPNEXT_API_KEY/ERPNEXT_API_SECRET "
        "or ERPNEXT_USERNAME/ERPNEXT_PASSWORD in the environment."
    )


def _get_session(force_new: bool = False) -> requests.Session:
    global _session
    with _session_lock:
        if force_new or _session is None:
            _session = _build_session()
        return _session


def _request(method: str, path: str, **kwargs):
    """Issue an authenticated request, re-authenticating once on 401/403."""
    kwargs.setdefault("timeout", 15)
    headers = dict(_SITE_HEADERS)
    headers.update(kwargs.pop("headers", {}))

    session = _get_session()
    resp = session.request(method, f"{ERPNEXT_URL}{path}", headers=headers, **kwargs)
    if resp.status_code in (401, 403):
        # Session/token may have expired — rebuild once and retry.
        session = _get_session(force_new=True)
        resp = session.request(method, f"{ERPNEXT_URL}{path}", headers=headers, **kwargs)
    return resp


def check_availability() -> bool:
    """Return True only if ERPNext is reachable **and** authentication works.

    Uses an authenticated endpoint so the reported health reflects whether the
    integration can actually read/write, not just whether the server responds.
    """
    if not _configured():
        logger.warning("ERPNext credentials not configured; integration disabled.")
        return False
    try:
        resp = _request("GET", "/api/method/frappe.auth.get_logged_user", timeout=10)
        if resp.status_code == 200:
            logger.info("ERPNext authenticated and reachable.")
            return True
        logger.warning("ERPNext auth check returned status %s", resp.status_code)
        return False
    except RequestException as e:
        logger.error("ERPNext connection/auth failed: %s", str(e))
        return False


def _find_customer(customer_name: str):
    """Return the ERPNext Customer name if one already exists, else None."""
    try:
        resp = _request(
            "GET",
            "/api/resource/Customer",
            params={"filters": f'[["customer_name","=","{customer_name}"]]'},
        )
        if resp.status_code == 200:
            rows = resp.json().get("data", [])
            if rows:
                return rows[0].get("name")
    except RequestException:
        pass
    return None


def _default_customer_group() -> str:
    """Return a valid *leaf* Customer Group.

    A customer cannot be assigned to a group node (e.g. "All Customer Groups"),
    so we discover a real leaf group. Falls back to "Commercial" (an ERPNext
    default) if discovery fails.
    """
    try:
        resp = _request(
            "GET",
            "/api/resource/Customer Group",
            params={"filters": '[["is_group","=",0]]', "limit_page_length": 1},
        )
        if resp.status_code == 200:
            rows = resp.json().get("data", [])
            if rows:
                return rows[0].get("name")
    except RequestException:
        pass
    return "Commercial"


def sync_site_to_customer(site_data: dict) -> str:
    """Sync a Django Site to an ERPNext Customer (idempotent).

    Returns the ERPNext Customer name (ID).
    """
    customer_name = site_data.get("name")

    existing = _find_customer(customer_name)
    if existing:
        logger.info("ERPNext Customer already exists for '%s': %s", customer_name, existing)
        return existing

    payload = {
        "customer_name": customer_name,
        "customer_type": "Company",
        "customer_group": _default_customer_group(),
        "territory": "All Territories",
    }

    try:
        resp = _request("POST", "/api/resource/Customer", json=payload)
        resp.raise_for_status()
        return resp.json().get("data", {}).get("name")
    except RequestException as e:
        body = getattr(e.response, "text", "")[:500] if getattr(e, "response", None) else ""
        logger.error("Failed to sync site to ERPNext Customer: %s | body=%s", str(e), body)
        raise
