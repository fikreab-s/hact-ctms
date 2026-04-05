# HACT CTMS — Backend System Workflow Guide

> Complete guide explaining how the system works and how to manually insert data
> step-by-step through the API (Postman, curl, or Swagger).

---

## System Overview (The Big Picture)

The HACT CTMS follows a clinical trial lifecycle. Data must be entered in a
**strict sequential order** because of foreign key dependencies:

```
Study → Site → Subject → Visit → SubjectVisit → Form → Item → FormInstance → ItemResponse → Query
                 ↓                                                              ↓
              Enroll                                                     Answer / Close
                 ↓
         Adverse Events (Safety)
         Lab Results (Lab)
```

---

## How Authentication Works

Every API call (except health check) requires a **Bearer token** from Keycloak.

### Get a Token
```
POST http://localhost/auth/realms/hact/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

client_id=hact-ctms-frontend
grant_type=password
username=hact-user
password=hact-user
```

**Response:** `{ "access_token": "eyJhbGc...", "expires_in": 300 }`

### Use the Token
Add this header to ALL subsequent API calls:
```
Authorization: Bearer eyJhbGc...
```

> In **Postman**: Set `Authorization → Type → Bearer Token → paste the token`

---

## Step-by-Step Data Entry (Full Trial Simulation)

### BASE URL: `http://localhost/api/v1`

---

### Step 1: Create a Study
**WHO:** `study_admin`  
**Endpoint:** `POST /api/v1/clinical/studies/`

```json
{
  "name": "Phase III RCT of Antimalarial Compound X",
  "protocol_number": "HACT-2026-002",
  "phase": "III",
  "sponsor": "Horn of Africa Clinical Trials",
  "start_date": "2026-04-01"
}
```

**Response:** `201 Created` → Note the returned `id` (e.g., `1`)

**Status:** Study starts as `planning`

```
Study lifecycle:  planning → active → locked → archived
                     ↓          ↓         ↓
              (setup phase) (data entry) (frozen)
```

---

### Step 2: Create Sites Under the Study
**WHO:** `study_admin`  
**Endpoint:** `POST /api/v1/clinical/sites/`

```json
{
  "study": 1,
  "site_code": "ETH-ADD-001",
  "name": "Tikur Anbessa Hospital — Addis Ababa",
  "country": "Ethiopia",
  "principal_investigator": "Dr. Turemo Bedaso",
  "status": "active",
  "activation_date": "2026-04-01"
}
```

Create a second site:
```json
{
  "study": 1,
  "site_code": "ETH-HAW-002",
  "name": "Hawassa University Referral Hospital",
  "country": "Ethiopia",
  "principal_investigator": "Dr. Fatima Ali",
  "status": "active"
}
```

> **Note:** `site_code` must be unique per study.

---

### Step 3: Activate the Study
**WHO:** `study_admin`  
**Endpoint:** `POST /api/v1/clinical/studies/1/transition/`

```json
{
  "status": "active"
}
```

> ⚠️ Subjects can only be enrolled into **active** studies.

---

### Step 4: Define the Visit Schedule
**WHO:** `study_admin`  
**Endpoint:** `POST /api/v1/clinical/visits/`

Create visits in order:

```json
// Screening visit
{
  "study": 1,
  "visit_name": "Screening",
  "visit_order": 1,
  "planned_day": -7,
  "window_before": 3,
  "window_after": 0,
  "is_screening": true
}
```
```json
// Baseline visit (Day 0)
{
  "study": 1,
  "visit_name": "Baseline (Day 0)",
  "visit_order": 2,
  "planned_day": 0,
  "window_before": 0,
  "window_after": 1,
  "is_baseline": true
}
```
```json
// Follow-up visit (Day 14)
{
  "study": 1,
  "visit_name": "Follow-up (Day 14)",
  "visit_order": 3,
  "planned_day": 14,
  "window_before": 2,
  "window_after": 2,
  "is_follow_up": true
}
```
```json
// End of study visit (Day 28)
{
  "study": 1,
  "visit_name": "End of Study (Day 28)",
  "visit_order": 4,
  "planned_day": 28,
  "window_before": 3,
  "window_after": 3,
  "is_follow_up": true
}
```

---

### Step 5: Define CRF Forms and Fields
**WHO:** `data_manager`  

#### 5a. Create a Form
**Endpoint:** `POST /api/v1/clinical/forms/`

```json
{
  "study": 1,
  "name": "Demographics",
  "version": "1.0",
  "description": "Baseline demographics CRF"
}
```

Note the `id` (e.g., `1`)

