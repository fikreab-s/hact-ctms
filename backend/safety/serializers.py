"""Safety serializers — safety schema."""
from rest_framework import serializers
from .models import AdverseEvent, CiomsForm, SafetyReview

class AdverseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdverseEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "reported_at")

class CiomsFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiomsForm
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "generated_date")

class SafetyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyReview
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
