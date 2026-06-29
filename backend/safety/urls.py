"""Safety URL routes — safety schema (DRF Router)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "safety"
router = DefaultRouter()
router.register(r"adverse-events", views.AdverseEventViewSet)
router.register(r"cioms-forms", views.CiomsFormViewSet)
router.register(r"safety-reviews", views.SafetyReviewViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # SAE Expedited Reporting
    path("sae-timeline/", views.SaeTimelineView.as_view(), name="sae-timeline"),
    path("sae/<int:pk>/mark-reported/", views.MarkSaeReportedView.as_view(), name="sae-mark-reported"),
]