#### 5b. Create Items (Fields) for the Form
**Endpoint:** `POST /api/v1/clinical/items/`

```json
{
  "form": 1,
  "field_name": "age",
  "field_label": "Age (years)",
  "field_type": "number",
  "required": true,
  "order": 1
}
```
```json
{
  "form": 1,
  "field_name": "sex",
  "field_label": "Sex",
  "field_type": "dropdown",
  "required": true,
  "order": 2,
  "options": [
    {"value": "M", "label": "Male"},
    {"value": "F", "label": "Female"}
  ]
}
```
```json
{
  "form": 1,
  "field_name": "weight_kg",
  "field_label": "Weight (kg)",
  "field_type": "number",
  "required": true,
  "order": 3
}
```

---

### Step 6: Screen Subjects
**WHO:** `data_manager`  
**Endpoint:** `POST /api/v1/clinical/subjects/`

```json
{
  "study": 1,
  "site": 1,
  "subject_identifier": "HACT-001-001",
  "screening_number": "SCR-001"
}
```

**Status:** Subject starts as `screened`

```
Subject lifecycle:  screened → enrolled → completed
                                   ↓
                             discontinued
```

---

### Step 7: Enroll the Subject
**WHO:** `site_coordinator`  
**Endpoint:** `POST /api/v1/clinical/subjects/1/enroll/`

```json
{
  "consent_signed_date": "2026-04-05",
  "enrollment_date": "2026-04-05"
}
```

> ⚠️ Study must be `active` and subject must be `screened`.

---

### Step 8: Schedule Subject Visits
**WHO:** `data_manager`  
**Endpoint:** `POST /api/v1/clinical/subject-visits/`

```json
{
  "subject": 1,
  "visit": 2,
  "scheduled_date": "2026-04-05",
  "actual_date": "2026-04-05",
  "status": "completed"
}
```

---

### Step 9: Fill Out a CRF (Data Entry)
**WHO:** `site_coordinator`

#### 9a. Create a Form Instance
**Endpoint:** `POST /api/v1/clinical/form-instances/`

```json
{
  "form": 1,
  "subject": 1,
  "subject_visit": 1,
  "instance_number": 1
}
```

Note the `id` (e.g., `1`). Status starts as `draft`.

#### 9b. Enter Data (Item Responses)
**Endpoint:** `POST /api/v1/clinical/item-responses/`

```json
{ "form_instance": 1, "item": 1, "value": "34" }
```
```json
{ "form_instance": 1, "item": 2, "value": "M" }
```
```json
{ "form_instance": 1, "item": 3, "value": "72.5" }
```

#### 9c. Submit the Form
**Endpoint:** `POST /api/v1/clinical/form-instances/1/submit/`

```json
{}
```

Status changes: `draft` → `submitted`

#### 9d. Sign the Form (21 CFR Part 11)
**Endpoint:** `POST /api/v1/clinical/form-instances/1/sign/`

```json
{
  "password": "hact-user",
  "meaning": "I confirm this data is accurate and complete."
}
```

Status changes: `submitted` → `signed`

```
Form lifecycle:  draft → submitted → signed → locked
                          (nurse)    (PI signs)  (study lock)
```

---

### Step 10: Raise a Data Query
**WHO:** `data_manager`  
**Endpoint:** `POST /api/v1/clinical/queries/`

```json
{
  "item_response": 1,
  "query_text": "Age value seems too low. Please verify."
}
```

Or auto-generate queries for missing required fields:
```
POST /api/v1/clinical/form-instances/1/generate-queries/
```

#### Answer the Query (Site Coordinator)
**Endpoint:** `POST /api/v1/clinical/queries/1/answer/`

```json
{
  "response_text": "Confirmed — patient is 34 years old."
}
```

#### Close the Query (Data Manager)
**Endpoint:** `POST /api/v1/clinical/queries/1/close/`

```json
{}
```

```
Query lifecycle:  open → answered → closed
                  (DM)    (SC)      (DM)
```

---

### Step 11: Report Adverse Events
**WHO:** `safety_officer`  
**Endpoint:** `POST /api/v1/safety/adverse-events/`

```json
{
  "subject": 1,
  "study": 1,
  "ae_term": "Headache",
  "severity": "mild",
  "serious": false,
  "causality": "unlikely",
  "outcome": "recovered",
  "start_date": "2026-04-10",
  "end_date": "2026-04-12",
  "description": "Mild headache lasting 2 days after first dose."
}
```

