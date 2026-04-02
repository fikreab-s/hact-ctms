# Day 4 — Postman Testing Guide

**Prerequisites:**
- Docker containers running (`docker compose up -d`)
- Seed data loaded (`docker exec hact-django-api python manage.py seed_data --flush`)
- Auth token obtained (login first)

**Base URL:** `http://localhost/api/v1`

---

## 1. Login (Get Access Token via Keycloak)

```
POST http://localhost/auth/realms/hact/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded (form-data)

client_id:      hact-ctms
client_secret:  mk108Hu1yat2GOkpm9EpFEIHyKiMX5Kh
grant_type:     password
username:       hact-user
password:       hact-user
```

Save the `access_token` from the response. Add to all subsequent requests:
```
Authorization: Bearer <access_token>
```

---

## 2. CSV Data Export

### 2a. Generate CSV Export

```
POST http://localhost/api/v1/outputs/snapshots/export-csv/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1
}
```

**Expected:** `201 Created`
```json
{
    "detail": "CSV export generated successfully.",
    "snapshot_id": 1,
    "file_url": "/media/exports/HACT-MALARIA-001/..._raw_export_....zip",
    "download_url": "/api/v1/outputs/snapshots/1/download/"
}
```

### 2b. Download Export File

```
GET http://localhost/api/v1/outputs/snapshots/{snapshot_id}/download/
Authorization: Bearer <access_token>
```

**Expected:** ZIP file download containing:
- `subjects.csv`
- `visits.csv`
- `form_data.csv`
- `adverse_events.csv`
- `lab_results.csv`
- `queries.csv`

### 2c. Invalid Study (Error Handling)

```
POST http://localhost/api/v1/outputs/snapshots/export-csv/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 99999
}
```

**Expected:** `404 Not Found`

---

## 3. CDISC ODM XML Export

### 3a. Generate ODM Export

```
POST http://localhost/api/v1/outputs/snapshots/export-odm/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1
}
```

**Expected:** `201 Created`
```json
{
    "detail": "CDISC ODM export generated successfully.",
    "snapshot_id": 2,
    "file_url": "/media/exports/HACT-MALARIA-001/..._ODM_....xml",
    "download_url": "/api/v1/outputs/snapshots/2/download/"
}
```

### 3b. Download ODM XML

```
GET http://localhost/api/v1/outputs/snapshots/{snapshot_id}/download/
Authorization: Bearer <access_token>
```

**Expected:** XML file with `<ODM>` root element, CDISC 1.3.2 format.

---

## 4. Data Quality Reports

### 4a. Comprehensive Report

```
POST http://localhost/api/v1/outputs/quality-reports/generate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1,
    "report_type": "comprehensive"
}
```

**Expected:** `201 Created` with full report data:
```json
{
    "detail": "Quality report (comprehensive) generated successfully.",
    "report_id": 1,
    "report_data": {
        "report_type": "comprehensive",
        "study_protocol": "HACT-MALARIA-001",
        "sections": {
            "missing_data": { "total_missing_fields": 0, ... },
            "query_status": { "total_queries": 2, "open": 1, ... },
            "enrollment": { "total_enrolled": 3, ... },
            "completion": { "overall_completion_rate": 50.0, ... },
            "visit_compliance": { "compliance_rate": 100.0, ... }
        },
        "summary": {
            "indicators": [...],
            "overall_status": "yellow"
        }
    }
}
```

### 4b. Missing Data Report Only

```
POST http://localhost/api/v1/outputs/quality-reports/generate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1,
    "report_type": "missing_data"
}
```

**Expected:** `201 Created` with missing data details.

### 4c. Query Status Report

```
POST http://localhost/api/v1/outputs/quality-reports/generate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1,
    "report_type": "query_status"
}
```

### 4d. Enrollment Report

```
POST http://localhost/api/v1/outputs/quality-reports/generate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1,
    "report_type": "enrollment"
}
```

### 4e. Visit Compliance Report

```
POST http://localhost/api/v1/outputs/quality-reports/generate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "study": 1,
    "report_type": "visit_compliance"
}
```

---

## 5. Study Lock (Database Freeze)

> **CAUTION:** This locks the study. Use a study in `active` status with all queries resolved.

### 5a. Verify Study is Active

```
GET http://localhost/api/v1/clinical/studies/1/
Authorization: Bearer <access_token>
```

Check `"status": "active"`.

### 5b. Resolve All Open Queries First

```
GET http://localhost/api/v1/clinical/queries/?status=open
Authorization: Bearer <access_token>
```

For each open query, answer then close:

```
POST http://localhost/api/v1/clinical/queries/{id}/answer/
Content-Type: application/json
{
    "response_text": "Verified — data is correct."
}

POST http://localhost/api/v1/clinical/queries/{id}/close/
```

### 5c. Lock the Study

```
POST http://localhost/api/v1/clinical/studies/1/transition/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "status": "locked"
}
```

**Expected:** `200 OK` with:
```json
{
    "detail": "Study transitioned from 'active' to 'locked'.",
    "study": { ... },
    "quality_report_id": 3,
    "quality_summary": {
        "indicators": [...],
        "overall_status": "green"
    },
    "snapshot_id": 3,
    "snapshot_url": "/media/exports/HACT-MALARIA-001/..._raw_export_....zip",
    "form_instances_locked": 2
}
```

### 5d. Verify Data is Locked

Try editing a subject (should fail):
```
PATCH http://localhost/api/v1/clinical/subjects/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "screening_number": "SCR-999"
}
```

**Expected:** `400 Bad Request` — Study is locked.

---

## 6. List Snapshots & Reports

### 6a. List All Snapshots

```
GET http://localhost/api/v1/outputs/snapshots/
Authorization: Bearer <access_token>
```

### 6b. List All Quality Reports

```
GET http://localhost/api/v1/outputs/quality-reports/
Authorization: Bearer <access_token>
```

### 6c. View Quality Report Detail

```
GET http://localhost/api/v1/outputs/quality-reports/{id}/
Authorization: Bearer <access_token>
```

**Expected:** Full `report_data` JSON with all sections.

---

## Test Checklist

| # | Test | Expected | ✅ |
|---|------|----------|----|
| 1 | Login | Token received | |
| 2a | CSV export | 201 + snapshot_id | |
| 2b | Download ZIP | ZIP file with 6 CSVs | |
| 2c | Invalid study | 404 Not Found | |
| 3a | ODM export | 201 + snapshot_id | |
| 3b | Download XML | Valid CDISC ODM XML | |
| 4a | Comprehensive report | 201 + full report_data | |
| 4b | Missing data report | 201 + missing data details | |
| 4c | Query status report | 201 + query metrics | |
| 4d | Enrollment report | 201 + enrollment by site | |
| 4e | Visit compliance report | 201 + compliance rate | |
| 5a | Study is active | status: "active" | |
| 5b | Resolve queries | All queries closed | |
| 5c | Lock study | 200 + snapshot + report | |
| 5d | Verify lock blocks edits | 400 Bad Request | |
| 6a | List snapshots | Array of snapshots | |
| 6b | List quality reports | Array of reports | |
| 6c | Report detail | Full report_data | |
