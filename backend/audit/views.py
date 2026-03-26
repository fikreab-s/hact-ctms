"""Audit views — audit schema (read-only ViewSet)."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of the audit trail. No create/update/delete via API."""
    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["action", "table_name", "user"]
    search_fields = ["table_name", "record_id"]
    ordering_fields = ["timestamp"]
