"""Lab URL routes — lab schema (DRF Router)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = "lab"
router = DefaultRouter()
router.register(r"results", views.LabResultViewSet)
router.register(r"reference-ranges", views.ReferenceRangeViewSet)
router.register(r"samples", views.SampleCollectionViewSet)

urlpatterns = [path("", include(router.urls))]
