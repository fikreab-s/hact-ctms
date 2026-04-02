# Day 3 — Postman Testing Guide

## Prerequisites

### Step 0: Get Access Token
All requests need the `Authorization: Bearer <token>` header.

**Request:**
```
POST http://localhost/auth/realms/hact/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded (form-data)

client_id:      hact-ctms
client_secret:  mk108Hu1yat2GOkpm9EpFEIHyKiMX5Kh
grant_type:     password
username:       hact-user
password:       hact-user
```

Copy the `access_token` from the response. Use it as:
```
Authorization: Bearer <paste_token_here>
```

---

## Test 1 — Study Status Workflow (FR-SM-05)

### 1a. GET Study Detail (nested response)
```
GET http://localhost/api/v1/clinical/studies/5/
Authorization: Bearer <token>
```
**Expected:** 200 OK with nested `sites[]`, `visits[]`, `forms[]`, plus `site_count`, `subject_count`, `enrolled_count`, `open_queries_count`.

### 1b. GET Study List (flat with counts)
```
GET http://localhost/api/v1/clinical/studies/
Authorization: Bearer <token>
```
**Expected:** 200 OK — flat list with `site_count`, `subject_count`, `enrolled_count` per study.

### 1c. Invalid Transition (should FAIL)
```
POST http://localhost/api/v1/clinical/studies/5/transition/
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "archived"
}
```
**Expected:** 400 Bad Request — "Cannot transition from 'active' to 'archived'. Allowed: ['locked']"

### 1d. Try to Lock (should FAIL — open queries exist)
```
POST http://localhost/api/v1/clinical/studies/5/transition/
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "locked"
}
```
**Expected:** 400 Bad Request — "Cannot lock study: 2 open queries remain."

---

## Test 2 — Subject Enrollment Workflow (FR-PM-02)

### 2a. Enroll a Screened Subject
Subject 44 (HACT-001-004) is `screened`.
```
POST http://localhost/api/v1/clinical/subjects/44/enroll/
Authorization: Bearer <token>
Content-Type: application/json

{
    "consent_signed_date": "2026-03-25",
    "enrollment_date": "2026-03-25"
}
```
**Expected:** 200 OK — "Subject HACT-001-004 enrolled successfully."

### 2b. Enroll Without Consent (should FAIL)
Subject 49 (HACT-002-003) is `screened`.
```
POST http://localhost/api/v1/clinical/subjects/49/enroll/
Authorization: Bearer <token>
Content-Type: application/json

{
    "enrollment_date": "2026-03-25"
}
```
**Expected:** 400 Bad Request — consent_signed_date is required.

### 2c. Enroll Already Enrolled (should FAIL)
```
POST http://localhost/api/v1/clinical/subjects/41/enroll/
Authorization: Bearer <token>
Content-Type: application/json

{
    "consent_signed_date": "2026-03-25"
}
```
**Expected:** 400 Bad Request — "Cannot enroll: subject is 'enrolled', not 'screened'."

### 2d. Withdraw an Enrolled Subject
```
POST http://localhost/api/v1/clinical/subjects/46/withdraw/
Authorization: Bearer <token>
Content-Type: application/json

{
    "reason": "Patient withdrawal of consent",
    "completion_date": "2026-03-28"
}
```
**Expected:** 200 OK — "Subject HACT-001-006 withdrawn."

### 2e. Complete an Enrolled Subject
```
POST http://localhost/api/v1/clinical/subjects/47/complete/
Authorization: Bearer <token>
Content-Type: application/json
```
**Expected:** 200 OK — "Subject HACT-002-001 completed the study."

---

## Test 3 — Visit Window Validation (FR-SM-02)

### 3a. GET Visits (check window_display)
```
GET http://localhost/api/v1/clinical/visits/?study=5
Authorization: Bearer <token>
```
**Expected:** Each visit shows `window_before`, `window_after`, and `window_display` (e.g., "Day -28 to Day -14" for Screening).

### 3b. GET Subject Visits (check is_within_window)
```
GET http://localhost/api/v1/clinical/subject-visits/?subject=41
Authorization: Bearer <token>
```
**Expected:** Each subject visit shows `is_within_window` (true/false/null), `visit_name`, `visit_order`, `planned_day`.

---

## Test 4 — Form Instance Data Entry (FR-DC-01)