For a **Serious** adverse event (SAE):
```json
{
  "subject": 1,
  "study": 1,
  "ae_term": "Severe allergic reaction",
  "severity": "severe",
  "serious": true,
  "causality": "probable",
  "outcome": "recovering",
  "start_date": "2026-04-15",
  "description": "Anaphylactic reaction requiring hospitalization."
}
```

---

### Step 12: Enter Lab Results
**WHO:** `lab_manager`  
**Endpoint:** `POST /api/v1/lab/results/`

```json
{
  "subject": 1,
  "subject_visit": 1,
  "test_name": "Hemoglobin",
  "result_value": "14.2",
  "unit": "g/dL",
  "reference_range_low": "12.0",
  "reference_range_high": "17.5",
  "flag": "N",
  "result_date": "2026-04-05"
}
```

Flags: `N` = Normal, `H` = High, `L` = Low

---

### Step 13: Lock the Study
**WHO:** `study_admin`  
**Endpoint:** `POST /api/v1/clinical/studies/1/transition/`

```json
{
  "status": "locked",
  "reason": "Database lock for primary analysis"
}
```

**This automatically:**
1. Generates a data quality report
2. Creates a frozen dataset snapshot (CSV ZIP)
3. Locks all form instances (`draft/submitted` → `locked`)

> ⚠️ After locking, no data changes are allowed.

---

### Step 14: Export Data
**WHO:** `data_manager`  

**Export CSV:**
```
GET /api/v1/outputs/snapshots/1/export-csv/
```

**Export ODM XML:**
```
GET /api/v1/outputs/snapshots/1/export-odm/
```

---

### Step 15: View Audit Trail
**WHO:** `auditor`  
**Endpoint:** `GET /api/v1/audit/logs/`

Every create, update, and delete action is recorded with:
- Timestamp
- User who made the change
- Table name
- Record ID
- Before/after values (JSONB)

---

## Complete Entity Relationship Summary

```
Study (1) ──── (N) Site
  │                  │
  │                  └── (N) Subject ──── (N) SubjectVisit
  │                           │                    │
  │                           │                    └── FormInstance → ItemResponse → Query
  │                           │
  │                           ├── AdverseEvent (Safety)
  │                           └── LabResult (Lab)
  │
  ├── (N) Visit (schedule template)
  ├── (N) Form ──── (N) Item
  └── (N) DatasetSnapshot, QualityReport (Outputs)
```

---

## API Quick Reference

| Step | Method | Endpoint | Role |
|------|--------|----------|------|
| Auth | POST | `/auth/realms/hact/protocol/openid-connect/token` | any |
| My profile | GET | `/api/v1/accounts/auth/me/` | any |
| Create study | POST | `/api/v1/clinical/studies/` | study_admin |
| List studies | GET | `/api/v1/clinical/studies/` | any |
| Transition study | POST | `/api/v1/clinical/studies/{id}/transition/` | study_admin |
| Create site | POST | `/api/v1/clinical/sites/` | study_admin |
| Create visit | POST | `/api/v1/clinical/visits/` | study_admin |
| Create subject | POST | `/api/v1/clinical/subjects/` | data_manager |
| Enroll subject | POST | `/api/v1/clinical/subjects/{id}/enroll/` | site_coordinator |
| Withdraw subject | POST | `/api/v1/clinical/subjects/{id}/withdraw/` | site_coordinator |
| Create form | POST | `/api/v1/clinical/forms/` | data_manager |
| Create item | POST | `/api/v1/clinical/items/` | data_manager |
| Create form instance | POST | `/api/v1/clinical/form-instances/` | site_coordinator |
| Enter data | POST | `/api/v1/clinical/item-responses/` | site_coordinator |
| Submit form | POST | `/api/v1/clinical/form-instances/{id}/submit/` | site_coordinator |
| Sign form | POST | `/api/v1/clinical/form-instances/{id}/sign/` | site_coordinator |
| Create query | POST | `/api/v1/clinical/queries/` | data_manager |
| Answer query | POST | `/api/v1/clinical/queries/{id}/answer/` | site_coordinator |
| Close query | POST | `/api/v1/clinical/queries/{id}/close/` | data_manager |
| Create AE | POST | `/api/v1/safety/adverse-events/` | safety_officer |
| Create lab result | POST | `/api/v1/lab/results/` | lab_manager |
| View audit | GET | `/api/v1/audit/logs/` | auditor |
| Export CSV | GET | `/api/v1/outputs/snapshots/{id}/export-csv/` | data_manager |

---

## Swagger UI

For interactive API testing with auto-generated docs:
```
http://localhost/api/v1/docs/
```

This shows all endpoints, request/response schemas, and lets you try them directly.
