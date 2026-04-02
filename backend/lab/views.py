"""Lab views — ViewSets with RBAC, enhanced serializers, and filtering."""

import csv
import io
from decimal import Decimal, InvalidOperation

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from core.mixins import AuditCreateMixin
from core.permissions import IsLabManager

from .filters import LabResultFilter
from .models import LabResult, ReferenceRange, SampleCollection
from .serializers import (
    LabResultDetailSerializer, LabResultListSerializer,
    ReferenceRangeSerializer, SampleCollectionSerializer,
)


class LabResultViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Lab result management with enhanced filtering and auto-flagging.

    Custom actions:
    - POST /results/import-csv/ — Bulk import lab results from CSV
    """

    queryset = LabResult.objects.select_related(
        "subject", "subject__site", "subject_visit",
        "subject_visit__visit", "imported_by",
    ).all()
    permission_classes = [IsLabManager]
    search_fields = ["test_name"]
    filterset_class = LabResultFilter
    ordering_fields = ["result_date", "test_name", "flag", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return LabResultListSerializer
        return LabResultDetailSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="import-csv",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_csv(self, request):
        """Bulk import lab results from a CSV file.

        POST /api/v1/lab/results/import-csv/
        Body: form-data with "file" (CSV) and "study" (study ID)

        CSV columns (required):
            subject_identifier, test_name, result_value, unit, result_date

        Auto-flags results (H/L/N) based on study reference ranges.
        """
        csv_file = request.FILES.get("file")
        study_id = request.data.get("study")

        if not csv_file:
            return Response(
                {"detail": "No CSV file provided. Upload as 'file' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not study_id:
            return Response(
                {"detail": "Study ID required. Provide 'study' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not csv_file.name.endswith(".csv"):
            return Response(
                {"detail": "File must be a .csv file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse CSV
        try:
            decoded = csv_file.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(decoded))
        except Exception as e:
            return Response(
                {"detail": f"Failed to parse CSV: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        required_cols = {"subject_identifier", "test_name", "result_value", "unit", "result_date"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            return Response(
                {"detail": f"Missing CSV columns: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Load reference ranges for this study
        from clinical.models import Subject

        ref_ranges = {}
        for rr in ReferenceRange.objects.filter(study_id=study_id):
            ref_ranges[rr.test_name.lower()] = rr

        # Process rows
        created = []
        errors = []
        for row_num, row in enumerate(reader, start=2):
            subj_id = row.get("subject_identifier", "").strip()
            test_name = row.get("test_name", "").strip()
            result_value = row.get("result_value", "").strip()
            unit = row.get("unit", "").strip()
            result_date = row.get("result_date", "").strip()

            if not all([subj_id, test_name, result_value, result_date]):
                errors.append({"row": row_num, "error": "Missing required field(s)."})
                continue

            # Find subject
            try:
                subject = Subject.objects.get(
                    subject_identifier=subj_id, study_id=study_id
                )
            except Subject.DoesNotExist:
                errors.append({"row": row_num, "error": f"Subject '{subj_id}' not found."})
                continue

            # Auto-flag against reference range
            flag = ""
            ref_low = None
            ref_high = None
            rr = ref_ranges.get(test_name.lower())
            if rr:
                ref_low = rr.range_low
                ref_high = rr.range_high
                try:
                    val = Decimal(result_value)
                    if val < rr.range_low:
                        flag = "L"
                    elif val > rr.range_high:
                        flag = "H"
                    else:
                        flag = "N"
                except (InvalidOperation, ValueError):
                    flag = ""

            # Create lab result
            try:
                lr = LabResult.objects.create(
                    subject=subject,
                    test_name=test_name,
                    result_value=result_value,
                    unit=unit,
                    reference_range_low=ref_low,
                    reference_range_high=ref_high,
                    flag=flag,
                    result_date=result_date,
                    imported_by=request.user,
                )
                created.append({
                    "row": row_num,
                    "id": lr.id,
                    "subject": subj_id,
                    "test": test_name,
                    "value": result_value,
                    "flag": flag or "—",
                })
            except Exception as e:
                errors.append({"row": row_num, "error": str(e)})

        return Response({
            "detail": f"Import complete: {len(created)} created, {len(errors)} errors.",
            "imported_count": len(created),
            "error_count": len(errors),
            "imported": created,
            "errors": errors,
        }, status=status.HTTP_201_CREATED)


class ReferenceRangeViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Reference range management."""

    queryset = ReferenceRange.objects.select_related("study").all()
    serializer_class = ReferenceRangeSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["study", "test_name", "gender"]


class SampleCollectionViewSet(AuditCreateMixin, viewsets.ModelViewSet):
    """Sample collection tracking."""

    queryset = SampleCollection.objects.select_related("subject").all()
    serializer_class = SampleCollectionSerializer
    permission_classes = [IsLabManager]
    filterset_fields = ["subject", "status", "sample_type"]

