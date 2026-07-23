"""
Risk-Based Monitoring (RBM) Views — ICH E6(R3) Compliance
==========================================================
Centralized monitoring dashboard computing risk indicators per site.

Endpoints:
    GET /api/v1/monitoring/site-risk-scores/?study_id=<id>
    GET /api/v1/monitoring/study-overview/?study_id=<id>
"""

import logging
from datetime import timedelta

from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsMonitoringViewer

from clinical.models import (
    FormInstance, Query, Site, Study, Subject, SubjectVisit,
)
from safety.models import AdverseEvent

logger = logging.getLogger("monitoring.views")


class SiteRiskScoresView(APIView):
    """GET /api/v1/monitoring/site-risk-scores/?study_id=<id>

    Computes risk indicators for each site in a study per ICH E6(R3):
    - Enrollment rate vs. target
    - Query rate (high = data quality concern)
    - AE reporting rate (low = possible under-reporting)
    - CRF completion timeliness
    - Overall risk score (0-100, lower = more risk)

    Returns color-coded risk levels: low (≥80), medium (50-79), high (<50)
    """

    permission_classes = [IsMonitoringViewer]

    def get(self, request):
        study_id = request.query_params.get("study_id")

        if not study_id:
            # Default to first active study
            study = Study.objects.filter(status="active").first()
            if not study:
                study = Study.objects.first()
            if not study:
                return Response({"results": [], "study": None})
            study_id = study.id
        else:
            try:
                study = Study.objects.get(pk=study_id)
            except Study.DoesNotExist:
                return Response({"detail": "Study not found."}, status=404)

        sites = Site.objects.filter(study=study)
        now = timezone.now()

        results = []
        for site in sites:
            indicators = self._compute_site_indicators(site, study, now)
            overall_score = self._compute_overall_score(indicators)
            risk_level = self._score_to_risk_level(overall_score)

            results.append({
                "site_id": site.id,
                "site_code": site.site_code,
                "site_name": site.name,
                "risk_level": risk_level,
                "overall_score": overall_score,
                "indicators": indicators,
            })

        # Sort by risk (highest risk first)
        results.sort(key=lambda x: x["overall_score"])

        return Response({
            "study": {
                "id": study.id,
                "name": study.name,
                "protocol_number": study.protocol_number,
            },
            "results": results,
        })

    def _compute_site_indicators(self, site, study, now):
        """Compute individual risk indicators for a site."""
        subjects = Subject.objects.filter(site=site, study=study)
        enrolled = subjects.filter(status="enrolled")

        # ── 1. Enrollment Rate ──
        # Subjects enrolled per month since site activation
        months_active = 1
        if site.activation_date:
            delta = (now.date() - site.activation_date).days
            months_active = max(1, delta / 30)

        enrollment_rate = round(enrolled.count() / months_active, 2)
        # Benchmark: 2 subjects/month is typical for a small trial
        enrollment_target = 2.0
        enrollment_score = min(100, round((enrollment_rate / max(enrollment_target, 0.01)) * 100))

        # ── 2. Query Rate ──
        # Open queries per subject at this site
        site_subjects = subjects.values_list("id", flat=True)
        open_queries = Query.objects.filter(
            item_response__form_instance__subject_id__in=site_subjects,
            status="open",
        ).count()
        total_subjects = subjects.count() or 1
        query_rate = round(open_queries / total_subjects, 2)
        # Benchmark: < 2 open queries per subject is good
        query_benchmark = 2.0
        if query_rate <= query_benchmark:
            query_score = 100
        else:
            query_score = max(0, round(100 - ((query_rate - query_benchmark) / query_benchmark) * 100))

        # ── 3. AE Reporting Rate ──
        # AEs per enrolled subject (low might mean under-reporting)
        ae_count = AdverseEvent.objects.filter(
            subject_id__in=site_subjects,
        ).count()
        ae_rate = round(ae_count / max(enrolled.count(), 1), 2)
        # Benchmark: 1-3 AEs per subject is typical
        # Too low (< 0.5) suggests under-reporting
        ae_benchmark = 1.0
        if ae_rate >= ae_benchmark:
            ae_score = 100
        elif ae_rate >= 0.5:
            ae_score = 70
        elif enrolled.count() == 0:
            ae_score = 100  # No subjects yet, can't judge
        else:
            ae_score = max(0, round((ae_rate / max(ae_benchmark, 0.01)) * 100))

        # ── 4. CRF Completion ──
        # Percentage of visits with completed CRFs
        total_visits = SubjectVisit.objects.filter(
            subject_id__in=site_subjects,
        ).count()
        completed_visits = SubjectVisit.objects.filter(
            subject_id__in=site_subjects,
            status="completed",
        ).count()
        crf_completion = round((completed_visits / max(total_visits, 1)) * 100, 1)
        crf_target = 95
        crf_score = min(100, round((crf_completion / max(crf_target, 1)) * 100))

        # ── 5. Protocol Deviations ──
        # Count overdue SAEs as proxy for protocol deviations
        overdue_saes = AdverseEvent.objects.filter(
            subject_id__in=site_subjects,
            serious=True,
            reporting_status="overdue",
        ).count()
        deviation_threshold = 3
        if overdue_saes == 0:
            deviation_score = 100
        else:
            deviation_score = max(0, round(100 - (overdue_saes / deviation_threshold) * 100))

        return {
            "enrollment_rate": {
                "value": enrollment_rate,
                "target": enrollment_target,
                "unit": "subjects/month",
                "score": enrollment_score,
                "risk": self._score_to_risk_level(enrollment_score),
            },
            "query_rate": {
                "value": query_rate,
                "benchmark": query_benchmark,
                "unit": "open queries/subject",
                "score": query_score,
                "risk": self._score_to_risk_level(query_score),
            },
            "ae_reporting_rate": {
                "value": ae_rate,
                "benchmark": ae_benchmark,
                "unit": "AEs/subject",
                "score": ae_score,
                "risk": self._score_to_risk_level(ae_score),
            },
            "crf_completion": {
                "value": crf_completion,
                "target": crf_target,
                "unit": "%",
                "score": crf_score,
                "risk": self._score_to_risk_level(crf_score),
            },
            "overdue_saes": {
                "value": overdue_saes,
                "threshold": deviation_threshold,
                "unit": "overdue SAEs",
                "score": deviation_score,
                "risk": self._score_to_risk_level(deviation_score),
            },
        }

    def _compute_overall_score(self, indicators):
        """Weighted average of all risk indicators."""
        weights = {
            "enrollment_rate": 0.20,
            "query_rate": 0.25,
            "ae_reporting_rate": 0.20,
            "crf_completion": 0.20,
            "overdue_saes": 0.15,
        }
        total = sum(
            indicators[key]["score"] * weights.get(key, 0.2)
            for key in indicators
        )
        return round(total)

    def _score_to_risk_level(self, score):
        if score >= 80:
            return "low"
        elif score >= 50:
            return "medium"
        return "high"


