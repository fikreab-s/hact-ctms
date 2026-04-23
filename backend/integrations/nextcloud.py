"""
HACT CTMS — Nextcloud Integration (eTMF Document Management)
==============================================================
WebDAV client for document upload/download and OCS API for
folder sharing. Nextcloud serves as the electronic Trial Master
File (eTMF) backend, storing regulatory documents, CIOMS forms,
safety reviews, contracts, and export snapshots.

Architecture:
    Django → Nextcloud WebDAV  (upload/download/mkdir)
    Django → Nextcloud OCS API (sharing, user info)

eTMF Folder Structure (auto-created per study):
    /eTMF/{PROTOCOL}/
    ├── 01_Regulatory/          # IRB/EC submissions, approvals
    ├── 02_Protocol/            # Protocol versions, amendments
    ├── 03_Safety/              # CIOMS forms, safety reviews, SAE reports
    ├── 04_DataManagement/      # CRF snapshots, DB lock records
    ├── 05_Monitoring/          # Monitoring visit reports
    ├── 06_SiteDocuments/       # Site-specific documents
    ├── 07_Contracts/           # Contracts, budgets
    ├── 08_Training/            # GCP certs, training logs
    ├── 09_Exports/             # CDISC/SDTM exports, data snapshots
    └── 10_Correspondence/      # Meeting minutes, email records
"""

import logging
import os
from io import BytesIO
from typing import Optional

import requests

logger = logging.getLogger("hact.integrations.nextcloud")

# =============================================================================
# Configuration (from environment / Django settings)
# =============================================================================

NC_BASE_URL = os.environ.get("NEXTCLOUD_URL", "http://nextcloud:80")
NC_USER = os.environ.get("NEXTCLOUD_ADMIN_USER", "admin")
NC_PASSWORD = os.environ.get("NEXTCLOUD_ADMIN_PASSWORD", "hact-nc-2026")

# WebDAV base path for Nextcloud
WEBDAV_BASE = f"{NC_BASE_URL}/remote.php/dav/files/{NC_USER}"
OCS_BASE = f"{NC_BASE_URL}/ocs/v2.php"

# eTMF folder template — TMF Reference Model inspired structure
ETMF_FOLDERS = [
    "01_Regulatory",
    "02_Protocol",
    "03_Safety",
    "04_DataManagement",
    "05_Monitoring",
    "06_SiteDocuments",
    "07_Contracts",
    "08_Training",
    "09_Exports",
    "10_Correspondence",
]


# =============================================================================
# Low-level WebDAV Helpers
# =============================================================================

def _webdav_request(method: str, path: str, **kwargs) -> requests.Response:
    """Execute a WebDAV request against Nextcloud."""
    url = f"{WEBDAV_BASE}/{path.lstrip('/')}"
    return requests.request(
        method,
        url,
        auth=(NC_USER, NC_PASSWORD),
        timeout=kwargs.pop("timeout", 60),
        **kwargs,
    )


def _ocs_request(method: str, endpoint: str, **kwargs) -> dict:
    """Execute an OCS API request against Nextcloud."""
    url = f"{OCS_BASE}/{endpoint.lstrip('/')}"
    headers = kwargs.pop("headers", {})
    headers["OCS-APIRequest"] = "true"
    headers.setdefault("Accept", "application/json")

    resp = requests.request(
        method,
        url,
        auth=(NC_USER, NC_PASSWORD),
        headers=headers,
        timeout=kwargs.pop("timeout", 60),
        **kwargs,
    )
    resp.raise_for_status()
    return resp.json()


# =============================================================================
# Health / Availability
# =============================================================================

