# HACT CTMS — Stakeholder Live Demo Guide
## Real Clinical Trial: End-to-End Walkthrough (14 Steps)

**Scenario**: *HACT-ETH-MAL-2026* — A Phase II Antimalarial Efficacy Trial of Artesunate-Amodiaquine (ASAQ) vs Standard-of-Care in Uncomplicated *P. falciparum* Malaria in the Oromia Region, Ethiopia.

**Purpose**: Demonstrate the complete clinical trial lifecycle through the HACT CTMS platform, showing all integrated systems working together — including OIDC SSO with 2FA, EDC data capture in OpenClinica, ODM XML/CDISC compliance, and database lock.

---

## Pre-Demo Checklist

Start all services before the demo:

```bash
# Start core + all integration services
docker compose up -d
docker compose --profile openclinica --profile senaite up -d
docker compose --profile erpnext --profile nextcloud up -d
```

Verify everything is running:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Required services:
| Service | URL | Must Show |
|---|---|---|
| **HACT CTMS Frontend** | http://localhost:5173 (dev) or http://localhost (prod) | ✅ Login page |
| **OpenClinica CE** | http://localhost:8082/OpenClinica | ✅ Login page |
| **SENAITE LIMS** | http://localhost:8081/senaite | ✅ Dashboard |
| **Keycloak SSO** | http://localhost/auth | ✅ Admin console |
| **ERPNext** (optional) | http://localhost:8000 | Login page |
| **Nextcloud** (optional) | http://localhost:8083 | Login page |

### OpenClinica Pre-Setup (One-Time)

Before the demo, ensure OpenClinica has a study configured:

1. **Login to OpenClinica**: http://localhost:8082/OpenClinica → `admin` / `admin`
2. **Create Study**: Tasks → Create Study:
   - Study Name: `HACT-ETH-MAL-2026 — Phase II ASAQ Efficacy`
   - Protocol ID: `HACT-ETH-MAL-2026`
   - Study OID: `S_HACT2026` (note this — needed in Django)
   - Phase: `Phase II Trial`
3. **Create Study Event**: Define Study Event → Add:
   - Name: `Baseline Visit (Day 0)`, OID: `SE_BASELINE`
   - Name: `Follow-up Day 3`, OID: `SE_DAY3`
   - Name: `Follow-up Day 7`, OID: `SE_DAY7`
   - Name: `End of Study Day 28`, OID: `SE_EOS`
4. **Create CRF** (Case Report Form):
   - Build CRFs → Create New CRF → Name: `Baseline Physical Exam`
   - Add items: `Temperature (°C)`, `Weight (kg)`, `Parasitemia (parasites/µL)`, `Presenting Symptoms`
   - Version: `v1.0`
5. **Assign CRF to Event**: Event Definition → Baseline Visit → Add CRF `Baseline Physical Exam v1.0`

---

## Demo Flow — 14-Step Clinical Trial Lifecycle

### Act 1: Authentication & Trial Setup (Steps 1-4)

---

#### Step 1 — OIDC SSO Login with PKCE (Frontend)

**Open**: http://localhost:5173

> **What to tell stakeholders**: *"Notice we're using OIDC Authorization Code + PKCE flow — the most secure OAuth 2.0 standard for web applications. No passwords are stored in the browser. The credentials go directly to Keycloak, which supports two-factor authentication."*

1. Click **"Sign in with Keycloak SSO"**
2. Keycloak login page appears → Enter `hact-user` / `hact-user`
3. *(If 2FA is enabled)* → Enter OTP from authenticator app
4. Automatically redirected back to the HACT dashboard

> **Talking point**: *"Three security layers: PKCE prevents code interception, session timeout logs you out after 30 minutes of inactivity, and tokens auto-refresh every 14 minutes without disrupting your work."*

---

#### Step 2 — Create the Study (HACT CTMS Frontend)

**Navigate to**: Studies → **Create Study**