### 4a. GET Form Instance Detail (nested responses)
Find a draft form instance (Vital Signs). Check FormInstance IDs from Test 1a study detail response, or use:
```
GET http://localhost/api/v1/clinical/form-instances/?status=draft
Authorization: Bearer <token>
```
Then get the detail (replace ID):
```
GET http://localhost/api/v1/clinical/form-instances/{draft_fi_id}/
Authorization: Bearer <token>
```
**Expected:** 200 OK with `responses[]`, `queries_count`, `open_queries_count`, `completion_percentage`.

### 4b. Submit a Draft Form (should FAIL — missing required fields)
Use the draft Vital Signs form instance ID:
```
POST http://localhost/api/v1/clinical/form-instances/{draft_fi_id}/submit/
Authorization: Bearer <token>
Content-Type: application/json

{}
```
**Expected:** 400 Bad Request — "2 required field(s) are missing: Heart Rate (bpm), Temperature (°C)"

### 4c. GET Form Detail with Items
```
GET http://localhost/api/v1/clinical/forms/?study=5
Authorization: Bearer <token>
```
Pick a form ID and get detail:
```
GET http://localhost/api/v1/clinical/forms/{form_id}/
Authorization: Bearer <token>
```
**Expected:** Nested `items[]` with `field_name`, `field_type`, `required`, `options`.

### 4d. Enter Data — Add Missing Item Responses
First, find the item IDs for heart_rate and temperature from the form detail above. Then create responses:
```
POST http://localhost/api/v1/clinical/item-responses/
Authorization: Bearer <token>
Content-Type: application/json

{
    "form_instance": {draft_fi_id},
    "item": {heart_rate_item_id},
    "value": "72"
}
```
And:
```
POST http://localhost/api/v1/clinical/item-responses/
Authorization: Bearer <token>
Content-Type: application/json

{
    "form_instance": {draft_fi_id},
    "item": {temperature_item_id},
    "value": "36.8"
}
```
**Expected:** 201 Created for each.

### 4e. Submit Draft Form (should SUCCEED now)
```
POST http://localhost/api/v1/clinical/form-instances/{draft_fi_id}/submit/
Authorization: Bearer <token>
Content-Type: application/json

{}
```
**Expected:** 200 OK — "Form 'Vital Signs' submitted successfully."

### 4f. Sign Submitted Form (21 CFR Part 11 e-signature)
```
POST http://localhost/api/v1/clinical/form-instances/{draft_fi_id}/sign/
Authorization: Bearer <token>
Content-Type: application/json

{
    "password": "Test@2026!",
    "meaning": "I have reviewed this data and confirm it is accurate."
}
```
**Expected:** 200 OK — "Form signed by hact-user."

### 4g. Type Validation — Enter Invalid Number
```
POST http://localhost/api/v1/clinical/item-responses/
Authorization: Bearer <token>
Content-Type: application/json

{
    "form_instance": {another_draft_fi_id},
    "item": {number_item_id},
    "value": "not-a-number"
}
```
**Expected:** 400 Bad Request — "expects a numeric value."

---

## Test 5 — Query Management (FR-DC-03/04)

### 5a. GET Queries List
```
GET http://localhost/api/v1/clinical/queries/
Authorization: Bearer <token>
```
**Expected:** List with `subject_identifier`, `form_name`, `field_name`, `raised_by_username`.

### 5b. Answer an Open Query
Use an open query ID (4 or 5):
```
POST http://localhost/api/v1/clinical/queries/4/answer/
Authorization: Bearer <token>
Content-Type: application/json

{
    "response_text": "Value has been entered. Heart rate is 72 bpm."
}
```
**Expected:** 200 OK — "Query answered successfully."

### 5c. Close a Query
```
POST http://localhost/api/v1/clinical/queries/4/close/
Authorization: Bearer <token>
Content-Type: application/json

{}
```
**Expected:** 200 OK — "Query closed successfully." Sets `resolved_by` and `resolved_at`.

### 5d. Auto-Generate Queries
Use a draft form instance with missing required fields:
```
POST http://localhost/api/v1/clinical/form-instances/{draft_fi_id}/generate-queries/
Authorization: Bearer <token>
Content-Type: application/json

{}
```
**Expected:** 200 OK — "X queries generated."

---

## Test 6 — Nested Serializers

### 6a. Subject Detail (nested visits + counts)
```
GET http://localhost/api/v1/clinical/subjects/41/
Authorization: Bearer <token>
```
**Expected:** Nested `subject_visits[]` (with `visit_name`, `is_within_window`), `adverse_events_count`, `form_instances_count`.

### 6b. Subject Visit Detail (nested form instances)
```
GET http://localhost/api/v1/clinical/subject-visits/{sv_id}/
Authorization: Bearer <token>
```
**Expected:** Nested `form_instances[]`.

