"""Lab serializers — lab schema."""
from rest_framework import serializers
from .models import LabResult, ReferenceRange, SampleCollection

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "imported_at")

class ReferenceRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceRange
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class SampleCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCollection
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
