# HACT CTMS — Complete Backend Workflow Guide

**How to use the system from scratch — step by step, in order.**

This guide explains how to manually set up and run a complete clinical trial in the HACT CTMS, without using seed data. Every step follows the real clinical trial workflow.

---

## Authentication

All API calls require a Keycloak access token:

```
POST http://localhost/auth/realms/hact/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded (form-data)

client_id:      hact-ctms
client_secret:  mk108Hu1yat2GOkpm9EpFEIHyKiMX5Kh
grant_type:     password
username:       hact-user
password:       hact-user
```

Save `access_token` → use as `Authorization: Bearer <access_token>` on every request.

---

## Phase 1: Study Setup (Study Admin)

### Step 1: Create a Study

```
POST /api/v1/clinical/studies/
{
    "name": "Malaria Treatment Trial",
    "protocol_number": "HACT-MAL-001",
    "phase": "Phase III",
    "sponsor": "HACT Foundation",
    "status": "planning",
    "start_date": "2026-04-01",
    "description": "Randomized trial of artemisinin combination therapy"
}
```

Note the `id` returned (e.g., `1`).

### Step 2: Create Sites

```
POST /api/v1/clinical/sites/
{
    "study": 1,
    "site_code": "ETH-001",
    "name": "Black Lion Hospital",
    "country": "Ethiopia",
    "city": "Addis Ababa",
    "status": "active"
}
```

Create additional sites the same way. Note each `id`.

### Step 3: Define the Visit Schedule

Visits are created **in order**, with `planned_day` relative to enrollment (Day 0):

```
POST /api/v1/clinical/visits/
{
    "study": 1,
    "visit_name": "Screening",
    "visit_order": 1,
    "planned_day": -14,
    "is_screening": true,
    "window_before": 14,
    "window_after": 0
}
```

```
POST /api/v1/clinical/visits/
{
    "study": 1,
    "visit_name": "Baseline (Day 0)",
    "visit_order": 2,
    "planned_day": 0,
    "is_baseline": true,
    "window_before": 0,
    "window_after": 1
}
```

```
POST /api/v1/clinical/visits/
{
    "study": 1,
    "visit_name": "Day 7",
    "visit_order": 3,
    "planned_day": 7,
    "window_before": 1,
    "window_after": 1
}
```

```
POST /api/v1/clinical/visits/
{
    "study": 1,
    "visit_name": "Day 28 (End of Study)",
    "visit_order": 4,
    "planned_day": 28,
    "window_before": 3,
    "window_after": 3
}
```

### Step 4: Design CRF Forms

Create forms (templates), then add fields (items) to each:

```
POST /api/v1/clinical/forms/
{
    "study": 1,
    "name": "Vital Signs",
    "version": "1.0",
    "is_active": true
}
```

Note form `id`, then add items:

```
POST /api/v1/clinical/items/
{
    "form": 1,
    "field_name": "heart_rate",
    "field_label": "Heart Rate (bpm)",
    "field_type": "number",
    "required": true,
    "order": 1
}
```

```
POST /api/v1/clinical/items/
{
    "form": 1,
    "field_name": "temperature",
    "field_label": "Temperature (C)",
    "field_type": "number",
    "required": true,
    "order": 2
}
```

```
POST /api/v1/clinical/items/
{
    "form": 1,
    "field_name": "blood_pressure",
    "field_label": "Blood Pressure (mmHg)",
    "field_type": "text",
    "required": true,
    "order": 3
}
```

**Field types:** `text`, `number`, `date`, `choice`, `boolean`

For choice fields, provide options as JSON:
```
{
    "field_type": "choice",
    "options": {"choices": ["Male", "Female", "Other"]}
}
```

### Step 5: Set Up Reference Ranges (Lab)

```
POST /api/v1/lab/reference-ranges/
{
    "study": 1,
    "test_name": "Hemoglobin",
    "gender": "all",
    "range_low": 12.0,
    "range_high": 17.5
}
```

### Step 6: Activate the Study

```
POST /api/v1/clinical/studies/1/transition/
{
    "status": "active"
}
```

> The study is now **active** — enrollment can begin.

---

## Phase 2: Enrollment (Site Coordinator)

### Step 7: Register a Subject (Screening)

```
POST /api/v1/clinical/subjects/
{
    "study": 1,
    "site": 1,
    "subject_identifier": "HACT-MAL-001-001",
    "screening_number": "SCR-001",
    "status": "screened"
}
```

Subject starts in `screened` status. Note `id`.

### Step 8: Record Screening Visit

```
POST /api/v1/clinical/subject-visits/
{
    "subject": 1,
    "visit": 1,
    "actual_date": "2026-04-02"
}
```

### Step 9: Create & Fill Screening Form

Create a form instance for this subject at this visit:

```
POST /api/v1/clinical/form-instances/
{
    "form": 1,
    "subject": 1,
    "subject_visit": 1,
    "status": "draft"
}
```

