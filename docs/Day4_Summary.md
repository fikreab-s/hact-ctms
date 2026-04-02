# Day 4 Summary — Data Export, Quality Reports & Testing

**Date:** March 30, 2026  
**Branch:** `feature/day4-export-quality-tests`  
**Status:** ✅ Complete — 27/27 automated tests passing

---

## What Was Built

### 1. Study Lock — Full Database Freeze
When a study transitions to `locked`, the system now automatically:

| Step | Action | Details |
|------|--------|---------|
| 1 | **Quality Report** | Generates a comprehensive data quality report (missing data, queries, enrollment, completion, visit compliance) |
| 2 | **Dataset Snapshot** | Creates a frozen CSV ZIP of all study data (subjects, visits, forms, AEs, lab results, queries) |
| 3 | **Form Lock** | Transitions all form instances (draft/submitted/signed) to `locked` status |

**Endpoint:** `POST /api/v1/clinical/studies/{id}/transition/`  
**Body:** `{"status": "locked"}`

---

### 2. CSV Data Export

Six CSV files bundled into a single ZIP:

| File | Contents |
|------|----------|
| `subjects.csv` | Subject demographics, enrollment status, consent dates |
| `visits.csv` | Visit schedule with window compliance (within/outside window) |
| `form_data.csv` | All form responses with field-level detail |
| `adverse_events.csv` | Adverse event listing with severity, causality, outcome |
| `lab_results.csv` | Lab results with reference ranges and flags |
| `queries.csv` | Data queries with full lifecycle info |

**Endpoint:** `POST /api/v1/outputs/snapshots/export-csv/`  
**Body:** `{"study": 5}`

Files saved to: `media/exports/<protocol>/` (swappable to Nextcloud on Day 9)

---

### 3. CDISC ODM 1.3.2 XML Export

Full regulatory-standard XML export with:
- `<Study>` — GlobalVariables, MetaDataVersion
- `<StudyEventDef>` — One per visit
- `<FormDef>` + `<ItemGroupDef>` + `<ItemDef>` — Per form/field
- `<ClinicalData>` — SubjectData → StudyEventData → FormData → ItemData

**Endpoint:** `POST /api/v1/outputs/snapshots/export-odm/`  
**Body:** `{"study": 5}`

> **Note:** This provides CDISC ODM for data exchange. Full SDTM submission-ready packages use OpenClinica + ETL tools (Day 7-8).

---

### 4. Data Quality Reports

Quality calculation engine with 5 metrics + traffic-light summary:

| Metric | What It Measures |
|--------|-----------------|
| **Missing Data** | Required fields without values across all forms |
| **Query Status** | Open/answered/closed counts with resolution rate |
| **Enrollment** | Enrolled vs total subjects by site |
| **Form Completion** | % of forms submitted and signed per form type |
| **Visit Compliance** | % of visits within protocol-defined windows |

**Summary Output:** Traffic-light indicators (green/yellow/red) for dashboard display.

**Endpoint:** `POST /api/v1/outputs/quality-reports/generate/`  
**Body:** `{"study": 5, "report_type": "comprehensive"}`

Report types: `missing_data`, `query_status`, `enrollment`, `completion`, `visit_compliance`, `comprehensive`

---

### 5. Automated Test Suite — 27 Tests

| Category | Tests | Status |
|----------|-------|--------|
| Study Transitions | 4 (valid, invalid, lock blocked by queries, lock with snapshot) | ✅ Pass |
| Subject Enrollment | 4 (enroll, no consent, re-enroll, withdraw) | ✅ Pass |
| Form Instance | 4 (submit incomplete, submit complete, sign, wrong password) | ✅ Pass |
| Query Lifecycle | 4 (answer, close, close-closed, auto-generate) | ✅ Pass |
| Visit Windows | 4 (range calc, screening, within, outside) | ✅ Pass |
| CSV Export | 2 (zip creation, invalid study) | ✅ Pass |
| ODM Export | 1 (XML creation) | ✅ Pass |
| Quality Reports | 3 (comprehensive, missing data, invalid study) | ✅ Pass |
| Study Lock | 1 (snapshot + report + form lock) | ✅ Pass |

---

## Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `backend/outputs/services.py` | CSV export service (6 individual exports + ZIP bundler) |
| `backend/outputs/odm_export.py` | CDISC ODM 1.3.2 XML generator |
| `backend/outputs/quality.py` | Data quality calculation engine (5 metrics + summary) |

### Modified Files
| File | Changes |
|------|---------|
| `backend/outputs/serializers.py` | List/Detail pattern + action serializers for export/quality |
| `backend/outputs/views.py` | Custom actions: export-csv, export-odm, download, generate |
| `backend/clinical/views.py` | Study lock now auto-creates snapshot + quality report + locks forms |
| `backend/clinical/tests.py` | 20 unit tests for Day 3 business logic |
| `backend/outputs/tests.py` | 7 unit tests for Day 4 exports and reports |

---

## API Endpoints Added

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/outputs/snapshots/export-csv/` | Generate CSV ZIP export |
| POST | `/api/v1/outputs/snapshots/export-odm/` | Generate CDISC ODM XML |
| GET | `/api/v1/outputs/snapshots/{id}/download/` | Download export file |
| POST | `/api/v1/outputs/quality-reports/generate/` | Generate quality report |

---

## External Systems Alignment

| Feature | Django (Now) | External System (Future) |
|---------|-------------|-------------------------|
| E-Signature | AuditLog with `action="sign"` + FormInstance.signed_by | OpenClinica native e-sig (Day 7) |
| DB Lock | Study transition → snapshot + lock forms | OpenClinica DB lock via API (Day 8) |
| CSV Export | Django `media/exports/` folder | Nextcloud WebDAV upload (Day 9) |
| CDISC Export | Basic ODM 1.3.2 XML | OpenClinica CDISC ODM + SAS/Pinnacle 21 ETL (Day 8) |
| Quality Reports | On-demand via API | Celery Beat scheduled (future) |

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| No dedicated ESignature model | AuditLog + FormInstance.signed_by covers 21 CFR Part 11; OpenClinica handles CRF signing natively |
| CSV saved to Django media folder | Swappable to Nextcloud WebDAV on Day 9 with zero API changes |
| Quality reports on-demand only | Celery Beat scheduling will be added when daily reports are needed |
| CDISC ODM (not raw SDTM) | ODM is the standard exchange format; SDTM requires ETL tools that OpenClinica integrates with |
| Superuser test users | Tests focus on business logic, not RBAC (RBAC tested separately) |
