"""Clinical URL routes — clinical schema (DRF Router)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "clinical"

router = DefaultRouter()
router.register(r"studies", views.StudyViewSet)
router.register(r"sites", views.SiteViewSet)
router.register(r"subjects", views.SubjectViewSet)
router.register(r"visits", views.VisitViewSet)
router.register(r"subject-visits", views.SubjectVisitViewSet)
router.register(r"forms", views.FormViewSet)
router.register(r"items", views.ItemViewSet)
router.register(r"form-instances", views.FormInstanceViewSet)
router.register(r"item-responses", views.ItemResponseViewSet)
router.register(r"queries", views.QueryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
