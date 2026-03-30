# Day 3 Summary — Business Logic, Enhanced Serializers & Filtering

**Date:** March 28, 2026  
**Branch:** `feature/day3-business-logic-serializers`  
**Status:** ✅ All tests passed

---

## What Was Built

Day 3 implemented the core clinical business logic — the workflows that make HACT a production-grade, ICH-GCP compliant trial management system.

---

## 1. Study Status Workflow (FR-SM-05)

**State Machine:** `planning → active → locked → archived`

| Transition | Validation |
|------------|-----------|
| `planning → active` | Allowed freely |
| `active → locked` | Requires ALL queries resolved (open_queries == 0) |
| `locked → archived` | Allowed freely |
| Any skip (e.g., `active → archived`) | ❌ Blocked |

**Lock behavior:**
- Locked studies block edits to clinical data (subjects, visits, forms)
- **Safety data (Adverse Events, CIOMS) remains editable** — per stakeholder requirement and standard clinical practice

**Endpoint:** `POST /api/v1/clinical/studies/{id}/transition/`

---

## 2. Subject Enrollment Workflow (FR-PM-02)

**State Machine:** `screened → enrolled/screen_failed`, `enrolled → completed/discontinued`

| Action | Validation |
|--------|-----------|
| **Enroll** | Requires `consent_signed_date` + `enrollment_date`. Study must be `active`. |
| **Withdraw** | Requires `reason`. Sets status to `discontinued`. |
| **Complete** | Subject must be `enrolled`. Auto-sets `completion_date`. |

**Endpoints:**
- `POST /api/v1/clinical/subjects/{id}/enroll/`
- `POST /api/v1/clinical/subjects/{id}/withdraw/`
- `POST /api/v1/clinical/subjects/{id}/complete/`

---

## 3. Visit Window Validation (FR-SM-02)

**New Model Fields:**
- `Visit.window_before` — Days before planned day (e.g., 2)
- `Visit.window_after` — Days after planned day (e.g., 2)

**Protocol-Specific Windows:**

| Visit | Planned Day | Window | Allowed Range |
|-------|------------|--------|--------------|
| Screening | Day -14 | -14/0 | Day -28 to Day -14 |
| Baseline | Day 0 | 0/+1 | Day 0 to Day 1 |
| Day 7 | Day 7 | ±1 | Day 6 to Day 8 |
| Day 28 | Day 28 | ±3 | Day 25 to Day 31 |

**Features:**
- `Visit.get_window_range(baseline_date)` — calculates actual date range
- `SubjectVisit.is_within_window` — auto-computed on every API response
- `VisitSerializer.window_display` — human-readable (e.g., "Day 25 to Day 31")

---

## 4. Form Instance Submit/Sign Workflow (FR-DC-01)

**State Machine:** `draft → submitted → signed → locked`

| Action | What It Does |
|--------|-------------|
| **Submit** | Validates all required fields are filled. Sets `submitted_at`. |
| **Sign** | 21 CFR Part 11 e-signature — requires password re-entry. Sets `signed_by`/`signed_at`. |
| **Generate Queries** | Auto-creates queries for every missing required field. |

**Endpoints:**
- `POST /api/v1/clinical/form-instances/{id}/submit/`
- `POST /api/v1/clinical/form-instances/{id}/sign/`
- `POST /api/v1/clinical/form-instances/{id}/generate-queries/`

**Field-Level Validation in ItemResponse:**
- `number` fields — validates numeric values
- `date` fields — validates YYYY-MM-DD format
- `dropdown`/`radio` fields — validates value against `options` list
- `validation_rule` — regex validation support

---

## 5. Query Management (FR-DC-03/04)

**State Machine:** `open → answered → closed`

| Action | Who | What |
|--------|-----|------|
| **Open** | Data Manager | Auto-generated or manually created with `query_text` |
| **Answer** | Site Coordinator | Requires `response_text` explaining resolution |
| **Close** | Data Manager | Auto-sets `resolved_by` and `resolved_at` |

**Endpoints:**
- `POST /api/v1/clinical/queries/{id}/answer/`
- `POST /api/v1/clinical/queries/{id}/close/`

---

## 6. Nested Serializers (List vs Detail)

Every ViewSet now switches between flat (list) and nested (detail) serializers:

| Model | List View (GET /items/) | Detail View (GET /items/{id}/) |
|-------|------------------------|-------------------------------|
| **Study** | `site_count`, `subject_count`, `enrolled_count` | + nested `sites[]`, `visits[]`, `forms[]`, `open_queries_count` |
| **Subject** | `study_protocol`, `site_code` | + nested `subject_visits[]`, `adverse_events_count`, `form_instances_count` |
| **FormInstance** | `form_name`, `completion_percentage` | + nested `responses[]`, `queries_count` |
| **Query** | `subject_identifier`, `form_name`, `field_name` | + `current_value` |
| **Adverse Event** | `subject_identifier`, `severity_display`, `days_open` | + nested `cioms_forms[]` |
| **Lab Result** | `subject_identifier`, `flag_display`, `visit_name` | + audit fields |