| Field | Value |
|---|---|
| Protocol Number | `HACT-ETH-MAL-2026` |
| Study Name | `Phase II Antimalarial Efficacy — ASAQ vs SOC` |
| Phase | `Phase II` |
| Sponsor | `Horn of Africa Clinical Trials (HACT)` |
| OpenClinica Study OID | `S_HACT2026` |
| Start Date | `2026-05-01` |
| End Date | `2027-12-31` |

**Click Create** → Study appears in the list.

> **What to tell stakeholders**: *"The moment this study is created, three things happen automatically: (1) an eTMF folder structure is created in Nextcloud, (2) the study metadata links to OpenClinica via the Study OID, and (3) the audit trail records who created it and when."*

---

#### Step 3 — Add Clinical Sites (Study Detail → New Site)

Click into `HACT-ETH-MAL-2026`, then **"New Site"**:

**Site 1:**
| Field | Value |
|---|---|
| Site Code | `ETH-ADM-001` |
| Name | `Adama General Hospital` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Fikadu Beyene` |

**Site 2:**
| Field | Value |
|---|---|
| Site Code | `ETH-JIM-002` |
| Name | `Jimma University Medical Center` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Meron Tadesse` |

> **Talking point**: *"When each site is created, ERPNext automatically receives it as a Customer record for contract and budget tracking. The signal fires asynchronously via Celery — no manual data entry in ERPNext needed."*

---

#### Step 4 — Verify Automated eTMF (Nextcloud)

**Open**: http://localhost:8083 → Login as `admin`

Navigate to **Files** → `eTMF/HACT-ETH-MAL-2026/`

Show the automatically created folder structure:
```
eTMF/HACT-ETH-MAL-2026/
  01_Protocol/
  02_IRB_Ethics/
  03_Regulatory/
  04_Site_Documents/
  05_Data_Management/
  06_Safety/
  07_Monitoring/
  08_Central_Lab/
```

> **Talking point**: *"This eTMF was created automatically — no one touched Nextcloud. Documents uploaded here are version-controlled and audit-trailed, meeting ICH-GCP requirements for inspection readiness."*

---

### Act 2: Subject Enrollment & EDC Data Capture (Steps 5-8)

---

#### Step 5 — Register & Enroll a Subject (Frontend)

**Navigate to**: Subjects → **New Subject**

| Field | Value |
|---|---|
| Study | `HACT-ETH-MAL-2026` |
| Site | `ETH-ADM-001 — Adama General Hospital` |
| Subject Identifier | `ETH-ADM-001-0001` |
| Screening Number | `SCR-0001` |

**Click Create** → Subject appears with status `screened`.

Now **Enroll** the subject:
- Click the subject ID → Subject detail page opens
- Click **"Enroll"** (or use the Enroll button in subjects list)
- Consent Signed Date: `2026-05-20`
- Enrollment Date: `2026-05-20`

> **What to tell stakeholders**: *"ICH-GCP Rule enforced: you CANNOT enroll without a consent date — the system rejects it. When enrollment succeeds, the subject is automatically pushed to OpenClinica via SOAP API."*

---

#### Step 6 — Verify Subject Sync in OpenClinica (EDC)

**Open**: http://localhost:8082/OpenClinica → Login as `admin`

**Navigate to**: Subject Matrix (View Subjects)

Show that subject `ETH-ADM-001-0001` appears automatically:
- Subject was created in Django CTMS
- Django signal triggered `sync_subject_to_openclinica` Celery task
- OpenClinica now has the subject ready for CRF data entry

> **Talking point**: *"This is the integration in action — the CTMS is the master system for enrollment, OpenClinica is the complementary EDC for clinical data capture. Data flows automatically via SOAP/XML — no double-entry."*

---

#### Step 7 — EDC Data Entry in OpenClinica (CRF Forms)

