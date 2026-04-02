"""Audit views — audit schema (read-only ViewSet with RBAC + CSV export)."""

import csv
from datetime import datetime

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from core.permissions import IsAuditor

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of the audit trail. No create/update/delete via API.

    Only users with Auditor or admin roles can access.

    Custom actions:
    - GET /logs/export-csv/ — Export audit trail as CSV for regulatory inspections
    """

    queryset = AuditLog.objects.select_related("user").all().order_by("-timestamp")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditor]
    filterset_fields = ["action", "table_name", "user"]
    search_fields = ["table_name", "record_id"]
    ordering_fields = ["timestamp"]

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        """Export audit trail as CSV for regulatory inspections.

        GET /api/v1/audit/logs/export-csv/
        Query params (all optional):
            - table_name: Filter by table (e.g., clinical_studies)
            - action: Filter by action (create, update, delete, sign)
            - user: Filter by user ID
            - date_from: Start date (YYYY-MM-DD)
            - date_to: End date (YYYY-MM-DD)
        """
        queryset = self.get_queryset()

        # Apply filters from query params
        table_name = request.query_params.get("table_name")
        action_filter = request.query_params.get("action")
        user_id = request.query_params.get("user")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if table_name:
            queryset = queryset.filter(table_name=table_name)
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if date_from:
            try:
                dt = datetime.strptime(date_from, "%Y-%m-%d")
                queryset = queryset.filter(timestamp__gte=dt)
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, "%Y-%m-%d")
                queryset = queryset.filter(timestamp__date__lte=dt)
            except ValueError:
                pass

        # Build CSV response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"HACT_AuditTrail_{timestamp}.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            "Timestamp",
            "User",
            "Action",
            "Table",
            "Record ID",
            "Old Values",
            "New Values",
        ])

        for log in queryset.iterator():
            writer.writerow([
                log.timestamp.isoformat() if log.timestamp else "",
                log.user.username if log.user else "system",
                log.action,
                log.table_name,
                log.record_id,
                log.old_values or "",
                log.new_values or "",
            ])

        return response

