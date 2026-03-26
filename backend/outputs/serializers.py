"""Outputs serializers — outputs schema."""
from rest_framework import serializers
from .models import DatasetSnapshot, DataQualityReport

class DatasetSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetSnapshot
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "snapshot_date")

class DataQualityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataQualityReport
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "generated_at")