**In OpenClinica** (http://localhost:8082/OpenClinica):

1. **Subject Matrix** → Click on subject `ETH-ADM-001-0001`
2. **Schedule Event**: Baseline Visit (Day 0) → Schedule
3. **Enter Data**: Click the pencil icon on Baseline Visit → Open `Baseline Physical Exam v1.0`
4. **Fill the CRF** with real malaria patient values:

| CRF Field | Value | Clinical Meaning |
|---|---|---|
| Body Temperature (°C) | `38.9` | Febrile (fever) |
| Weight (kg) | `62.5` | Normal BMI |
| Parasitemia (parasites/µL) | `45,000` | Confirmed P. falciparum |
| Presenting Symptoms | `Fever, chills, headache, myalgia for 3 days` | Classic malaria presentation |

5. **Mark as Complete** → CRF status changes to ✅

> **Talking point**: *"This is electronic data capture happening live in OpenClinica. Every keystroke is audit-trailed. The CRF validates data types — you can't enter text in a numeric field. This is where clinical research coordinators spend most of their time during a trial."*

---

#### Step 8 — ODM XML Export & CDISC Compliance (OpenClinica)

**In OpenClinica**:

1. Navigate to: **Tasks** → **Extract Data** → **Create Dataset**
2. Select Study: `HACT-ETH-MAL-2026`
3. Select Events: All
4. Select CRFs: All
5. Click **Generate Dataset** → Choose format: **ODM XML 1.3**
6. Download the `.xml` file

**Open the XML file** and show the structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3"
     FileType="Snapshot"
     FileOID="HACT-ETH-MAL-2026_Export"
     CreationDateTime="2026-05-20T12:00:00">

  <ClinicalData StudyOID="S_HACT2026">
    <SubjectData SubjectKey="ETH-ADM-001-0001">
      <StudyEventData StudyEventOID="SE_BASELINE">
        <FormData FormOID="F_BASELINEPHYSICAL_V10">
          <ItemGroupData ItemGroupOID="IG_BASELINE">
            <ItemData ItemOID="I_TEMPERATURE" Value="38.9"/>
            <ItemData ItemOID="I_WEIGHT_KG" Value="62.5"/>
            <ItemData ItemOID="I_PARASITEMIA" Value="45000"/>
            <ItemData ItemOID="I_SYMPTOMS" Value="Fever, chills, headache, myalgia for 3 days"/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>
```

> **Talking point**: *"This is CDISC ODM XML 1.3 — the international standard for clinical data exchange. This format is what you submit to regulatory authorities (FDA, EMA, NAFDAC). Every data point has its OID, every value is traceable to the source CRF. OpenClinica generates this automatically — no manual transformation needed."*

**CDISC Compliance Summary**:
| Standard | Status | Purpose |
|---|---|---|
| **ODM v1.3** | ✅ Supported | Clinical data exchange format |
| **CDASH** | ✅ CRF design follows | Clinical Data Acquisition Standards |
| **SDTM** | ⚠️ Post-processing | Study Data Tabulation Model (for submission) |
| **ADaM** | ⚠️ Statistical layer | Analysis Data Model (for stats) |

> **Talking point**: *"We natively support ODM 1.3 and CDASH. For regulatory submission, the ODM export feeds into SDTM/ADaM conversion tools. The important thing is — the raw data is captured correctly and completely."*

---

### Act 3: Lab Results & Safety Monitoring (Steps 9-10)

---

#### Step 9 — Lab Results from SENAITE (Automatic Integration)

**How it works in production** (no code needed):

```
┌──────────────┐     webhook POST        ┌──────────────┐     auto-saves     ┌──────────────┐
│   SENAITE    │ ─────────────────────▶  │    Django     │ ───────────────▶  │   Frontend   │
│  Lab Tech    │  /integrations/senaite/ │  Celery Task  │   LabResult DB    │   Lab Page   │
│  publishes   │  webhook/results-       │  processes    │                   │   shows ↓    │
│  results     │  published/             │  & flags      │                   │  🔴 LOW      │
└──────────────┘                         └──────────────┘                    └──────────────┘
```

**Production flow** — zero manual steps:
1. Lab technician enters test results in **SENAITE** (http://localhost:8081/senaite)
2. Technician clicks **"Publish"** on the sample
3. SENAITE fires a webhook → `POST /api/v1/integrations/senaite/webhook/results-published/`
4. Django Celery worker receives it → creates `LabResult` records automatically
5. **Celery Beat** also runs a periodic sync every 15 minutes as a safety net
6. Frontend **Lab page** shows results immediately — auto-flagged against reference ranges

> **No shell commands, no manual import, no copy-paste. It just works.**

---

**Option A — Demo with live SENAITE** (preferred, if SENAITE is running):

1. Open SENAITE: http://localhost:8081/senaite → Login
2. Create a Sample for patient `ETH-ADM-001-0001`
3. Enter lab values: Hemoglobin = 9.2, WBC = 5.8, Platelets = 95, ALT = 42
4. Click **"Publish"** → Results flow automatically to Django

**Option B — Demo shortcut** (if SENAITE has no sample data):

This simulates what SENAITE would have sent — for demo purposes only:
```bash
docker exec hact-django-api python manage.py shell -c "
from lab.models import ReferenceRange, LabResult
from clinical.models import Study, Subject
from decimal import Decimal
from datetime import date

study = Study.objects.get(protocol_number='HACT-ETH-MAL-2026')
subject = Subject.objects.get(subject_identifier='ETH-ADM-001-0001')

# Reference ranges (normally set up once during study setup)
for name, low, high, unit in [('Hemoglobin',12.0,17.5,'g/dL'),('WBC Count',4.0,11.0,'10^3/uL'),('Platelet Count',150,400,'10^3/uL'),('ALT',7,56,'U/L')]:
    ReferenceRange.objects.get_or_create(study=study, test_name=name, defaults={'range_low':low, 'range_high':high, 'unit':unit})

# Simulated lab values (what SENAITE webhook would push)
for test, val, unit, low, high, flag in [('Hemoglobin','9.2','g/dL',Decimal('12.0'),Decimal('17.5'),'L'),('WBC Count','5.8','10^3/uL',Decimal('4.0'),Decimal('11.0'),'N'),('Platelet Count','95','10^3/uL',Decimal('150'),Decimal('400'),'L'),('ALT','42','U/L',Decimal('7'),Decimal('56'),'N')]:
    LabResult.objects.create(subject=subject, test_name=test, result_value=val, unit=unit, reference_range_low=low, reference_range_high=high, flag=flag, result_date=date(2026, 5, 20))

print('Simulated SENAITE results: Hb 9.2 (LOW), WBC 5.8 (N), Plt 95 (LOW), ALT 42 (N)')
"
```

---

**Show in Frontend**: Navigate to **Lab** page:
- 🔴 Hemoglobin: **9.2** g/dL (LOW — anemia, typical in malaria)
- 🟢 WBC: **5.8** (Normal)
- 🔴 Platelets: **95** (LOW — thrombocytopenia, common in malaria)
- 🟢 ALT: **42** (Normal)

Then click the **Subject ID** → Subject Detail page shows visits, AEs, and labs in one 360° view.

> **Talking point**: *"In production, the lab technician never leaves SENAITE, and the clinician never leaves the CTMS frontend. Results flow automatically via webhooks. The system auto-flags out-of-range values — no one needs to manually compare against reference ranges. This is the power of integrated systems."*

---

#### Step 10 — Report an SAE (Frontend → Safety → Report AE)

**Navigate to**: Safety → Click **"Report AE"** button (RBAC: only admin/study_admin/safety_officer)

Fill the form:
| Field | Value |
|---|---|
| Subject | `ETH-ADM-001-0001` |
| AE Term | `Severe anemia requiring blood transfusion` |
| Onset Date | `2026-05-22` |
| Severity | `Severe` |
| SAE? | `Yes — SAE` |
| SAE Criteria | `Requires hospitalization` |
| Causality | `Possible` |
| Outcome | `Recovering` |
| Action Taken | `Drug interrupted, blood transfusion administered` |
| Description | `Hb dropped to 7.1 g/dL from 9.2 at baseline. Urgent transfusion required.` |

> **Talking point**: *"This SAE form follows ICH-GCP E2A standards. The seriousness criteria (hospitalization) triggers expedited reporting — 7 days for fatal/life-threatening, 15 days for other serious. Role-based access control ensures only authorized safety officers can report."*

**Generate CIOMS I PDF** (RBAC: admin, study_admin, safety_officer only):
- In the SAE row, click the purple **"CIOMS"** button
- System generates a CIOMS I form PDF for regulatory submission
- PDF downloads automatically

> **Talking point**: *"The CIOMS I form is the international standard for expedited SAE reporting to regulatory authorities. Our system generates it automatically from the AE data — no manual form-filling, no transcription errors."*

---

### Act 4: Data Quality, Database Lock & Export (Steps 11-14)

---

#### Step 11 — Raise & Resolve Data Query (Frontend → Queries)

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Query, ItemResponse, FormInstance
from django.contrib.auth import get_user_model
User = get_user_model()

fi = FormInstance.objects.filter(subject__subject_identifier='ETH-ADM-001-0001').first()
response = fi.responses.filter(item__field_name='parasitemia').first()
user = User.objects.first()

Query.objects.create(item_response=response, status='open', query_text='Parasitemia 45,000/µL — confirm against source document.', raised_by=user)
print('Query raised on parasitemia field.')
"
```

**Show in Frontend**: Queries page → Answer → Close the query.

> **Talking point**: *"Data queries are the backbone of clinical data cleaning. Every query has a complete audit trail — who raised it, when, who answered, and who closed it."*

---

#### Step 12 — Export Data & Database Lock (Frontend → Studies)

**Navigate to**: Studies → `HACT-ETH-MAL-2026`

**Export Data** (RBAC: admin, study_admin, data_manager):
1. Click **"CSV"** button → Downloads a ZIP with all study data as CSV files
2. Click **"ODM XML"** button → Downloads CDISC ODM 1.3.2 XML export

> **Talking point**: *"Both exports are generated from the Django CTMS database. The CSV is for statistical tools (R, SAS, STATA). The ODM XML is the CDISC standard for regulatory submission. Both are also available from OpenClinica for EDC data."*

**Database Lock** (RBAC: admin, study_admin):
1. First resolve all queries (Step 11)
2. Click **"Move to locked"** button in the Study Detail header
3. System enforces: **All queries must be closed before locking**
4. Once locked: study banner shows **"Study Locked — All data is frozen"**

> **Talking point**: *"Database lock is a critical GCP milestone. The system prevents lock if any queries remain open. Once locked, the dataset is immutable — ready for statistical analysis and regulatory submission."*

---

#### Step 13 — Database Lock in OpenClinica (EDC)

**In OpenClinica** (http://localhost:8082/OpenClinica):

1. Navigate to: **Tasks** → **Lock Study**
2. Or per-CRF: Subject Matrix → Select subject → CRF → **Lock** icon
3. Status changes to 🔒 (locked)

Show the lock chain:
| System | Lock Status | What It Freezes |
|---|---|---|
| **Django CTMS** | ✅ Locked (Step 12) | Enrollment, queries, metadata |
| **OpenClinica EDC** | ✅ Locked (Step 13) | CRF data, event data |

> **Talking point**: *"Both systems are locked independently but consistently. The CTMS prevents new enrollments and data changes. OpenClinica prevents CRF modifications. Together, they guarantee dataset integrity for regulatory submission. This is the 'double-lock' pattern recommended for integrated CTMS/EDC architectures."*

---

#### Step 14 — Complete Audit Trail (Frontend → Audit)

**Navigate to**: Audit page → Show the complete chronological trail:

| Timestamp | User | Action | Model | Details |
|---|---|---|---|---|
| 2026-05-20 | hact-user | LOGIN | Session | OIDC PKCE authentication via Keycloak |
| 2026-05-20 | hact-user | CREATE | Study | HACT-ETH-MAL-2026 created |
| 2026-05-20 | hact-user | CREATE | Site | Adama General Hospital (ETH-ADM-001) |
| 2026-05-20 | hact-user | CREATE | Subject | ETH-ADM-001-0001 screened |
| 2026-05-20 | hact-user | UPDATE | Subject | Status → enrolled, consent signed |
| 2026-05-20 | hact-user | CREATE | LabResult | Hemoglobin = 9.2 (LOW) |
| 2026-05-22 | hact-user | CREATE | AdverseEvent | SAE: Severe anemia |
| 2026-05-22 | hact-user | CREATE | Query | Parasitemia verification |
| 2026-05-22 | hact-user | UPDATE | Query | Status → closed |
| 2026-05-22 | hact-user | UPDATE | Study | Status → locked |

> **Talking point**: *"21 CFR Part 11 compliance: every action has a timestamp, user identity (authenticated via OIDC SSO), and before/after values. This audit trail is immutable. When an FDA inspector asks 'who changed this data?', we produce this instantly."*

---

## Dashboard — Data Quality & System Status

**Navigate to**: Dashboard (home page)

The Dashboard now shows two additional widgets at the bottom:

### Data Quality Score (circular gauge)
- Shows percentage of resolved queries (green ≥80%, amber ≥50%, red <50%)
- Displays: resolved queries count, open queries count, SAE count
- **"Generate Report"** button (RBAC: admin, study_admin, data_manager only)

### System Status
- Live status of all 6 integrated services:
  - PostgreSQL ✅, Redis ✅, Keycloak SSO ✅
  - OpenClinica EDC, SENAITE LIMS, ERPNext (shows Online/Offline)
- Auto-refreshes every 60 seconds

> **Talking point**: *"The Data Quality Score gives an instant snapshot of data cleanliness. 100% means all queries are resolved — ready for database lock. The System Status widget shows all integrated services in real-time. This is your operational cockpit."*

---

## Milestones Tracker (Study Detail Page)

**Navigate to**: Studies → `HACT-ETH-MAL-2026` → Scroll to **Milestones** section

**Add Milestones** (RBAC: admin, study_admin, ops_manager):
1. Click **"Add Milestone"** → Select type:
   - First Patient In, 50% Enrollment, Last Patient In
   - Last Patient Out, Database Lock, Statistical Analysis Complete, Final Report
2. Set planned date → Click **"Add Milestone"**
3. Mark as **"Complete"** when milestone is achieved (records actual date)

| Milestone | Planned | Status | Actual |
|---|---|---|---|
| First Patient In | 2026-06-01 | ✅ Completed | 2026-05-20 |
| 50% Enrollment | 2026-09-01 | 🕐 Planned | — |
| Database Lock | 2027-06-01 | 🕐 Planned | — |

> **Talking point**: *"Clinical trial milestones are tracked in real-time. Everyone can see progress. Delayed milestones are flagged automatically. This transparency is critical for sponsor reporting and regulatory timelines."*

---

## Closing Statement for Stakeholders

> *"What you've seen is a complete clinical trial lifecycle — 14 steps from OIDC SSO login through study creation, subject enrollment, EDC data capture in OpenClinica, ODM XML/CDISC export, lab integration from SENAITE, safety reporting with CIOMS I PDF generation, data queries, milestone tracking, and dual database lock — all running on a 100% open-source platform.*
>
> *Security: OIDC PKCE authentication with optional 2FA, role-based access control for 9 user roles, automatic session timeout, and encrypted token refresh.*
>
> *Compliance: ICH-GCP compliant workflows, 21 CFR Part 11 audit trails, CDISC ODM XML 1.3 data export, CIOMS I safety reporting, and enforced business rules (consent before enrollment, queries before lock).*
>
> *Integration: Django CTMS orchestrates OpenClinica (EDC), SENAITE (LIMS), ERPNext (operations), and Nextcloud (eTMF) — synchronized via Celery tasks and Django signals, all under Keycloak single sign-on.*
>
> *Data Quality: Real-time quality scoring, milestone tracking, CSV/ODM export, and a system status dashboard — everything a clinical operations team needs.*
>
> *This is production-ready infrastructure for clinical research in the Horn of Africa."*

---

## Cleanup After Demo (Optional)

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Study
study = Study.objects.filter(protocol_number='HACT-ETH-MAL-2026').first()
if study:
    study.delete()
    print('Demo data cleaned up.')
"
```
