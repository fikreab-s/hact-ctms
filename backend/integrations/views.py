"""
HACT CTMS — Integration API Views
===================================
REST endpoints for document upload/download via Nextcloud eTMF.
"""

import base64
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsLabManager, IsStudyAdmin

logger = logging.getLogger("hact.integrations.views")


@api_view(["POST"])
@permission_classes([IsStudyAdmin])
def upload_document(request):
    """
    Upload a document to the eTMF in Nextcloud.

    POST /api/v1/integrations/documents/upload/
    Body (multipart/form-data):
        - file: The file to upload
        - protocol_number: Study protocol (e.g. "HACT-001")
        - category: eTMF category folder (e.g. "03_Safety", "01_Regulatory")

    Returns:
        - 201: { "url": "...", "filename": "...", "category": "...", "protocol": "..." }
        - 400: Validation error
        - 503: Nextcloud not available
    """
    protocol = request.data.get("protocol_number")
    category = request.data.get("category")
    uploaded_file = request.FILES.get("file")

    # Validate required fields
    if not protocol:
        return Response(
            {"error": "protocol_number is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not category:
        return Response(
            {"error": "category is required (e.g. '03_Safety', '01_Regulatory')"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not uploaded_file:
        return Response(
            {"error": "file is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate category is a known eTMF folder
    from integrations.nextcloud import ETMF_FOLDERS
    valid_categories = [f for f in ETMF_FOLDERS]
    if category not in valid_categories:
        return Response(
            {
                "error": f"Invalid category '{category}'",
                "valid_categories": valid_categories,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check Nextcloud availability
    from integrations.nextcloud import is_available, upload_to_etmf

    if not is_available():
        return Response(
            {"error": "Nextcloud is not available. Start with: docker compose --profile nextcloud up -d"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Read file content
    content = uploaded_file.read()
    content_type = uploaded_file.content_type or "application/octet-stream"
    filename = uploaded_file.name

    # Upload to Nextcloud
    url = upload_to_etmf(
        protocol_number=protocol,
        category=category,
        filename=filename,
        content=content,
        content_type=content_type,
    )

    if url:
        logger.info(
            "Document uploaded by %s: %s/%s/%s",
            request.user.username,
            protocol,
            category,
            filename,
        )
        return Response(
            {
                "url": url,
                "filename": filename,
                "category": category,
                "protocol": protocol,
                "size_bytes": len(content),
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"error": "Failed to upload document to Nextcloud"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_etmf(request, protocol_number):
    """
    List eTMF documents for a study.

    GET /api/v1/integrations/etmf/{protocol_number}/
    Query params:
        - category: Optional eTMF subfolder (e.g. "03_Safety")

    Returns:
        - 200: { "protocol": "...", "category": "...", "documents": [...] }
        - 503: Nextcloud not available
    """
    from integrations.nextcloud import is_available, list_etmf_documents

    if not is_available():
        return Response(
            {"error": "Nextcloud is not available"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    category = request.query_params.get("category", "")
    documents = list_etmf_documents(protocol_number, category)

    return Response({
        "protocol": protocol_number,
        "category": category or "(root)",
        "documents": [
            {
                "name": doc["name"],
                "is_directory": doc["is_dir"],
            }
            for doc in documents
        ],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_etmf_categories(request):
    """
    List valid eTMF category folder names.

    GET /api/v1/integrations/etmf-categories/
    """
    from integrations.nextcloud import ETMF_FOLDERS

    return Response({
        "categories": [
            {"id": folder, "label": folder.replace("_", " ")}
            for folder in ETMF_FOLDERS
        ]
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def integration_status(request):
    """
    Health status of all external integrations.

    GET /api/v1/integrations/status/
    """
    result = {}

    # Nextcloud
    try:
        from integrations.nextcloud import is_available as nc_available, get_server_info
        nc_up = nc_available()
        nc_info = get_server_info() if nc_up else None
        result["nextcloud"] = {
            "status": "healthy" if nc_up else "unavailable",
            "version": nc_info.get("versionstring") if nc_info else None,
        }
    except Exception:
        result["nextcloud"] = {"status": "error"}

    # OpenClinica
    try:
        from integrations.openclinica import is_available as oc_available
        result["openclinica"] = {
            "status": "healthy" if oc_available() else "unavailable",
        }
    except Exception:
        result["openclinica"] = {"status": "error"}

    # ERPNext
    try:
        from integrations.erpnext import check_availability as erp_available
        result["erpnext"] = {
            "status": "healthy" if erp_available() else "unavailable",
        }
    except Exception:
        result["erpnext"] = {"status": "error"}

    # SENAITE
    try:
        from integrations.senaite import check_availability as senaite_available
        result["senaite"] = {
            "status": "healthy" if senaite_available() else "unavailable",
        }
    except Exception:
        result["senaite"] = {"status": "error"}

    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def openclinica_diagnostic(request):
    """
    Read-only OpenClinica SOAP web-service diagnostic.

    GET /api/v1/integrations/openclinica/diagnostic/?study_identifier=HACTPSBIV2

    Returns WS config, an authenticated listAll probe (raw HTTP status +
    snippet), and — when study_identifier is given — the studies/subjects
    OpenClinica reports. Helps distinguish auth vs endpoint vs data issues.
    """
    from integrations.openclinica import diagnostic

    study_identifier = request.query_params.get("study_identifier", "")
    create_label = request.query_params.get("create_label", "")
    site_identifier = request.query_params.get("site_identifier", "")
    return Response(diagnostic(study_identifier, create_label, site_identifier))


@api_view(["POST"])
@permission_classes([IsStudyAdmin])
def import_openclinica_metadata(request):
    """
    Import CRF metadata (visits, forms, items) from OpenClinica into CTMS.

    POST /api/v1/integrations/openclinica/import-metadata/
    Body: { "study_id": 4, "dry_run": true }

    - dry_run=true (default): parse + preview what would be created/updated,
      write nothing (also returns a raw ODM snippet for debugging).
    - dry_run=false: upsert the CTMS Visit/Form/Item/VisitForm rows and store
      the real OpenClinica OIDs so captured data round-trips back to OC.
    """
    from clinical.models import Study
    from integrations.metadata_import import import_study_metadata

    study_id = request.data.get("study_id")
    dry_run = bool(request.data.get("dry_run", True))

    if not study_id:
        return Response(
            {"error": "study_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        study = Study.objects.get(pk=study_id)
    except Study.DoesNotExist:
        return Response(
            {"error": "Study not found"}, status=status.HTTP_404_NOT_FOUND
        )

    result = import_study_metadata(study, dry_run=dry_run)
    http = status.HTTP_200_OK if result.get("ok") else status.HTTP_400_BAD_REQUEST
    return Response(result, status=http)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def erpnext_webhook(request):
    """
    Webhook endpoint for ERPNext events.
    Expected to be called when a Site Contract is marked as 'Signed'.
    
    POST /api/v1/integrations/erpnext/webhook/contract-signed/
    Body:
        {
            "erpnext_site_id": "Customer-001",
            "contract_status": "Signed"
        }
    """
    erpnext_site_id = request.data.get("erpnext_site_id")
    contract_status = request.data.get("contract_status")
    
    if not erpnext_site_id:
        return Response(
            {"error": "erpnext_site_id is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if contract_status == "Signed":
        from clinical.models import Site
        try:
            site = Site.objects.get(erpnext_site_id=erpnext_site_id)
            if site.status != 'active':
                site.status = 'active'
                site.save(update_fields=['status'])
                logger.info(f"Site {site.name} activated via ERPNext contract signature webhook.")
            return Response({"status": "success", "message": "Site activated."})
        except Site.DoesNotExist:
            logger.warning(f"ERPNext webhook received for unknown site ID: {erpnext_site_id}")
            return Response(
                {"error": "Site not found in CTMS"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    return Response({"status": "ignored", "message": f"Contract status is {contract_status}"})


def _senaite_webhook_authorized(request) -> bool:
    """
    Authorize an inbound SENAITE webhook.

    SENAITE/Plone calls this server-to-server and has no Keycloak token, so we
    authenticate with a shared secret sent as ``X-SENAITE-Token`` (or
    ``?token=``). An already-authenticated CTMS user is also accepted so the
    endpoint stays usable from the app/tests. If no secret is configured we
    fall back to requiring authentication (fail closed).
    """
    from django.conf import settings as _settings

    secret = getattr(_settings, "SENAITE_WEBHOOK_SECRET", "") or ""
    if secret:
        provided = (
            request.META.get("HTTP_X_SENAITE_TOKEN")
            or request.query_params.get("token")
            or ""
        )
        if provided and provided == secret:
            return True
    return bool(request.user and request.user.is_authenticated)


@api_view(["POST"])
@permission_classes([AllowAny])
def senaite_webhook(request):
    """
    Webhook endpoint for SENAITE events — the low-latency alternative to the
    15-minute Celery poll. When SENAITE publishes a sample it POSTs here and we
    immediately (a) mark the linked SampleCollection completed and (b) kick off
    an on-demand results pull, so CTMS reflects the new results within seconds.

    Auth: shared secret via ``X-SENAITE-Token`` header (see SENAITE_WEBHOOK_SECRET)
    or an authenticated CTMS session.

    POST /api/v1/integrations/senaite/webhook/results-published/
    Body:
        {
            "senaite_sample_id": "SAMP-2026-0001",   # optional but recommended
            "status": "published"
        }
    """
    if not _senaite_webhook_authorized(request):
        return Response(
            {"error": "Unauthorized — missing or invalid webhook token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    senaite_sample_id = request.data.get("senaite_sample_id")
    sample_status = request.data.get("status", "published")

    if sample_status != "published":
        return Response(
            {"status": "ignored", "message": f"Sample status is {sample_status}"}
        )

    from integrations.tasks import pull_results_from_senaite
    from lab.models import SampleCollection

    study_id = None
    sample_marked = False

    # Link + complete the specific sample when we know its id (optional — some
    # SENAITE setups only send an event ping without the sample id).
    if senaite_sample_id:
        sample = (
            SampleCollection.objects.select_related("subject")
            .filter(senaite_sample_id=senaite_sample_id)
            .first()
        )
        if sample:
            study_id = getattr(sample.subject, "study_id", None)
            if sample.status != "completed":
                sample.status = "completed"
                sample.save(update_fields=["status"])
            sample_marked = True
            logger.info(
                "Sample %s marked completed via SENAITE results-published webhook.",
                senaite_sample_id,
            )
        else:
            logger.warning(
                "SENAITE webhook for unknown sample %s — still triggering pull.",
                senaite_sample_id,
            )

    # Trigger the immediate results pull (async on the worker). Scoped to the
    # sample's study when known, otherwise a global pull.
    pull_results_from_senaite.delay(study_id=study_id)

    return Response(
        {
            "status": "accepted",
            "sample_marked_completed": sample_marked,
            "pull_triggered": True,
            "study_id": study_id,
        }
    )


@api_view(["POST"])
@permission_classes([IsLabManager])
def senaite_pull_results(request):
    """
    On-demand trigger for the SENAITE -> CTMS lab-result pull (same logic the
    Celery beat runs every 15 min). Runs synchronously and returns what was
    fetched from SENAITE plus how many LabResults were imported/skipped, which
    makes it usable both as a "Sync lab results now" action and for diagnostics.

    POST /api/v1/integrations/senaite/pull-results/
    Body (optional): { "study_id": 4 }
    """
    import requests as _requests
    from django.conf import settings as _settings

    from integrations import senaite as _sen
    from integrations.senaite import fetch_published_results
    from integrations.tasks import pull_results_from_senaite

    study_id = request.data.get("study_id")

    # --- diagnostics: show exactly what the container sees from SENAITE ---
    debug = {"senaite_url": _sen.SENAITE_URL, "api_user": _sen.SENAITE_USER, "api_base": _sen.API_BASE}
    try:
        ar = _requests.get(
            f"{_sen.API_BASE}/search",
            params={"portal_type": "AnalysisRequest", "review_state": "published",
                    "getClientTitle": "HACT Clinical Trials", "complete": "yes", "limit": 50},
            auth=_sen._auth(), timeout=15,
        )
        debug["ar_status"] = ar.status_code
        debug["ar_count"] = len((ar.json() or {}).get("items", [])) if ar.ok else None
        an = _requests.get(
            f"{_sen.API_BASE}/search",
            params={"portal_type": "Analysis", "review_state": "published", "complete": "yes", "limit": 200},
            auth=_sen._auth(), timeout=15,
        )
        debug["analysis_status"] = an.status_code
        debug["analysis_count"] = len((an.json() or {}).get("items", [])) if an.ok else None
        # who does SENAITE think we are? (bad Basic-auth password -> Anonymous, still 200)
        cu = _requests.get(f"{_sen.API_BASE}/users/current", auth=_sen._auth(), timeout=15)
        try:
            cu_items = (cu.json() or {}).get("items", [{}])
            debug["current_user"] = cu_items[0].get("userid") or cu_items[0].get("username") or cu_items[0]
        except Exception:  # noqa: BLE001
            debug["current_user"] = cu.text[:120]
        debug["current_user_status"] = cu.status_code
        # AR count with NO client filter, to isolate the getClientTitle filter
        ar_all = _requests.get(
            f"{_sen.API_BASE}/search",
            params={"portal_type": "AnalysisRequest", "complete": "no", "limit": 5},
            auth=_sen._auth(), timeout=15,
        )
        debug["ar_all_count"] = len((ar_all.json() or {}).get("items", [])) if ar_all.ok else None
    except Exception as e:  # noqa: BLE001
        debug["diag_error"] = str(e)

    fetched = fetch_published_results(client_title="HACT Clinical Trials")

    try:
        outcome = pull_results_from_senaite.apply(kwargs={"study_id": study_id}).result
    except Exception as e:  # surface task errors instead of hiding them
        logger.exception("Manual SENAITE pull failed")
        return Response(
            {"error": str(e), "fetched_count": len(fetched)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "debug": debug,
            "fetched_count": len(fetched),
            "fetched_preview": fetched[:8],
            "task_result": str(outcome),
        }
    )
