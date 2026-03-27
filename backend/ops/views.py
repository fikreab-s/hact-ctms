"""Ops views — ops schema ViewSets."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contract, Milestone, TrainingRecord
from .serializers import ContractSerializer, MilestoneSerializer, TrainingRecordSerializer

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("site").all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["contract_number"]
    filterset_fields = ["site", "status"]

class TrainingRecordViewSet(viewsets.ModelViewSet):
    queryset = TrainingRecord.objects.select_related("site").all()
    serializer_class = TrainingRecordSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["staff_name", "training_type"]
    filterset_fields = ["site", "training_type"]

class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.select_related("study", "site").all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["study", "site", "status"]
