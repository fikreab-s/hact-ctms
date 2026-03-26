"""Ops serializers — ops schema."""
from rest_framework import serializers
from .models import Contract, Milestone, TrainingRecord

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class TrainingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingRecord
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