Note form instance `id`, then enter data:

```
POST /api/v1/clinical/item-responses/
{
    "form_instance": 1,
    "item": 1,
    "value": "72"
}
```

```
POST /api/v1/clinical/item-responses/
{
    "form_instance": 1,
    "item": 2,
    "value": "36.8"
}
```

```
POST /api/v1/clinical/item-responses/
{
    "form_instance": 1,
    "item": 3,
    "value": "120/80"
}
```

### Step 10: Submit the Form

```
POST /api/v1/clinical/form-instances/1/submit/
```

> Validates all required fields are filled. Returns 400 if any are missing.

### Step 11: Enroll the Subject

```
POST /api/v1/clinical/subjects/1/enroll/
{
    "consent_signed_date": "2026-04-02",
    "enrollment_date": "2026-04-02"
}
```

> **Requires** `consent_signed_date` — without it, enrollment is rejected (ICH-GCP compliance).

Subject transitions: `screened` → `enrolled`.

---

## Phase 3: Study Conduct (Data Collection)

### Step 12: Record Subsequent Visits

For each protocol visit, create a subject-visit:

```
POST /api/v1/clinical/subject-visits/
{
    "subject": 1,
    "visit": 2,
    "actual_date": "2026-04-15"
}
```

The system auto-checks if `actual_date` falls within the protocol window.

### Step 13: Data Entry Per Visit

For each visit, create form instances, fill responses, submit:

1. **Create form instance** → `POST /form-instances/`
2. **Enter data** → `POST /item-responses/`
3. **Submit** → `POST /form-instances/{id}/submit/`
4. **Sign (e-signature)** → `POST /form-instances/{id}/sign/`

### Step 14: Sign Forms (21 CFR Part 11)

```
POST /api/v1/clinical/form-instances/1/sign/
{
    "password": "hact-user",
    "meaning": "I confirm the data entered is accurate and complete."
}
```

> Requires re-entering password as electronic signature. Creates audit trail entry.

### Step 15: Import Lab Results (Bulk CSV)

Create a CSV file (`lab_results.csv`):
```csv
subject_identifier,test_name,result_value,unit,result_date
HACT-MAL-001-001,Hemoglobin,14.2,g/dL,2026-04-02
HACT-MAL-001-001,WBC,8500,cells/uL,2026-04-02
HACT-MAL-001-001,Platelets,250000,cells/uL,2026-04-02
```

Upload via Postman:
```
POST /api/v1/lab/results/import-csv/
Content-Type: multipart/form-data

Fields:
  file: [upload lab_results.csv]
  study: 1
```

> Auto-flags results H/L/N against reference ranges.

### Step 16: Record Adverse Events

```
POST /api/v1/safety/adverse-events/
{
    "subject": 1,
    "study": 1,
    "ae_term": "Headache",
    "start_date": "2026-04-10",
    "severity": "mild",
    "serious": false,
    "causality": "possible",
    "outcome": "recovered",
    "end_date": "2026-04-12",
    "action_taken": "Paracetamol 500mg administered"
}
```

For **Serious Adverse Events (SAEs)**, set `"serious": true` with criteria:

```
POST /api/v1/safety/adverse-events/
{
    "subject": 1,
    "study": 1,
    "ae_term": "Severe allergic reaction",
    "start_date": "2026-04-15",
    "severity": "severe",
    "serious": true,
    "serious_criteria": "Life-threatening, required hospitalization",
    "causality": "probable",
    "outcome": "recovering",
    "action_taken": "Study drug discontinued, IV steroids administered"
}
```

### Step 17: Generate CIOMS Form for SAE

First, create a CIOMS form record:
```
POST /api/v1/safety/cioms-forms/
{
    "adverse_event": 2,
    "regulatory_authority": "EFDA",
    "submission_deadline": "2026-04-22"
}
```

Then generate the PDF:
```
POST /api/v1/safety/cioms-forms/1/generate-pdf/
```

Download:
```
GET /api/v1/safety/cioms-forms/1/download/
```

---

## Phase 4: Data Management (Data Manager)

### Step 18: Auto-Generate Queries for Missing Data

```
POST /api/v1/clinical/form-instances/{id}/generate-queries/
```

> Creates queries for every required field that's empty.

### Step 19: Create Manual Queries

```
POST /api/v1/clinical/queries/
{
    "item_response": 1,
    "raised_by": 1,
    "query_text": "Heart rate of 72 seems low. Please verify.",
    "status": "open"
}
```

### Step 20: Answer a Query (Site Coordinator)

```
POST /api/v1/clinical/queries/{id}/answer/
{
    "response_text": "Value verified against source document. Heart rate was 72 bpm."
}
```

### Step 21: Close a Query (Data Manager)

```
POST /api/v1/clinical/queries/{id}/close/
```

