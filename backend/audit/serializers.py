"""Audit serializers — audit schema (read-only)."""
from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = (
            "id", "user", "action", "table_name", "record_id",
            "old_value", "new_value", "ip_address", "user_agent", "timestamp",
        )