class StudyOverviewView(APIView):
    """GET /api/v1/monitoring/study-overview/?study_id=<id>

    Returns aggregated study-level risk metrics.
    """

    permission_classes = [IsMonitoringViewer]

    def get(self, request):
        study_id = request.query_params.get("study_id")

        if not study_id:
            study = Study.objects.filter(status="active").first()
            if not study:
                study = Study.objects.first()
            if not study:
                return Response({"detail": "No studies found."}, status=404)
            study_id = study.id
        else:
            try:
                study = Study.objects.get(pk=study_id)
            except Study.DoesNotExist:
                return Response({"detail": "Study not found."}, status=404)

        sites = Site.objects.filter(study=study)
        subjects = Subject.objects.filter(study=study)
        enrolled = subjects.filter(status="enrolled")
        queries = Query.objects.filter(
            item_response__form_instance__subject__study=study
        )
        saes = AdverseEvent.objects.filter(study=study, serious=True)

        # Compute site risk counts using the risk score view logic
        risk_view = SiteRiskScoresView()
        now = timezone.now()
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for site in sites:
            indicators = risk_view._compute_site_indicators(site, study, now)
            score = risk_view._compute_overall_score(indicators)
            level = risk_view._score_to_risk_level(score)
            risk_counts[level] += 1

        # Enrollment target (estimate from study dates)
        enrollment_target = subjects.count() or 20  # Default target

        # Overall risk level
        if risk_counts["high"] > 0:
            overall_risk = "high"
        elif risk_counts["medium"] > risk_counts["low"]:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        return Response({
            "study": {
                "id": study.id,
                "name": study.name,
                "protocol_number": study.protocol_number,
                "status": study.status,
            },
            "total_sites": sites.count(),
            "high_risk_sites": risk_counts["high"],
            "medium_risk_sites": risk_counts["medium"],
            "low_risk_sites": risk_counts["low"],
            "overdue_saes": saes.filter(reporting_status="overdue").count(),
            "pending_saes": saes.filter(reporting_status="pending").count(),
            "open_queries": queries.filter(status="open").count(),
            "total_subjects": subjects.count(),
            "enrolled_subjects": enrolled.count(),
            "enrollment_vs_target": {
                "actual": enrolled.count(),
                "target": enrollment_target,
                "percent": round((enrolled.count() / max(enrollment_target, 1)) * 100),
            },
            "overall_risk_level": overall_risk,
        })