### Step 22: Generate Data Quality Report

```
POST /api/v1/outputs/quality-reports/generate/
{
    "study": 1,
    "report_type": "comprehensive"
}
```

Returns traffic-light indicators:
- **Missing Data** — green/yellow/red
- **Open Queries** — green/yellow/red
- **Form Completion** — completion %
- **Visit Compliance** — within-window %
- **Enrollment Progress** — by site

---

## Phase 5: Study Completion

### Step 23: Complete or Withdraw Subjects

Complete:
```
POST /api/v1/clinical/subjects/{id}/complete/
```

Withdraw:
```
POST /api/v1/clinical/subjects/{id}/withdraw/
{
    "reason": "Patient withdrew consent"
}
```

### Step 24: Resolve ALL Open Queries

Before locking, **every query must be closed**:

```
GET /api/v1/clinical/queries/?status=open
```

For each → answer → close.

### Step 25: Export Data

CSV export:
```
POST /api/v1/outputs/snapshots/export-csv/
{"study": 1}
```

CDISC ODM XML export:
```
POST /api/v1/outputs/snapshots/export-odm/
{"study": 1}
```

Download:
```
GET /api/v1/outputs/snapshots/{id}/download/
```

### Step 26: Lock the Database

```
POST /api/v1/clinical/studies/1/transition/
{
    "status": "locked"
}
```

**This automatically:**
1. Generates a comprehensive quality report
2. Creates a frozen CSV snapshot
3. Locks ALL form instances (no more edits)

> After lock, **safety data (AEs) can still be edited** — everything else is frozen.

### Step 27: Archive the Study

```
POST /api/v1/clinical/studies/1/transition/
{
    "status": "archived"
}
```

### Step 28: Export Audit Trail

```
GET /api/v1/audit/logs/export-csv/?date_from=2026-04-01&date_to=2026-05-01
```

Downloads a CSV of all audit records for regulatory inspection.

---

## Data Flow Diagram

```
Study Setup (planning)
    │
    ├── Create Study
    ├── Create Sites
    ├── Define Visit Schedule
    ├── Design CRF Forms + Items
    ├── Set Reference Ranges
    │
    ▼
Activate Study (active)
    │
    ├── Register Subjects (screened)
    ├── Record Screening Visit
    ├── Fill Screening Forms
    ├── Enroll Subjects (screened → enrolled)
    │
    ▼
Study Conduct
    │
    ├── Record Visits
    ├── Data Entry → Submit → Sign (e-signature)
    ├── Import Lab Results (CSV)
    ├── Record Adverse Events
    ├── Generate CIOMS PDFs for SAEs
    ├── Auto/Manual Queries → Answer → Close
    │
    ▼
Data Management
    │
    ├── Quality Reports (missing data, queries, compliance)
    ├── Export CSV / CDISC ODM
    ├── Resolve ALL open queries
    │
    ▼
Lock Database (locked)
    │
    ├── Auto: Quality report + Snapshot + Lock forms
    ├── Safety data still editable
    │
    ▼
Archive Study (archived)
    │
    └── Export Audit Trail for regulatory inspection
```

---

## Status Workflows

### Study: `planning → active → locked → archived`
### Subject: `screened → enrolled → completed` or `→ discontinued`
### Form Instance: `draft → submitted → signed → locked`
### Query: `open → answered → closed`
### CIOMS Form: `draft → submitted → approved`

---

## API Endpoint Summary

| Module | Endpoint | Actions |
|--------|----------|---------|
| **Clinical** | `/studies/` | CRUD + `transition` |
| | `/sites/` | CRUD |
| | `/subjects/` | CRUD + `enroll`, `withdraw`, `complete` |
| | `/visits/` | CRUD |
| | `/subject-visits/` | CRUD |
| | `/forms/` | CRUD |
| | `/items/` | CRUD |
| | `/form-instances/` | CRUD + `submit`, `sign`, `generate-queries` |
| | `/item-responses/` | CRUD |
| | `/queries/` | CRUD + `answer`, `close` |
| **Safety** | `/adverse-events/` | CRUD |
| | `/cioms-forms/` | CRUD + `generate-pdf`, `download` |
| | `/safety-reviews/` | CRUD |
| **Lab** | `/results/` | CRUD + `import-csv` |
| | `/reference-ranges/` | CRUD |
| | `/samples/` | CRUD |
| **Outputs** | `/snapshots/` | CRUD + `export-csv`, `export-odm`, `download` |
| | `/quality-reports/` | CRUD + `generate` |
| **Audit** | `/logs/` | READ + `export-csv` |
| **Ops** | `/contracts/` | CRUD |
| | `/training-records/` | CRUD |
| | `/milestones/` | CRUD |
| **Accounts** | `/users/` | CRUD |
| | `/roles/` | CRUD |
| | `/user-roles/` | CRUD |
| | `/site-staff/` | CRUD |