### 6c. Adverse Event Detail (nested CIOMS)
```
GET http://localhost/api/v1/safety/adverse-events/
Authorization: Bearer <token>
```
**Expected:** `subject_identifier`, `site_code`, `study_protocol`, `severity_display`, `days_open`.

---

## Test 7 — Advanced Filtering

### 7a. Filter Subjects by Status
```
GET http://localhost/api/v1/clinical/subjects/?status=enrolled
Authorization: Bearer <token>
```
**Expected:** Only enrolled subjects.

### 7b. Filter Subjects by Site
```
GET http://localhost/api/v1/clinical/subjects/?site=13
Authorization: Bearer <token>
```
**Expected:** Only subjects at site ETH-001.

### 7c. Filter by Date Range
```
GET http://localhost/api/v1/clinical/subjects/?enrollment_date_after=2026-03-01&enrollment_date_before=2026-03-31
Authorization: Bearer <token>
```
**Expected:** Subjects enrolled in March 2026.

### 7d. Filter AEs by Severity
```
GET http://localhost/api/v1/safety/adverse-events/?severity=mild
Authorization: Bearer <token>
```
**Expected:** Only mild AEs.

### 7e. Filter AEs by Seriousness
```
GET http://localhost/api/v1/safety/adverse-events/?serious=true
Authorization: Bearer <token>
```
**Expected:** Only SAEs.

### 7f. Filter Queries by Status
```
GET http://localhost/api/v1/clinical/queries/?status=open
Authorization: Bearer <token>
```
**Expected:** Only open queries.

### 7g. Filter Form Instances by Status
```
GET http://localhost/api/v1/clinical/form-instances/?status=draft
Authorization: Bearer <token>
```
**Expected:** Only draft form instances.

---

## Test 8 — Search & Pagination

### 8a. Search Subjects
```
GET http://localhost/api/v1/clinical/subjects/?search=HACT-001
Authorization: Bearer <token>
```
**Expected:** Only subjects with "HACT-001" in identifier.

### 8b. Search with Ordering
```
GET http://localhost/api/v1/clinical/subjects/?ordering=-enrollment_date
Authorization: Bearer <token>
```
**Expected:** Subjects ordered by enrollment date (newest first).

### 8c. Pagination
```
GET http://localhost/api/v1/clinical/subjects/?page=1&page_size=3
Authorization: Bearer <token>
```
**Expected:** First page with 3 results, `count`, `next`, `previous` fields.

---

## Summary Checklist

| Test | Endpoint | Expected Status |
|------|----------|----------------|
| 1a | GET `/studies/5/` | 200 — nested detail |
| 1b | GET `/studies/` | 200 — flat list |
| 1c | POST `/studies/5/transition/` (invalid) | 400 — blocked |
| 1d | POST `/studies/5/transition/` (lock) | 400 — open queries |
| 2a | POST `/subjects/44/enroll/` | 200 — enrolled |
| 2b | POST `/subjects/49/enroll/` (no consent) | 400 — blocked |
| 2c | POST `/subjects/41/enroll/` (already enrolled) | 400 — blocked |
| 2d | POST `/subjects/46/withdraw/` | 200 — withdrawn |
| 2e | POST `/subjects/47/complete/` | 200 — completed |
| 3a | GET `/visits/?study=5` | 200 — windows shown |
| 3b | GET `/subject-visits/?subject=41` | 200 — is_within_window |
| 4a | GET `/form-instances/?status=draft` | 200 — with completeness |
| 4b | POST `/form-instances/{id}/submit/` (incomplete) | 400 — missing fields |
| 4c | GET `/forms/{id}/` | 200 — nested items |
| 4d | POST `/item-responses/` | 201 — data entered |
| 4e | POST `/form-instances/{id}/submit/` (complete) | 200 — submitted |
| 4f | POST `/form-instances/{id}/sign/` | 200 — signed |
| 4g | POST `/item-responses/` (bad type) | 400 — validation |
| 5a | GET `/queries/` | 200 — with context |
| 5b | POST `/queries/4/answer/` | 200 — answered |
| 5c | POST `/queries/4/close/` | 200 — closed |
| 5d | POST `/form-instances/{id}/generate-queries/` | 200 — generated |
| 6a | GET `/subjects/41/` | 200 — nested visits |
| 6b | GET `/subject-visits/{id}/` | 200 — nested forms |
| 6c | GET `/adverse-events/` | 200 — nested fields |
| 7a-g | Various filters | 200 — filtered results |
| 8a-c | Search + ordering + pagination | 200 — correct results |
