"""Feedback URL routes (UAT)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "feedback"
router = DefaultRouter()
router.register(r"items", views.FeedbackViewSet)

urlpatterns = [path("", include(router.urls))]
