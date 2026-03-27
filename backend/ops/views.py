"""Ops views — ops schema ViewSets with RBAC."""
from rest_framework import viewsets
from core.mixins import AuditCreateMixin
from core.permissions import IsOpsManager
from .models import Contract, Milestone, TrainingRecord
from .serializers import ContractSerializer, MilestoneSerializer, TrainingRecordSerializer


class ContractViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("site").all()
    serializer_class = ContractSerializer
    permission_classes = [IsOpsManager]
    search_fields = ["contract_number"]
    filterset_fields = ["site", "status"]


class TrainingRecordViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = TrainingRecord.objects.select_related("site").all()
    serializer_class = TrainingRecordSerializer
    permission_classes = [IsOpsManager]
    search_fields = ["staff_name", "training_type"]
    filterset_fields = ["site", "training_type"]


class MilestoneViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    queryset = Milestone.objects.select_related("study", "site").all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsOpsManager]
    filterset_fields = ["study", "site", "status"]