---

## 7. Advanced Filtering

### New Filter Files

| File | FilterSets | Key Filters |
|------|-----------|-------------|
| `clinical/filters.py` | SubjectFilter, SubjectVisitFilter, FormInstanceFilter, QueryFilter | Date ranges, cross-model lookups, text search |
| `safety/filters.py` | AdverseEventFilter | Severity, seriousness, subject, site, date range |
| `lab/filters.py` | LabResultFilter | Test name, flag, subject, site, date range |

### Example Filter Queries
```
GET /subjects/?status=enrolled&site=13&enrollment_date_after=2026-03-01
GET /adverse-events/?serious=true&severity=moderate
GET /queries/?status=open&study=5
GET /lab-results/?flag=H&test_name_contains=ALT
```

---

## 8. Seed Data Enhancements

| Entity | Count | Details |
|--------|-------|---------|
| Form Items | 13 | Correct field types (number, text, date, dropdown, radio) with options |
| FormInstances | 6 | 3 submitted (Demographics) + 3 draft (Vital Signs) |
| ItemResponses | 17 | Filled data for demographics + partial vitals |
| Queries | 3 | 2 open (missing fields) + 1 answered (verification) |
| Visit Windows | 7 | Protocol-specific windows per visit |

---

## 9. Bug Fix — Swagger/ReDoc Documentation

**Issue:** Swagger UI and ReDoc returned 500 Internal Server Error.  
**Root Causes:**
1. Schema views inherited global `IsAuthenticated` — blocked unauthenticated access
2. Serializer field names mismatched model fields (`age_min` vs `age_lower`)

**Fix:**
- Added `permission_classes=[AllowAny]` to schema views in `urls.py`
- Fixed `ReferenceRangeSerializer` and `SampleCollectionSerializer` field names

---

## Files Changed / Created

| Action | File | What Changed |
|--------|------|-------------|
| ✏️ Modified | `clinical/models.py` | Added `window_before`, `window_after`, `get_window_range()` to Visit |
| ✏️ Rewritten | `clinical/serializers.py` | 580 lines: all workflows, validation, nested serializers |
| ✏️ Rewritten | `clinical/views.py` | 320 lines: 12 custom @action endpoints |
| ✏️ Rewritten | `safety/serializers.py` | Nested fields, SAE validation, CIOMS forms |
| ✏️ Rewritten | `safety/views.py` | List/detail switching, FilterSet |
| ✏️ Rewritten | `lab/serializers.py` | Auto-flagging, nested fields, fixed field names |
| ✏️ Rewritten | `lab/views.py` | List/detail switching, FilterSet |
| ✏️ Modified | `hact_ctms/urls.py` | AllowAny on Swagger/ReDoc |
| ✏️ Modified | `seed_data.py` | FormInstances, ItemResponses, Queries, visit windows |
| ✏️ Modified | `docker-compose.yml` | Exposed PostgreSQL on port 5433 |
| 🆕 Created | `clinical/filters.py` | 4 custom FilterSets |
| 🆕 Created | `safety/filters.py` | AdverseEventFilter |
| 🆕 Created | `lab/filters.py` | LabResultFilter |
| 🆕 Created | `clinical/migrations/0002_add_visit_window_fields.py` | Visit window migration |

---

## New API Endpoints (12 Custom Actions)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/studies/{id}/transition/` | Study status workflow |
| POST | `/subjects/{id}/enroll/` | Enroll with consent |
| POST | `/subjects/{id}/withdraw/` | Withdraw/discontinue |
| POST | `/subjects/{id}/complete/` | Mark complete |
| POST | `/form-instances/{id}/submit/` | Submit with validation |
| POST | `/form-instances/{id}/sign/` | 21 CFR Part 11 e-sign |
| POST | `/form-instances/{id}/generate-queries/` | Auto-generate queries |
| POST | `/queries/{id}/answer/` | Answer query |
| POST | `/queries/{id}/close/` | Close query |

---

## Testing Status

All 28 test cases from `docs/Day3_Postman_Testing_Guide.md` passed:

- ✅ Study workflow transitions (valid + invalid)
- ✅ Subject enrollment (with/without consent)
- ✅ Visit window display and validation
- ✅ Form instance submit/sign (completeness + e-signature)
- ✅ Query lifecycle (open → answer → close)
- ✅ Nested serializers (list vs detail)
- ✅ Advanced filtering (status, site, date range, severity)
- ✅ Search and pagination
- ✅ Swagger/ReDoc documentation