def is_available() -> bool:
    """Check if Nextcloud is reachable and installed."""
    try:
        resp = requests.get(
            f"{NC_BASE_URL}/status.php",
            timeout=5,
        )
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_server_info() -> Optional[dict]:
    """Get Nextcloud server info via status.php."""
    try:
        resp = requests.get(f"{NC_BASE_URL}/status.php", timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error("Failed to get Nextcloud server info: %s", e)
    return None


# =============================================================================
# Directory Operations (WebDAV MKCOL / PROPFIND)
# =============================================================================

def create_folder(path: str) -> bool:
    """
    Create a folder in Nextcloud via WebDAV MKCOL.
    Returns True if created or already exists.
    """
    resp = _webdav_request("MKCOL", path)
    if resp.status_code in (201, 405):
        # 201 = Created, 405 = Already exists
        return True
    logger.error("Failed to create folder '%s': HTTP %s", path, resp.status_code)
    return False


def folder_exists(path: str) -> bool:
    """Check if a folder exists via WebDAV PROPFIND."""
    resp = _webdav_request("PROPFIND", path, headers={"Depth": "0"})
    return resp.status_code in (200, 207)


def list_folder(path: str) -> list:
    """
    List contents of a Nextcloud folder.
    Returns list of dicts with 'name' and 'is_dir' keys.
    """
    resp = _webdav_request("PROPFIND", path, headers={"Depth": "1"})
    if resp.status_code not in (200, 207):
        logger.error("Failed to list folder '%s': HTTP %s", path, resp.status_code)
        return []

    # Parse the multistatus XML response
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        logger.error("Failed to parse PROPFIND response for '%s'", path)
        return []

    ns = {"d": "DAV:"}
    items = []
    for response_el in root.findall("d:response", ns):
        href = response_el.findtext("d:href", "", ns)
        # Skip the folder itself (first entry)
        name = href.rstrip("/").split("/")[-1]
        if not name or name == NC_USER:
            continue

        resource_type = response_el.find(".//d:resourcetype", ns)
        is_dir = resource_type is not None and resource_type.find("d:collection", ns) is not None

        items.append({"name": name, "is_dir": is_dir, "href": href})

    return items


# =============================================================================
# File Operations (WebDAV PUT / GET / DELETE)
# =============================================================================

def upload_file(remote_path: str, content: bytes, content_type: str = "application/octet-stream") -> bool:
    """
    Upload a file to Nextcloud via WebDAV PUT.
    Creates parent directories automatically.

    Args:
        remote_path: Path in Nextcloud (e.g. "eTMF/HACT-001/03_Safety/cioms_001.pdf")
        content: File content as bytes
        content_type: MIME type

    Returns:
        True if upload succeeded
    """
    # Ensure parent directories exist
    parts = remote_path.strip("/").split("/")
    for i in range(1, len(parts)):
        parent = "/".join(parts[:i])
        create_folder(parent)

    resp = _webdav_request(
        "PUT",
        remote_path,
        data=content,
        headers={"Content-Type": content_type},
    )
    if resp.status_code in (201, 204):
        logger.info("Uploaded file to Nextcloud: %s", remote_path)
        return True
    logger.error("Failed to upload '%s': HTTP %s", remote_path, resp.status_code)
    return False


def download_file(remote_path: str) -> Optional[bytes]:
    """
    Download a file from Nextcloud via WebDAV GET.
    Returns file content as bytes, or None on failure.
    """
    resp = _webdav_request("GET", remote_path)
    if resp.status_code == 200:
        return resp.content
    logger.error("Failed to download '%s': HTTP %s", remote_path, resp.status_code)
    return None


def delete_file(remote_path: str) -> bool:
    """Delete a file or folder from Nextcloud via WebDAV DELETE."""
    resp = _webdav_request("DELETE", remote_path)
    if resp.status_code in (204, 404):
        return True
    logger.error("Failed to delete '%s': HTTP %s", remote_path, resp.status_code)
    return False


def get_file_url(remote_path: str) -> str:
    """
    Build a Nextcloud download URL for a given remote path.
    This URL can be stored in Django file_url fields.
    """
    return f"{NC_BASE_URL}/remote.php/dav/files/{NC_USER}/{remote_path.lstrip('/')}"


# =============================================================================
# eTMF — Trial Master File Management
# =============================================================================

def create_etmf_structure(protocol_number: str) -> bool:
    """
    Create the full eTMF folder structure for a study.
    Based on the TMF Reference Model.

    Args:
        protocol_number: Study protocol (e.g. "HACT-001")

    Returns:
        True if all folders created successfully
    """
    base = f"eTMF/{protocol_number}"
    logger.info("Creating eTMF structure for study: %s", protocol_number)

    if not create_folder("eTMF"):
        return False
    if not create_folder(base):
        return False

    success = True
    for folder in ETMF_FOLDERS:
        if not create_folder(f"{base}/{folder}"):
            success = False
            logger.error("Failed to create eTMF folder: %s/%s", base, folder)

    if success:
        logger.info("✅ eTMF structure created for %s (%d folders)", protocol_number, len(ETMF_FOLDERS))
    return success


def upload_to_etmf(
    protocol_number: str,
    category: str,
    filename: str,
    content: bytes,
    content_type: str = "application/pdf",
) -> Optional[str]:
    """
    Upload a document to the appropriate eTMF category folder.

    Args:
        protocol_number: Study protocol (e.g. "HACT-001")
        category: eTMF subfolder (e.g. "03_Safety", "01_Regulatory")
        filename: Document filename
        content: File content as bytes
        content_type: MIME type

    Returns:
        The Nextcloud file URL if successful, None otherwise
    """
    remote_path = f"eTMF/{protocol_number}/{category}/{filename}"

    if upload_file(remote_path, content, content_type):
        url = get_file_url(remote_path)
        logger.info("Document uploaded to eTMF: %s", remote_path)
        return url

    return None


def list_etmf_studies() -> list:
    """List all study protocol folders under /eTMF/."""
    if not folder_exists("eTMF"):
        return []

    items = list_folder("eTMF")
    return [item["name"] for item in items if item["is_dir"]]


def list_etmf_documents(protocol_number: str, category: str = "") -> list:
    """
    List documents in a study's eTMF folder.

    Args:
        protocol_number: Study protocol (e.g. "HACT-001")
        category: Optional subfolder (e.g. "03_Safety"). If empty, lists categories.
    """
    path = f"eTMF/{protocol_number}"
    if category:
        path = f"{path}/{category}"

    return list_folder(path)
