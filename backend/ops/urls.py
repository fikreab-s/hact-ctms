"""Ops URL routes — ops schema (DRF Router)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "ops"
router = DefaultRouter()
router.register(r"contracts", views.ContractViewSet)
router.register(r"training-records", views.TrainingRecordViewSet)
router.register(r"milestones", views.MilestoneViewSet)

urlpatterns = [path("", include(router.urls))]
