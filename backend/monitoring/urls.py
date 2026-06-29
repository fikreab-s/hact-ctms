"""Monitoring URL routes — Risk-Based Monitoring (RBM)."""

from django.urls import path
from . import views

app_name = "monitoring"

urlpatterns = [
    path("site-risk-scores/", views.SiteRiskScoresView.as_view(), name="site-risk-scores"),
    path("study-overview/", views.StudyOverviewView.as_view(), name="study-overview"),
]
