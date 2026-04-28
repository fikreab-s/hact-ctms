"""
HACT CTMS — Integration API Views
===================================
REST endpoints for document upload/download via Nextcloud eTMF.
"""

import base64
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger("hact.integrations.views")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
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

    return Response(result)


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
