# Risk-Based Monitoring & SAE Expedited Reporting — End-to-End Testing Guide

> **Version**: 1.0  
> **Date**: 2026-06-20  
> **Applies to**: HACT CTMS Phase 1 — Regulatory Must-Haves  
> **Prerequisites**: Docker services running, frontend dev server at `http://localhost:5173`

---

## Table of Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Test Data Seeding](#2-test-data-seeding)
3. [RBM Dashboard — Site Risk Heatmap](#3-rbm-dashboard--site-risk-heatmap)
4. [SAE Expedited Reporting — Timeline & Countdown](#4-sae-expedited-reporting--timeline--countdown)
5. [SAE Auto-Notification (Celery Beat)](#5-sae-auto-notification-celery-beat)
6. [End-to-End Flow](#6-end-to-end-flow)
7. [Expected Results Checklist](#7-expected-results-checklist)

---

## 1. Prerequisites & Setup

### 1.1 Verify Services Are Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected services:
| Container | Status |
|-----------|--------|
| hact-django-api | Up |
| hact-postgres | Up |
| hact-redis | Up |
| hact-celery-worker | Up |
| hact-celery-beat | Up |
| hact-keycloak | Up |
| hact-nginx | Up |

### 1.2 Verify Django Has the Monitoring App

```bash
docker exec hact-django-api python manage.py showmigrations safety
```

Expected output should include:
```
safety
 [X] 0001_initial
 [X] 0002_sae_expedited_reporting
```

### 1.3 Verify Frontend Compiles

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` — login with your Keycloak credentials.

### 1.4 Verify Monitoring API is Accessible

```bash
# Test from a terminal (replace TOKEN with a valid JWT)
curl -s http://localhost/api/v1/monitoring/study-overview/ -H "Authorization: Bearer <TOKEN>" | python -m json.tool
```

Or simply navigate to `http://localhost:5173/monitoring` after login.

---

## 2. Test Data Seeding

Before testing, we need at minimum:
- 1 study (active)
- 2+ sites
- 3+ enrolled subjects across those sites
- Some open queries
- At least 2 SAEs (one fatal/life-threatening, one other)

### 2.1 Seed via Django Admin

Open `http://localhost/admin/` and login with admin credentials.

#### Create a Study (if not exists)

| Field | Value |
|-------|-------|
| Name | PSBI Neonatal Sepsis Trial |
| Protocol Number | PSBI-2026-001 |
| Phase | II |
| Status | active |
| Start Date | 2026-01-01 |

#### Create 2 Sites

| Site Code | Name | Status | Activation Date |
|-----------|------|--------|-----------------|
| ETH-ADM-001 | Addis Ababa Medical Center | active | 2026-01-15 |
| ETH-JMC-002 | Jimma Medical Center | active | 2026-02-01 |

#### Create Subjects (at least 3 per site)

| Subject ID | Site | Status | Enrollment Date |
|-----------|------|--------|-----------------|
| ETH-ADM-001-0001 | ETH-ADM-001 | enrolled | 2026-03-01 |
| ETH-ADM-001-0002 | ETH-ADM-001 | enrolled | 2026-04-15 |
| ETH-ADM-001-0003 | ETH-ADM-001 | enrolled | 2026-05-20 |
| ETH-JMC-002-0001 | ETH-JMC-002 | enrolled | 2026-03-10 |
| ETH-JMC-002-0002 | ETH-JMC-002 | enrolled | 2026-04-20 |

### 2.2 Seed via Management Command (Quick)

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Study, Site, Subject
from safety.models import AdverseEvent
from django.utils import timezone
from datetime import timedelta

# Get or create study
study = Study.objects.first()
if not study:
    study = Study.objects.create(
        name='PSBI Neonatal Sepsis Trial',
        protocol_number='PSBI-2026-001',
        phase='II',
        status='active',
        start_date='2026-01-01',
    )
    print(f'Created study: {study}')

# Get or create sites
site1, _ = Site.objects.get_or_create(
    study=study, site_code='ETH-ADM-001',
    defaults={'name': 'Addis Ababa Medical Center', 'status': 'active', 'activation_date': '2026-01-15'}
)
site2, _ = Site.objects.get_or_create(
    study=study, site_code='ETH-JMC-002',
    defaults={'name': 'Jimma Medical Center', 'status': 'active', 'activation_date': '2026-02-01'}
)
print(f'Sites: {site1}, {site2}')

# Create subjects if fewer than 3 per site
for i, site in enumerate([site1, site2]):
    existing = Subject.objects.filter(site=site).count()
    for j in range(existing + 1, 4):
        sid = f'{site.site_code}-{j:04d}'
        Subject.objects.get_or_create(
            study=study, site=site, subject_identifier=sid,
            defaults={'status': 'enrolled', 'enrollment_date': '2026-03-01', 'consent_signed_date': '2026-03-01'}
        )
        print(f'  Created subject: {sid}')

print('Done seeding base data.')
"
```

### 2.3 Seed SAE Test Cases

Create two SAEs — one with a **7-day deadline** (fatal) and one with a **15-day deadline** (hospitalization):

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Study, Subject
from safety.models import AdverseEvent
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
study = Study.objects.first()

# --- SAE 1: Fatal → 7-day deadline ---
subj1 = Subject.objects.filter(study=study).first()
sae1, created = AdverseEvent.objects.get_or_create(
    subject=subj1,
    study=study,
    ae_term='Neonatal death due to septic shock',
    defaults={
        'start_date': timezone.now().date(),
        'severity': 'severe',
        'serious': True,
        'serious_criteria': 'death',
        'causality': 'possible',
        'outcome': 'fatal',
        'reported_by': user,
    }
)
if created:
    sae1.compute_deadline()
    sae1.save()
    print(f'Created SAE-{sae1.pk}: {sae1.ae_term}')
    print(f'  Deadline: {sae1.reporting_deadline} (7 days)')
    print(f'  Status: {sae1.reporting_status}')

# --- SAE 2: Hospitalization → 15-day deadline ---
subj2 = Subject.objects.filter(study=study).last()
sae2, created = AdverseEvent.objects.get_or_create(
    subject=subj2,
    study=study,
    ae_term='Severe pneumonia requiring hospitalization',
    defaults={
        'start_date': timezone.now().date(),
        'severity': 'severe',
        'serious': True,
        'serious_criteria': 'required_hospitalization',
        'causality': 'probable',
        'outcome': 'recovering',
        'reported_by': user,
    }
)
if created:
    sae2.compute_deadline()
    sae2.save()
    print(f'Created SAE-{sae2.pk}: {sae2.ae_term}')
    print(f'  Deadline: {sae2.reporting_deadline} (15 days)')
    print(f'  Status: {sae2.reporting_status}')

# --- SAE 3: Overdue SAE (for testing overdue detection) ---
sae3, created = AdverseEvent.objects.get_or_create(
    subject=subj1,
    study=study,
    ae_term='Severe anemia requiring blood transfusion (OVERDUE TEST)',
    defaults={
        'start_date': (timezone.now() - timedelta(days=20)).date(),
        'severity': 'severe',
        'serious': True,
        'serious_criteria': 'required_hospitalization',
        'causality': 'possible',
        'outcome': 'recovering',
        'reported_by': user,
    }
)
if created:
    # Manually set reported_at to 20 days ago so the deadline is past
    AdverseEvent.objects.filter(pk=sae3.pk).update(reported_at=timezone.now() - timedelta(days=20))
    sae3.refresh_from_db()
    sae3.compute_deadline()
    sae3.save()
    print(f'Created OVERDUE SAE-{sae3.pk}: {sae3.ae_term}')
    print(f'  Deadline: {sae3.reporting_deadline} (15 days from 20 days ago = 5 days OVERDUE)')
    print(f'  Status: {sae3.reporting_status}')

# --- Also create some open Queries for risk score variation ---
from clinical.models import Query
q_count = Query.objects.filter(subject__study=study, status='open').count()
if q_count < 3:
    for i in range(3 - q_count):
        subj = Subject.objects.filter(study=study).order_by('?').first()
        Query.objects.create(
            subject=subj,
            query_text=f'Test query #{i+1} - Please verify AE onset date',
            status='open',
            priority='high',
            created_by=user,
        )
        print(f'  Created open query for {subj.subject_identifier}')

print()
print('=== Test Data Summary ===')
print(f'SAEs with deadlines: {AdverseEvent.objects.filter(serious=True, reporting_deadline__isnull=False).count()}')
print(f'  Pending: {AdverseEvent.objects.filter(reporting_status=\"pending\").count()}')
print(f'  Overdue: {AdverseEvent.objects.filter(reporting_status=\"overdue\").count()}')
print(f'Open queries: {Query.objects.filter(subject__study=study, status=\"open\").count()}')
print(f'Enrolled subjects: {Subject.objects.filter(study=study, status=\"enrolled\").count()}')
"
```

> [!TIP]
> After running the seed commands, you can verify the data in Django Admin at `http://localhost/admin/safety/adverseevent/` — look for the `Reporting Deadline` and `Reporting Status` columns.

---

## 3. RBM Dashboard — Site Risk Heatmap

### 3.1 Navigate to the Monitoring Page

```
1. Open http://localhost:5173
2. Login with Keycloak credentials (e.g., hact-user)
3. In the sidebar, find the "Oversight" section
4. Click "Monitoring"
5. You should land on the Risk-Based Monitoring dashboard
```

### 3.2 Verify Study Risk Overview Cards

At the top of the page, you should see **6 summary cards**:

| Card | Expected |
|------|----------|
| Total Sites | Number of sites in the study (e.g., 2) |
| High Risk | Count of sites with risk score < 50 |
| Medium Risk | Count of sites with risk score 50-79 |
| Low Risk | Count of sites with risk score ≥ 80 |
| Overdue SAEs | Count of SAEs past their deadline |
| Open Queries | Count of unresolved data queries |

### 3.3 Verify Overall Risk Level Banner

Below the cards, a color-coded banner shows:
- 🟢 **Green** = Low Risk (all sites are healthy)
- 🟡 **Amber** = Medium Risk (some concerns)
- 🔴 **Red** = High Risk (at least one high-risk site)

The banner also shows enrollment progress (e.g., "Enrollment: 5/5 subjects (100% of target)").

### 3.4 Verify Site Risk Heatmap Table

The table shows one row per site with columns:

| Column | What to Check |
|--------|---------------|
| Site | Site code + name |
| Risk Level | Color-coded badge (Low/Medium/High) |
| Score | Overall score 0-100 |
| Enrollment | Enrollment rate value |
| Queries | Open queries per subject |
| AE Rate | AEs per enrolled subject |
| CRF % | CRF completion percentage |
| SAEs | Overdue SAE count |

### 3.5 Test Expandable KPI Details

```
1. Click on any site row → the row expands
2. You should see 5 KPI cards with:
   - Enrollment Rate (subjects/month)
   - Query Rate (open queries/subject)
   - AE Reporting (AEs/subject)
   - CRF Completion (%)
   - Overdue SAEs (count)
3. Each card shows:
   - Current value
   - Target/benchmark
   - Progress bar (green/amber/red)
   - Score out of 100
4. Click the row again → it collapses
```

### 3.6 Test Study Selector

```
1. If you have multiple studies, use the dropdown at the top-right
2. Select a different study → the dashboard should refresh
3. Select "All Studies (default)" → shows the first active study
```

---

## 4. SAE Expedited Reporting — Timeline & Countdown

### 4.1 Verify SAE Timeline Section

Scroll down on the Monitoring page. You should see the **"SAE Expedited Reporting Timeline"** section with:

- Header showing: "ICH-GCP E6(R2): Fatal/life-threatening → 7 days · Other SAE → 15 days"
- Filter badges: **Pending** (amber), **Overdue** (red), **On Time** (green)
- A table of SAEs with countdown timers

### 4.2 Verify SAE Countdown Display

For each SAE in the table, verify:

| Column | Expected for test data |
|--------|----------------------|
| SAE | AE ID + term (e.g., "AE-1: Neonatal death due to septic shock") |
| Subject | Subject identifier + site code |
| Criteria | Seriousness criteria (e.g., "death", "required hospitalization") |
| Deadline | Computed date (7 or 15 days from reported_at) |
| Time Remaining | Countdown badge with mini progress bar |
| Status | Pending (amber) / Overdue (red) / On Time (green) |
| Action | "Mark Reported" button for pending/overdue SAEs |

### 4.3 Verify Countdown Color Coding

| SAE Type | Expected Countdown |
|----------|-------------------|
| SAE 1 (fatal, fresh) | 🟢 Green badge: "~7.0d left" (< 50% elapsed) |
| SAE 2 (hospitalization, fresh) | 🟢 Green badge: "~15.0d left" (< 50% elapsed) |
| SAE 3 (overdue test) | 🔴 Red badge: "~5.0d overdue" |

### 4.4 Test Filter Badges

```
1. Click "Pending" badge → table shows only pending SAEs
2. Click "Overdue" badge → table shows only overdue SAEs
3. Click "On Time" badge → table shows only reported-on-time SAEs
4. Click the same badge again → filter is removed (shows all)
```

### 4.5 Test "Mark Reported" Action

```
1. Find an SAE with "Pending" or "Overdue" status
2. Click the "Mark Reported" button
3. Expected:
   - Toast: "SAE marked as reported to authority"
   - Status changes to "On Time" (if before deadline) or stays "Overdue" (if past)
   - "Mark Reported" button is replaced with the reported date
   - The summary badges update (Pending count decreases)
```

### 4.6 Verify SAE Created from Safety Page Gets Deadline

```
1. Navigate to Safety page (/safety)
2. Click "Report AE" button
3. Fill the form:
   - Subject: Pick an enrolled subject
   - AE Term: "Test SAE for deadline verification"
   - Onset Date: Today
   - Severity: Severe
   - Serious: Yes — SAE
   - SAE Criteria: "Life-threatening"
   - Causality: Possible
   - Outcome: Recovering
4. Submit the form
5. Navigate back to Monitoring page (/monitoring)
6. Scroll to SAE Timeline
7. Expected: The new SAE appears with a 7-day countdown (life-threatening → 7 days)
```

---

## 5. SAE Auto-Notification (Celery Beat)

### 5.1 Manually Trigger the Deadline Check Task

```bash
docker exec hact-django-api python manage.py shell -c "
from safety.tasks import check_sae_reporting_deadlines
result = check_sae_reporting_deadlines()
print(f'Result: {result}')
"
```

Expected output:
```
Result: Checked 3 pending SAEs. Notifications sent: X. Overdue: Y.
```

### 5.2 Check Email Notifications (Console Backend)

Since we use the console email backend in development, email content is printed to the Django logs:

```bash
docker logs hact-django-api --tail 50 2>&1 | findstr "SAE"
```

Look for lines like:
```
[SAE Notification] ⚠️ [WARNING] SAE Reporting Deadline — AE-1 (ETH-ADM-001-0001)
[SAE Notification] ❌ [OVERDUE] SAE Reporting Deadline — AE-3 (ETH-ADM-001-0001)
```

### 5.3 Verify Notification Thresholds

The Celery task tracks which thresholds have been notified to avoid duplicate emails:

```bash
docker exec hact-django-api python manage.py shell -c "
from safety.models import AdverseEvent
for sae in AdverseEvent.objects.filter(serious=True, reporting_deadline__isnull=False):
    print(f'AE-{sae.pk}: status={sae.reporting_status}, 50%={sae.notified_at_50_pct}, 90%={sae.notified_at_90_pct}, pct_elapsed={sae.deadline_percent_elapsed}%')
"
```

### 5.4 Verify Celery Beat Schedule

```bash
docker exec hact-django-api python manage.py shell -c "
from django.conf import settings
for name, config in settings.CELERY_BEAT_SCHEDULE.items():
    print(f'{name}: task={config[\"task\"]}, interval={config[\"schedule\"]}s')
"
```

Expected to include:
```
check-sae-deadlines-every-6-hours: task=safety.check_sae_reporting_deadlines, interval=21600s
```

---

## 6. End-to-End Flow

Complete this flow as a Study Monitor / Safety Officer would:

```
1. Login → http://localhost:5173
2. Navigate to Monitoring page (sidebar → Oversight → Monitoring)
3. See the study risk overview:
   - Total sites, risk distribution, overdue SAE count
4. Review the Site Risk Heatmap:
   - Click each site to expand KPI details
   - Identify any high-risk sites
5. Scroll to SAE Timeline:
   - Review all SAEs with deadlines
   - Note any OVERDUE (red) SAEs requiring immediate action
6. Mark an overdue SAE as reported:
   - Click "Mark Reported" → verify status changes
7. Go to Safety page → create a new SAE:
   - Mark as serious with "death" criteria
   - Submit
8. Return to Monitoring → verify:
   - New SAE appears in timeline with 7-day countdown
   - Risk scores may have updated
9. Run the Celery task manually to check notifications:
   docker exec hact-django-api python manage.py shell -c \
     "from safety.tasks import check_sae_reporting_deadlines; print(check_sae_reporting_deadlines())"
10. Check Django logs for email notification content:
    docker logs hact-django-api --tail 30
```

---

## 7. Expected Results Checklist

### RBM Dashboard

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 1 | Navigate to `/monitoring` | Page loads with 3 sections | ☐ |
| 2 | Study overview cards render | 6 cards with correct counts | ☐ |
| 3 | Overall risk banner shows | Color-coded risk level + enrollment | ☐ |
| 4 | Site risk heatmap table | All sites listed with risk badges | ☐ |
| 5 | Click site row to expand | 5 KPI cards with scores + progress bars | ☐ |
| 6 | Click site row again | Row collapses | ☐ |
| 7 | Study selector dropdown | Changes data when study is selected | ☐ |
| 8 | Risk levels are color-coded | 🟢 Low / 🟡 Medium / 🔴 High | ☐ |

### SAE Expedited Reporting

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 9 | SAE timeline section visible | Table with countdown timers | ☐ |
| 10 | Fatal SAE deadline | 7 calendar days from reported_at | ☐ |
| 11 | Hospitalization SAE deadline | 15 calendar days from reported_at | ☐ |
| 12 | Overdue SAE detection | Red "overdue" badge + negative days | ☐ |
| 13 | Countdown progress bar | Green (<50%) / Amber (50-90%) / Red (>90%) | ☐ |
| 14 | Filter by Pending | Only pending SAEs shown | ☐ |
| 15 | Filter by Overdue | Only overdue SAEs shown | ☐ |
| 16 | Mark Reported button | Status changes, button replaced with date | ☐ |
| 17 | New SAE from Safety page | Appears in timeline with correct deadline | ☐ |

### Celery Beat & Notifications

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 18 | Manual task trigger | Returns "Checked N pending SAEs..." | ☐ |
| 19 | Email content in Django logs | SAE notification text visible | ☐ |
| 20 | Overdue SAEs auto-marked | Status updated to "overdue" by task | ☐ |
| 21 | Notification flags set | `notified_at_50_pct` / `notified_at_90_pct` set correctly | ☐ |
| 22 | Celery Beat schedule registered | Task appears in beat schedule | ☐ |

### No Regressions

| # | Test Case | Expected Result | Pass? |
|---|-----------|-----------------|-------|
| 23 | Dashboard page (`/`) loads | No errors, all charts render | ☐ |
| 24 | Safety page (`/safety`) loads | AE table renders, create AE works | ☐ |
| 25 | Subjects page (`/subjects`) loads | Subject list renders | ☐ |
| 26 | Sidebar shows Monitoring | "Monitoring" appears under "Oversight" | ☐ |

---

> [!NOTE]
> **Production Email Setup**: In production, replace the console email backend with SMTP:
> ```
> EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
> EMAIL_HOST=smtp.gmail.com
> EMAIL_PORT=587
> EMAIL_USE_TLS=True
> EMAIL_HOST_USER=your-email@gmail.com
> EMAIL_HOST_PASSWORD=your-app-password
> ```
> Set these in your `.env` file or Docker environment variables.
