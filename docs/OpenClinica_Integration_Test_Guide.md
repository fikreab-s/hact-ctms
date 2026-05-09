# HACT CTMS — OpenClinica Integration End-to-End Test Guide

This guide validates the complete OpenClinica (OC) integration with the HACT CTMS platform, covering connectivity, SOAP API, subject sync, form data sync, and the React frontend data flow.

---

## Architecture Overview

```
┌──────────────────┐     SOAP/XML        ┌──────────────────┐
│  Django CTMS      │ ──────────────────► │  OpenClinica CE   │
│  (hact-django-api)│                     │  (hact-openclinica)│
│                   │  - Create Subject   │                   │
│  Celery Workers   │  - Schedule Event   │  Port 8080        │
│  (async tasks)    │  - Import ODM Data  │  ZODB + Postgres  │
│                   │  - List Studies     │                   │
│  React Frontend   │                     │  SOAP WS API      │
│  (hact-nginx)     │ ◄──────────────────│  /OpenClinica-ws/  │
└──────────────────┘     Study list       └──────────────────┘
```

**Key Design**: Django is the master. OpenClinica is a *complementary EDC*. Subjects and form data flow **Django → OC** via Celery tasks. OC is NOT the source of truth — Django is.

---

## Prerequisites

Ensure these containers are running:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=hact"
```

Required:
- `hact-django-api` (healthy)
- `hact-openclinica` (healthy)
- `hact-oc-postgres` (healthy)
- `hact-celery-worker` (Up)
- `hact-celery-beat` (Up)

If OpenClinica is not running:
```bash
docker compose --profile openclinica up -d
```

---

## Test 1: API Connectivity

```bash
docker exec hact-django-api python manage.py test_openclinica
```

**Expected output:**
```
Testing OpenClinica connection...
  URL: http://openclinica:8080/OpenClinica
  WS:  http://openclinica:8080/OpenClinica-ws

✅ OpenClinica is REACHABLE

Listing studies in OpenClinica...
  📋 default-study: Default Study
  📋 HACT-001: HACT Test Study

