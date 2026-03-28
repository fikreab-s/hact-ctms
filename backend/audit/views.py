"""Audit views — audit schema (read-only ViewSet with RBAC)."""
from rest_framework import viewsets
from core.permissions import IsAuditor
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of the audit trail. No create/update/delete via API.
    
    Only users with Auditor or admin roles can access.
    """
    queryset = AuditLog.objects.select_related("user").all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditor]
    filterset_fields = ["action", "table_name", "user"]
    search_fields = ["table_name", "record_id"]
    ordering_fields = ["timestamp"]