✅ OpenClinica integration test complete.
```

---

## Test 2: Integration Status API

```bash
docker exec hact-django-api python manage.py shell -c "
from integrations.openclinica import is_available
print('OC Available:', is_available())
"
```

**Expected**: `OC Available: True`

You can also check via the integration status endpoint (requires auth token):
```
GET /api/v1/integrations/status/
```
Response should include: `"openclinica": {"status": "healthy"}`

---

## Test 3: SOAP Study List

```bash
docker exec hact-django-api python manage.py shell -c "
from integrations.openclinica import list_studies
studies = list_studies()
for s in studies:
    print(f\"  {s['identifier']}: {s['name']} (OID: {s.get('oid', 'N/A')})\" )
"
```

**Expected**: Lists all studies configured in OpenClinica.

---

## Test 4: Subject Sync (Django → OpenClinica)

This tests the `sync_subject_to_openclinica` Celery task.

### 4a. Set the OpenClinica Study OID on a Django Study

First, find your OC study OID from the SOAP response above, then set it:

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Study
# Use the identifier from your OC study list
study = Study.objects.filter(protocol_number='HACT-2026-001').first()
if study:
    study.openclinica_study_oid = 'HACT-001'  # Match OC identifier
    study.save(update_fields=['openclinica_study_oid'])
    print(f'Set OC OID for {study.protocol_number} to {study.openclinica_study_oid}')
else:
    print('Study not found')
"
```

### 4b. Trigger Subject Sync

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Subject
from integrations.tasks import sync_subject_to_openclinica

# Get a subject from the study
subject = Subject.objects.filter(study__protocol_number='HACT-2026-001').first()
if subject:
    print(f'Syncing subject {subject.subject_identifier} to OC...')
    result = sync_subject_to_openclinica.apply(args=[subject.id])
    print(f'Result: {result.get()}')
else:
    print('No subjects found in study')
"
```

**Expected**:
- `Result: {'status': 'success', 'oc_oid': 'SS_...'}`
- Or `{'status': 'skipped', 'reason': 'no_study_oid'}` if OID not set

### 4c. Verify in OpenClinica UI

1. Open **http://localhost:8082/OpenClinica** (or your mapped port)
2. Login as `root` / `Like@1234567`
3. Navigate to **Study Subject Matrix**
4. Confirm the subject appears

---

## Test 5: Form Data Sync (Django → OpenClinica via ODM XML)

This tests the `sync_form_data_to_openclinica` Celery task.

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import FormInstance
from integrations.tasks import sync_form_data_to_openclinica

# Get a submitted form instance
fi = FormInstance.objects.filter(
    subject__study__openclinica_study_oid__isnull=False
).exclude(
    subject__study__openclinica_study_oid=''
).first()

if fi:
    print(f'Syncing form {fi.form.name} for {fi.subject.subject_identifier}...')
    result = sync_form_data_to_openclinica.apply(args=[fi.id])
    print(f'Result: {result.get()}')
else:
    print('No form instances linked to OC-enabled studies')
    print('Tip: Set openclinica_study_oid on a study first (Test 4a)')
"
```

**Expected**: `Result: {'status': 'success'}` or skipped if no OC OID

---

## Test 6: Event Scheduling (Django → OpenClinica)

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Subject, Visit
from integrations.tasks import schedule_event_in_openclinica
from datetime import date

subject = Subject.objects.filter(
    study__openclinica_study_oid__isnull=False
).exclude(study__openclinica_study_oid='').first()

visit = Visit.objects.filter(
    openclinica_event_definition_oid__isnull=False
).exclude(openclinica_event_definition_oid='').first()

if subject and visit:
    print(f'Scheduling event {visit.visit_name} for {subject.subject_identifier}...')
    result = schedule_event_in_openclinica.apply(
        args=[subject.id, visit.id, str(date.today())]
    )
    print(f'Result: {result.get()}')
else:
    print('No subjects or visits with OC OIDs configured')
    print('This is expected if you have not set openclinica_event_definition_oid on visits')
"
```

---

## Test 7: ODM XML Export

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import FormInstance
from integrations.openclinica import build_odm_for_form_instance

fi = FormInstance.objects.select_related(
    'subject', 'subject__study', 'form', 'subject_visit', 'subject_visit__visit'
).prefetch_related('responses', 'responses__item').first()

if fi:
    odm = build_odm_for_form_instance(fi)
    print('Generated ODM XML:')
    print(odm[:500])
else:
    print('No form instances found')
"
```

**Expected**: Valid ODM XML with `<ClinicalData>`, `<SubjectData>`, `<FormData>`, `<ItemData>` elements.

---

## Test 8: Frontend Data Flow Verification

The React frontend does NOT communicate with OpenClinica directly. The data flow is:

```
React UI → Django REST API → Django Models ←→ OpenClinica (via Celery)
```

### What to verify in the frontend:

1. **Studies Page** (`/studies`): Shows all studies including `openclinica_study_oid` in detail view
2. **Study Detail** (`/studies/:id`): Displays the OC OID field
3. **Subjects Page** (`/subjects`): Subjects synced to OC appear the same as non-OC subjects
4. **Lab Page** (`/lab`): Lab results are independent of OC (managed via SENAITE)

### How to verify:
1. Open the HACT CTMS frontend: **http://localhost**
2. Login with your Keycloak credentials
3. Navigate to Studies → click a study → confirm the OC Study OID shows
4. Navigate to Subjects → confirm subjects exist and can be enrolled
5. Enroll a subject → check OC UI to see if the subject was synced

---

## Test 9: Health Check (Celery Beat)

Verify OC health checks are running periodically:

```bash
docker logs hact-celery-worker --tail 20 2>&1 | findstr openclinica
```

**Expected**: Logs showing `OpenClinica health check: ✅ Available`

---

## Quick Reference: What Syncs Where

| HACT CTMS Action | OpenClinica Sync | Trigger |
|---|---|---|
| Create Subject + Enroll | Creates StudySubject in OC | Celery task (manual/signal) |
| Submit Form Data | Imports ODM XML into OC | Celery task (manual/signal) |
| Create Visit | Schedules Event in OC | Celery task (manual/signal) |
| OC Study List | Django reads from OC SOAP | On-demand query |
| Health Check | Periodic availability check | Celery Beat (10 min) |

> [!TIP]
> **Auto-trigger signals are ACTIVE.** Subject enrollment, form submission, and visit creation automatically trigger OC sync via Celery tasks. No manual commands needed in production — the table above shows the automatic flow.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `OpenClinica is NOT reachable` | Run `docker compose --profile openclinica up -d` |
| `SOAP Fault: ... authentication` | Check `OPENCLINICA_ADMIN_USER` and `OPENCLINICA_ADMIN_PASSWORD` in `.env` |
| `no_study_oid` skip | Set `openclinica_study_oid` on the Django Study model (Test 4a) |
| Subject sync fails | Ensure the OC study has a site matching the Django site_code |
| ODM import fails | OC study must have matching CRF OIDs and Event Definition OIDs |
| Liquibase lock error | Restart OC: `docker compose restart openclinica` |
| OC login fails | Default: `root` / password from `.env` OPENCLINICA_ADMIN_PASSWORD |
