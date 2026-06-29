# HACT CTMS — Stakeholder Live Demo Guide
## PSBI Neonatal Clinical Trial: End-to-End Walkthrough (16 Steps)

**Scenario**: *HACT-PSBI-ETH-2026* — A Phase III Randomized Controlled Trial (RCT 2) evaluating treatment of Possible Serious Bacterial Infection (PSBI) in young infants (0–59 days) with moderate mortality risk signs, in the Oromia Region, Ethiopia.

**Study Arm**: **RCT 2** — Continued Inpatient Treatment vs. Discharged on Oral Amoxicillin

**Purpose**: Demonstrate the complete clinical trial lifecycle through the HACT CTMS platform — from OIDC SSO login through screening, enrollment, 48-hour assessment, treatment follow-up, outcome assessment, safety reporting, lab integration, data quality, and database lock — using all integrated systems: **OpenClinica (EDC)**, **SENAITE (LIMS)**, **Nextcloud (eTMF)**, **ERPNext (Operations)**, and **Keycloak (SSO)**.

---

## Pre-Demo Checklist

### Start All Services

```bash
# Start core platform + all integration services
docker compose up -d
docker compose --profile openclinica --profile senaite up -d
docker compose --profile erpnext --profile nextcloud up -d
```

### Verify Everything Is Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Required Services

| # | Service | URL | Must Show |
|---|---------|-----|-----------|
| 1 | **HACT CTMS Frontend** | http://localhost:5173 (dev) or http://localhost (prod) | ✅ Login page with "Sign in with Keycloak SSO" button |
| 2 | **Django Backend API** | http://localhost/api/health/ | ✅ `{"status": "healthy"}` |
| 3 | **Keycloak SSO** | http://localhost/auth | ✅ Admin console |
| 4 | **OpenClinica CE** | http://localhost:8082/OpenClinica | ✅ Login page |
| 5 | **SENAITE LIMS** | http://localhost:8081/senaite | ✅ Dashboard |
| 6 | **Nextcloud (eTMF)** | http://localhost:8083 | ✅ Login page |
| 7 | **ERPNext (Ops)** | http://localhost:8000 | ✅ Login page |

---

## OpenClinica Pre-Setup (One-Time Before Demo)

> **Do this once before the demo. It takes ~30 minutes.**

### 1. Login to OpenClinica
- URL: http://localhost:8082/OpenClinica
- Credentials: `admin` / `admin`

### 2. Create Study
**Tasks → Create Study:**

| Field | Value |
|-------|-------|
| Study Name | `HACT-PSBI-ETH-2026 — RCT 2 PSBI Neonatal Treatment` |
| Protocol ID | `HACT-PSBI-ETH-2026` |
| Study OID | `S_PSBI2026` *(note this — needed in Django `.env`)* |
| Phase | `Phase III Trial` |
| Status | `Available` |

### 3. Create Study Events (Visit Schedule)
**Tasks → Define Study Event → Add:**

| Event Name | Event OID | Type | Forms Assigned |
|------------|-----------|------|----------------|
| Screening & Enrollment | `SE_SCREENING` | Scheduled | A1_SCREEN_ENROLL |
| 48-hour Assessment (RCT 2) | `SE_48H` | Scheduled | B1_RCT2_48H |
| Day 2 Treatment Follow-up | `SE_DAY2` | Scheduled | B2_RCT2_TREATMENT |
| Day 4 Treatment Follow-up | `SE_DAY4` | Scheduled | B2_RCT2_TREATMENT |
| Day 8 Treatment Follow-up | `SE_DAY8` | Scheduled | B2_RCT2_TREATMENT |
| Day 15 Outcome Assessment | `SE_DAY15` | Scheduled | B3_RCT2_OUTCOME |
| Serious Adverse Event | `SE_SAE` | Unscheduled | C1_SAE |

### 4. Create CRFs (Case Report Forms)
**Tasks → Build CRF → Create New CRF:**

Build these 4 CRFs for RCT 2 (use `proposed_variable` names from the PSBI spec as Item Names):

#### CRF 1: `A1_SCREEN_ENROLL` — Screening & Enrollment (v1.0)
| Item Name | Label | Type | Required | Codelist |
|-----------|-------|------|----------|----------|
| `SUBJID` | Identification number | text | Yes | — |
| `SCRDTC` | Date of screening | date | Yes | — |
| `SCRTM` | Time of screening | time | No | — |
| `SCRCONS` | Consent for screening obtained | radio | Yes | YN (1=Yes, 2=No) |
| `BRTHDTC` | Date of birth | date | Yes | — |
| `SEX` | Sex of infant | radio | Yes | SEX (M/F/U) |
| `WEIGHT` | Weight of infant (grams) | numeric | Yes | — |
| `INCLMET` | Inclusion criteria met | radio | Yes | YN |
| `EXCLMET` | Exclusion criteria present | radio | Yes | YN |
| `TRTARM` | Treatment arm (randomization) | dropdown | Conditional | TRTARM |

#### CRF 2: `B1_RCT2_48H` — 48-Hour Assessment (v1.0)
| Item Name | Label | Type | Required | Codelist |
|-----------|-------|------|----------|----------|
| `ASSESSDTC` | Date of assessment | date | Yes | — |
| `ASSESSLOC` | Place of assessment | dropdown | Yes | ASSESSLOC |
| `FEEDDIFF` | Difficulty feeding | radio | Yes | — |
| `CHESTIND` | Severe chest indrawing | radio | Yes | YN |
| `TEMP` | Axillary temperature (°C) | numeric | Yes | — |
| `CRITILL` | Critical illness signs present | radio | Yes | YN |

#### CRF 3: `B2_RCT2_TREATMENT` — Treatment Record (v1.0)
| Item Name | Label | Type | Required | Codelist |
|-----------|-------|------|----------|----------|
| `DAYNUM` | Visit day number | dropdown | Yes | VISIT |
| `ASSESSLOC` | Place of completing form | dropdown | Yes | ASSESSLOC |
| `RESPONDENT` | Adult primary respondent | dropdown | Conditional | RESPONDENT |
| `OTHABX` | Other antibiotic name | text | Conditional | — |
| `REMTAB` | Remaining tablets/suspension | numeric | Conditional | — |

#### CRF 4: `C1_SAE` — Serious Adverse Event (v1.0)
| Item Name | Label | Type | Required | Codelist |
|-----------|-------|------|----------|----------|
| `SUBJID` | Identification number | text | Yes | — |
| `SAERPTDTC` | Date of filling SAE form | date | Yes | — |
| `ANAPHYL` | Anaphylactic reaction | radio | Yes | YN |
| `ALLERGIC` | Other allergic reaction/rash | radio | Yes | YN |
| `INJSITE` | Injection site infection/abscess | radio | Yes | YN |
| `DIARRHEA` | Diarrhoea with severe dehydration | radio | Yes | YN |
| `AESLIFE` | Life threatening AE | radio | Yes | YN |
| `AESTDTC` | Date of onset | date | Yes | — |
| `AEENDTC` | Date of resolution | date | Conditional | — |
| `AEACN` | Action taken | dropdown | Yes | AEACN |
| `AEOUT` | Outcome | dropdown | Yes | AEOUT |
| `DTHDTC` | Date of death | date | Conditional | — |
| `SAEDESC` | Description of SAE/death | textarea | Yes | — |

### 5. Assign CRFs to Events
**Event Definition → Select event → Add CRF:**
- `SE_SCREENING` → `A1_SCREEN_ENROLL v1.0`
- `SE_48H` → `B1_RCT2_48H v1.0`
- `SE_DAY2` / `SE_DAY4` / `SE_DAY8` → `B2_RCT2_TREATMENT v1.0`
- `SE_SAE` → `C1_SAE v1.0`

---

## Demo Flow — 16-Step PSBI Clinical Trial Lifecycle

---

### 🔐 Act 1: Authentication & Study Setup (Steps 1–4)

---

#### Step 1 — OIDC SSO Login with PKCE (Frontend)

**Open**: http://localhost:5173

> **What to tell stakeholders**: *"We use OIDC Authorization Code + PKCE — the most secure OAuth 2.0 standard for SPAs. No passwords are stored in the browser. Credentials go directly to Keycloak, which supports two-factor authentication."*

1. Click **"Sign in with Keycloak SSO"**
2. Redirected to Keycloak login page → Enter `hact-user` / `hact-user`
3. *(If 2FA is configured)* → Enter OTP from authenticator app
4. Redirected back to HACT CTMS dashboard automatically

**What happens behind the scenes:**
```
Frontend                  Keycloak                    Django Backend
   │                         │                              │
   │── PKCE challenge ──────▶│                              │
   │                         │── Login form ──▶ User        │
   │                         │◀── Credentials ──           │
   │◀── Authorization code ──│                              │
   │── Exchange code+verifier▶│                              │
   │◀── Access + Refresh tokens                             │
   │── GET /api/v1/accounts/auth/me/ (Bearer token) ──────▶│
   │◀── User profile + roles ──────────────────────────────│
```

> **Talking point**: *"Three security layers: PKCE prevents code interception, session timeout logs you out after 30 minutes of inactivity, and tokens auto-refresh every 60 seconds before expiry."*

---

#### Step 2 — Create the PSBI Study (HACT CTMS Frontend)

**Navigate to**: Studies → **Create Study**

| Field | Value |
|-------|-------|
| Protocol Number | `HACT-PSBI-ETH-2026` |
| Study Name | `RCT 2 — PSBI Neonatal Treatment (Moderate Mortality Risk)` |
| Phase | `Phase III` |
| Sponsor | `Horn of Africa Clinical Trials (HACT)` |
| OpenClinica Study OID | `S_PSBI2026` |
| Start Date | `2026-06-01` |
| End Date | `2028-06-30` |

**Click Create** → Study appears in the list with status `Planning`.

**What happens automatically (backend signals + Celery tasks):**

| System | Automatic Action | Verification |
|--------|-----------------|--------------|
| **Nextcloud (eTMF)** | Creates folder structure: `eTMF/HACT-PSBI-ETH-2026/01_Protocol/` through `08_Central_Lab/` | Check Nextcloud → Files |
| **OpenClinica** | Links study via `S_PSBI2026` OID | Study metadata connected |
| **Audit Trail** | Records `CREATE Study` event with user + timestamp | Check Audit page |
| **Django DB** | `clinical_studies` table — new row inserted | Admin panel |

> **Talking point**: *"The moment this study is created, three things happen: an eTMF folder structure is created in Nextcloud, the study links to OpenClinica via OID, and the audit trail records who created it and when — all automatically."*

---

#### Step 3 — Add Clinical Sites (Study Detail → New Site)

Click into `HACT-PSBI-ETH-2026`, then click **"New Site"**:

**Site 1: Adama General Hospital**
| Field | Value |
|-------|-------|
| Site Code | `ETH-ADM-001` |
| Name | `Adama General Hospital` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Fikadu Beyene` |

**Site 2: Jimma University Medical Center**
| Field | Value |
|-------|-------|
| Site Code | `ETH-JIM-002` |
| Name | `Jimma University Medical Center` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Meron Tadesse` |

**What happens automatically:**

| System | Automatic Action |
|--------|-----------------|
| **ERPNext** | Site created as a "Customer" record for contract/budget tracking |
| **Nextcloud** | Site subfolder created: `eTMF/HACT-PSBI-ETH-2026/04_Site_Documents/ETH-ADM-001/` |
| **Audit Trail** | Records `CREATE Site` for each site |

> **Talking point**: *"When each site is created, ERPNext automatically receives it for contract tracking, and Nextcloud creates a site-specific document folder. Zero manual data entry in external systems."*

---

#### Step 4 — Verify Automated eTMF (Nextcloud)

**Open**: http://localhost:8083 → Login as `admin`

Navigate to **Files** → `eTMF/HACT-PSBI-ETH-2026/`

Show the automatically created folder structure:
```
eTMF/HACT-PSBI-ETH-2026/
  01_Protocol/
  02_IRB_Ethics/
  03_Regulatory/
  04_Site_Documents/
    ETH-ADM-001/
    ETH-JIM-002/
  05_Data_Management/
  06_Safety/
  07_Monitoring/
  08_Central_Lab/
```

> **Talking point**: *"This eTMF was created automatically — no one touched Nextcloud. Upload your protocol, IRB approval, and consent forms here. Everything is version-controlled and audit-trailed, meeting ICH-GCP requirements for inspection readiness."*

---

### 👶 Act 2: Screening, Enrollment & EDC Data Capture (Steps 5–9)

---

#### Step 5 — Screen & Register a Newborn Subject (Frontend)

**Navigate to**: Subjects → **New Subject**

| Field | Value | Clinical Meaning |
|-------|-------|-----------------|
| Study | `HACT-PSBI-ETH-2026` | PSBI neonatal trial |
| Site | `ETH-ADM-001 — Adama General Hospital` | Enrolling site |
| Subject Identifier | `ETH-ADM-001-0001` | Country-Hospital-Sequential |
| Screening Number | `SCR-0001` | Pre-enrollment ID |

**Click Create** → Subject appears with status `screened`.

> **What to tell stakeholders**: *"The subject is registered but NOT enrolled yet. Screening precedes enrollment — we need consent and eligibility assessment first. This follows ICH-GCP E6(R2) requirements."*

---

#### Step 6 — Enroll the Subject with Consent (Frontend)

Click the subject ID → Subject detail page opens.

1. Click **"Enroll"**
2. Fill enrollment details:

| Field | Value | Clinical Meaning |
|-------|-------|-----------------|
| Consent Signed Date | `2026-06-15` | Mother gave informed consent |
| Enrollment Date | `2026-06-15` | Same day — infant meets criteria |

**Click Enroll** → Status changes to `enrolled`.

**What happens automatically:**

| System | Action |
|--------|--------|
| **Django** | Subject status → `enrolled`, consent date recorded |
| **OpenClinica** | Subject `ETH-ADM-001-0001` created via SOAP API (Celery task `sync_subject_to_openclinica`) |
| **Audit Trail** | Records `UPDATE Subject — status: screened → enrolled` |

> **Talking point**: *"ICH-GCP rule enforced: you CANNOT enroll without a consent date — the system rejects it. When enrollment succeeds, the subject is automatically pushed to OpenClinica for clinical data capture."*

---

#### Step 7 — Verify Subject Sync in OpenClinica (EDC)

**Open**: http://localhost:8082/OpenClinica → Login as `admin`

**Navigate to**: Subject Matrix (View Subjects)

Show that subject `ETH-ADM-001-0001` appears automatically:
- Created by Django CTMS → synced via Celery task
- OpenClinica now has the subject ready for CRF data entry

> **Talking point**: *"This is the CTMS–EDC integration in action. Django is the master system for enrollment, OpenClinica is the complementary EDC for clinical data capture. Data flows automatically — no double-entry."*

---

#### Step 8 — Screening CRF Data Entry in OpenClinica (A1_SCREEN_ENROLL)

**In OpenClinica** (http://localhost:8082/OpenClinica):

1. **Subject Matrix** → Click on `ETH-ADM-001-0001`
2. **Schedule Event**: `Screening & Enrollment` → Schedule for `2026-06-15`
3. **Enter Data**: Click pencil icon → Open `A1_SCREEN_ENROLL v1.0`
4. **Fill the CRF** with real PSBI patient values:

| CRF Field (Item Name) | Value | Clinical Meaning |
|------------------------|-------|-----------------|
| `SUBJID` | `ETH-ADM-001-0001` | Subject identifier |
| `SCRDTC` | `2026-06-15` | Screening date |
| `SCRTM` | `09:30` | Time of screening |
| `SCRCONS` | `1` (Yes) | Consent obtained from mother |
| `BRTHDTC` | `2026-06-10` | Born 5 days ago |
| `SEX` | `F` (Female) | Female infant |
| `WEIGHT` | `2850` | 2850 grams (normal) |
| `INCLMET` | `1` (Yes) | Meets inclusion criteria for RCT 2 |
| `EXCLMET` | `2` (No) | No exclusion criteria |
| `TRTARM` | `Oral Amoxicillin` | Randomized to discharge arm |

5. **Mark as Complete** → CRF status changes to ✅

> **Talking point**: *"This is electronic data capture happening live. Every keystroke is audit-trailed. The CRF validates data types — you can't enter text in a numeric field. Variable names like SUBJID, BRTHDTC, SEX are already SDTM-aligned for regulatory submission."*

---

#### Step 9 — 48-Hour Assessment in OpenClinica (B1_RCT2_48H)

**In OpenClinica**:

1. **Subject Matrix** → `ETH-ADM-001-0001`
2. **Schedule Event**: `48-hour Assessment (RCT 2)` → Schedule for `2026-06-17`
3. **Enter Data**: Open `B1_RCT2_48H v1.0`
4. **Fill the CRF**:

| CRF Field (Item Name) | Value | Clinical Meaning |
|------------------------|-------|-----------------|
| `ASSESSDTC` | `2026-06-17` | 48 hours after enrollment |
| `ASSESSLOC` | `Hospital` | Still admitted |
| `FEEDDIFF` | `No difficulty` | Feeding normally |
| `CHESTIND` | `2` (No) | No severe chest indrawing |
| `TEMP` | `37.2` | Normal temperature (°C) |
| `CRITILL` | `2` (No) | No critical illness signs — safe to discharge |

5. **Mark as Complete** → ✅

> **Talking point**: *"The 48-hour assessment is the critical decision point in RCT 2. If CRITILL = No, the infant can be discharged on oral amoxicillin. If Yes, continued inpatient treatment. This decision is captured in OpenClinica with full audit trail."*

---

### 🔬 Act 3: Lab Results & Safety Monitoring (Steps 10–12)

---

#### Step 10 — Lab Results from SENAITE (Automatic Integration)

**How it works in production** (zero manual steps):

```
┌──────────────┐     webhook POST        ┌──────────────┐     auto-saves     ┌──────────────┐
│   SENAITE    │ ─────────────────────▶  │    Django     │ ───────────────▶  │   Frontend   │
│  Lab Tech    │  /integrations/senaite/ │  Celery Task  │   LabResult DB    │   Lab Page   │
│  publishes   │  webhook/results-       │  processes    │                   │   shows ↓    │
│  results     │  published/             │  & flags      │                   │  🔴 HIGH     │
└──────────────┘                         └──────────────┘                    └──────────────┘
```

**Option A — Demo with live SENAITE** (preferred):

1. Open SENAITE: http://localhost:8081/senaite → Login
2. Create a Sample for patient `ETH-ADM-001-0001`
3. Enter neonatal lab values: CRP = 12.5, Hemoglobin = 14.8, WBC = 18.2, Platelets = 280
4. Click **"Publish"** → Results flow automatically to Django

**Option B — Demo shortcut** (if SENAITE has no sample data):

```bash
docker exec hact-django-api python manage.py shell -c "
from lab.models import ReferenceRange, LabResult
from clinical.models import Study, Subject
from decimal import Decimal
from datetime import date

study = Study.objects.get(protocol_number='HACT-PSBI-ETH-2026')
subject = Subject.objects.get(subject_identifier='ETH-ADM-001-0001')

# Neonatal reference ranges (normally set up once)
for name, low, high, unit in [
    ('C-Reactive Protein (CRP)', 0, 5.0, 'mg/L'),
    ('Hemoglobin', 14.0, 22.0, 'g/dL'),
    ('WBC Count', 5.0, 21.0, '10^3/uL'),
    ('Platelet Count', 150, 400, '10^3/uL'),
]:
    ReferenceRange.objects.get_or_create(
        study=study, test_name=name,
        defaults={'range_low': low, 'range_high': high, 'unit': unit}
    )

# Simulated neonatal lab values
for test, val, unit, low, high, flag in [
    ('C-Reactive Protein (CRP)', '12.5', 'mg/L', Decimal('0'), Decimal('5.0'), 'H'),
    ('Hemoglobin', '14.8', 'g/dL', Decimal('14.0'), Decimal('22.0'), 'N'),
    ('WBC Count', '18.2', '10^3/uL', Decimal('5.0'), Decimal('21.0'), 'N'),
    ('Platelet Count', '280', '10^3/uL', Decimal('150'), Decimal('400'), 'N'),
]:
    LabResult.objects.create(
        subject=subject, test_name=test, result_value=val,
        unit=unit, reference_range_low=low, reference_range_high=high,
        flag=flag, result_date=date(2026, 6, 15)
    )

print('Neonatal PSBI lab results created: CRP 12.5 (HIGH), Hb 14.8 (N), WBC 18.2 (N), Plt 280 (N)')
"
```

**Show in Frontend**: Navigate to **Lab** page:
- 🔴 CRP: **12.5** mg/L (HIGH — confirms bacterial infection, consistent with PSBI)
- 🟢 Hemoglobin: **14.8** g/dL (Normal for neonate)
- 🟢 WBC: **18.2** (Normal for neonate — neonates have higher WBC)
- 🟢 Platelets: **280** (Normal)

Click the **Subject ID** → Subject Detail page shows visits, AEs, and labs in one 360° view.

> **Talking point**: *"CRP > 5 mg/L confirms the bacterial infection diagnosis in this neonate. In production, the lab technician never leaves SENAITE, and the clinician never leaves the CTMS. Results flow automatically via webhooks. The system auto-flags out-of-range values."*

---

#### Step 11 — Report a Serious Adverse Event (Frontend → Safety)

**Navigate to**: Safety → Click **"Report AE"**

Fill the SAE form (these fields match the C1_SAE CRF from the PSBI spec):

| Field | Value | Clinical Meaning |
|-------|-------|-----------------|
| Subject | `ETH-ADM-001-0001` | Affected infant |
| AE Term | `Diarrhoea with severe dehydration` | PSBI-specific SAE type |
| Onset Date | `2026-06-20` | Day 5 post-enrollment |
| Severity | `Severe` | Requires intervention |
| SAE? | `Yes — SAE` | Meets seriousness criteria |
| SAE Criteria | `Requires hospitalization` | Infant re-admitted |
| Causality | `Possible` | Possibly related to study treatment |
| Outcome | `Recovering` | Still being treated |
| Action Taken | `Drug interrupted, IV fluids administered` | Emergency rehydration |
| Description | `Infant developed watery diarrhoea on Day 5. Severe dehydration requiring IV rehydration. Amoxicillin suspended.` | Narrative for CIOMS |

**Click Submit** → SAE appears in the safety dashboard.

**Generate CIOMS I PDF**:
- Click the purple **"CIOMS"** button on the SAE row
- System generates a CIOMS I form PDF automatically
- PDF downloads → ready for regulatory submission to EFDA

**What happens automatically:**

| System | Action |
|--------|--------|
| **Django** | `AdverseEvent` + `CiomsForm` records created |
| **Nextcloud** | CIOMS PDF can be uploaded to `eTMF/06_Safety/` |
| **Audit Trail** | Records `CREATE AdverseEvent — SAE: Diarrhoea with severe dehydration` |

> **Talking point**: *"This SAE form follows the C1_SAE specification from the PSBI protocol. The CIOMS I form is the international standard for expedited reporting — 7 days for fatal/life-threatening, 15 days for other serious events. Our system generates it automatically from the data."*

---

#### Step 12 — Treatment Follow-up in OpenClinica (B2_RCT2_TREATMENT)

**In OpenClinica**:

1. **Subject Matrix** → `ETH-ADM-001-0001`
2. **Schedule Event**: `Day 2 Treatment Follow-up` → Schedule for `2026-06-17`
3. **Enter Data**: Open `B2_RCT2_TREATMENT v1.0`
4. **Fill the CRF**:

| CRF Field (Item Name) | Value | Clinical Meaning |
|------------------------|-------|-----------------|
| `DAYNUM` | `D2` | Day 2 follow-up |
| `ASSESSLOC` | `Hospital` | Assessment at hospital |
| `RESPONDENT` | `Mother` | Mother present |
| `OTHABX` | *(empty)* | No additional antibiotics |
| `REMTAB` | `8` | 8 tablets remaining |

5. **Mark as Complete** → ✅

Repeat for **Day 4** and **Day 8** with updated values.

> **Talking point**: *"Treatment records track compliance — how many tablets remain, where the assessment happens. This is critical for assessing whether the oral amoxicillin discharge arm is as effective as continued hospitalization."*

---

### 📊 Act 4: Data Quality, Export & Database Lock (Steps 13–16)

---

#### Step 13 — Raise & Resolve Data Query (Frontend → Queries)

**Create a query** (via Django shell for demo):

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Query, ItemResponse, FormInstance
from django.contrib.auth import get_user_model
User = get_user_model()

fi = FormInstance.objects.filter(subject__subject_identifier='ETH-ADM-001-0001').first()
if fi:
    response = fi.responses.first()
    user = User.objects.first()
    Query.objects.create(
        item_response=response, status='open',
        query_text='Weight 2850g — please confirm this was measured on a calibrated scale per SOP.',
        raised_by=user
    )
    print('Data query raised on weight measurement.')
else:
    print('No form instance found — create one first via the API.')
"
```

**Show in Frontend**: Navigate to **Queries** page.
1. See the open query → Click to view details
2. Click **"Answer"** → Type: `Confirmed — Seca 354 scale, calibrated 2026-06-01, certificate on file.`
3. Click **"Close"** → Query status: ✅ Closed

> **Talking point**: *"Data queries are the backbone of clinical data cleaning. Every query has a complete audit trail. All queries must be closed before database lock — the system enforces this."*

---

#### Step 14 — ODM XML Export & CDISC Compliance

**In OpenClinica** (http://localhost:8082/OpenClinica):

1. **Tasks** → **Extract Data** → **Create Dataset**
2. Select Study: `HACT-PSBI-ETH-2026`
3. Select Events: All
4. Select CRFs: All
5. **Generate Dataset** → Format: **ODM XML 1.3**
6. Download the `.xml` file

**Show the XML structure:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3"
     FileType="Snapshot"
     FileOID="HACT-PSBI-ETH-2026_Export"
     CreationDateTime="2026-06-20T12:00:00">

  <ClinicalData StudyOID="S_PSBI2026">
    <SubjectData SubjectKey="ETH-ADM-001-0001">
      <StudyEventData StudyEventOID="SE_SCREENING">
        <FormData FormOID="F_A1_SCREEN_ENROLL_V10">
          <ItemGroupData ItemGroupOID="IG_A1_SCREENING">
            <ItemData ItemOID="I_SUBJID" Value="ETH-ADM-001-0001"/>
            <ItemData ItemOID="I_SCRDTC" Value="2026-06-15"/>
            <ItemData ItemOID="I_SEX" Value="F"/>
            <ItemData ItemOID="I_WEIGHT" Value="2850"/>
            <ItemData ItemOID="I_BRTHDTC" Value="2026-06-10"/>
            <ItemData ItemOID="I_TRTARM" Value="Oral Amoxicillin"/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>

      <StudyEventData StudyEventOID="SE_48H">
        <FormData FormOID="F_B1_RCT2_48H_V10">
          <ItemGroupData ItemGroupOID="IG_B1_48H">
            <ItemData ItemOID="I_ASSESSDTC" Value="2026-06-17"/>
            <ItemData ItemOID="I_TEMP" Value="37.2"/>
            <ItemData ItemOID="I_CRITILL" Value="2"/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>
```

**Also export from Django CTMS** (Frontend):
- Navigate to: Studies → `HACT-PSBI-ETH-2026`
- Click **"CSV"** → Downloads ZIP with all study data
- Click **"ODM XML"** → Downloads CDISC ODM 1.3.2 XML

**CDISC Compliance Summary:**
| Standard | Status | Purpose |
|----------|--------|---------|
| **ODM v1.3** | ✅ Supported | Clinical data exchange format |
| **CDASH** | ✅ CRF variables aligned | Clinical Data Acquisition Standards |
| **SDTM** | ⚠️ Post-processing | Study Data Tabulation Model (SUBJID→DM, TEMP→VS, etc.) |
| **ADaM** | ⚠️ Statistical layer | Analysis Data Model (for biostatisticians) |

> **Talking point**: *"Variable names like SUBJID, BRTHDTC, SEX, TEMP, TRTARM are already SDTM-aligned — this was designed from the start using the PSBI metadata specification. The ODM XML is what you submit to regulatory authorities."*

---

#### Step 15 — Database Lock (Frontend + OpenClinica)

**In Django CTMS (Frontend):**

1. Navigate to: Studies → `HACT-PSBI-ETH-2026`
2. First: Verify all queries are closed (Step 13)
3. Click **"Move to locked"** button in Study Detail header
4. System enforces: **All queries must be closed before locking**
5. Once locked: banner shows **"Study Locked — All data is frozen"**

**In OpenClinica:**

1. **Tasks** → **Lock Study**
2. Or per-CRF: Subject Matrix → Select subject → CRF → **Lock** icon 🔒

**Double-Lock Verification:**
| System | Lock Status | What It Freezes |
|--------|-------------|-----------------|
| **Django CTMS** | ✅ Locked | Enrollment, queries, metadata, exports |
| **OpenClinica EDC** | ✅ Locked | CRF data, event data, audit trail |

> **Talking point**: *"Both systems are locked independently but consistently. The CTMS prevents new enrollments and data changes. OpenClinica prevents CRF modifications. This 'double-lock' guarantees dataset integrity for regulatory submission to EFDA."*

---

#### Step 16 — Complete Audit Trail (Frontend → Audit)

**Navigate to**: Audit page → Show the complete chronological trail:

| Timestamp | User | Action | Model | Details |
|-----------|------|--------|-------|---------|
| 2026-06-15 09:00 | hact-user | LOGIN | Session | OIDC PKCE authentication via Keycloak |
| 2026-06-15 09:01 | hact-user | CREATE | Study | HACT-PSBI-ETH-2026 created |
| 2026-06-15 09:02 | hact-user | CREATE | Site | Adama General Hospital (ETH-ADM-001) |
| 2026-06-15 09:03 | hact-user | CREATE | Site | Jimma University Medical Center (ETH-JIM-002) |
| 2026-06-15 09:05 | hact-user | CREATE | Subject | ETH-ADM-001-0001 screened |
| 2026-06-15 09:06 | hact-user | UPDATE | Subject | Status: screened → enrolled, consent signed |
| 2026-06-15 10:00 | system | CREATE | LabResult | CRP = 12.5 mg/L (HIGH) — via SENAITE webhook |
| 2026-06-17 14:00 | hact-user | CREATE | FormInstance | B1_RCT2_48H — 48-hour assessment completed |
| 2026-06-20 08:00 | hact-user | CREATE | AdverseEvent | SAE: Diarrhoea with severe dehydration |
| 2026-06-20 08:05 | hact-user | CREATE | CiomsForm | CIOMS I PDF generated for SAE |
| 2026-06-20 09:00 | hact-user | CREATE | Query | Weight verification query opened |
| 2026-06-20 09:15 | hact-user | UPDATE | Query | Status: open → closed (answered) |
| 2026-06-25 16:00 | hact-user | UPDATE | Study | Status: active → locked |

> **Talking point**: *"21 CFR Part 11 compliance: every action has a timestamp, user identity (authenticated via Keycloak SSO), and before/after values. This audit trail is immutable. When an EFDA or FDA inspector asks 'who changed this data and when?', we produce this instantly."*

---

## System Integration Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HACT CTMS PLATFORM                               │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ React    │  │   Django    │  │   Celery     │  │   PostgreSQL     │ │
│  │ Frontend │─▶│   REST API  │─▶│   Workers    │─▶│   Database       │ │
│  │ (Vite)   │  │   (DRF)     │  │   + Beat     │  │   (16+)          │ │
│  └────┬─────┘  └──────┬──────┘  └──────┬───────┘  └──────────────────┘ │
│       │               │               │                                 │
│       └───────────────┼───────────────┘                                 │
│                       │                                                  │
├───────────────────────┼──────────────────────────────────────────────────┤
│                       │  Integration Layer (Celery Tasks)                │
│  ┌────────────────┐   │   ┌────────────────┐   ┌────────────────────┐  │
│  │  Keycloak SSO  │◀──┤   │  OpenClinica CE │   │  SENAITE LIMS      │  │
│  │  (OIDC/PKCE)   │   │   │  (EDC/eCRF)     │   │  (Lab Results)     │  │
│  │  • 9 roles     │   ├──▶│  • CRF capture   │   │  • Webhooks        │  │
│  │  • 2FA         │   │   │  • ODM XML       │   │  • Auto-flagging   │  │
│  │  • JWT tokens  │   │   │  • Audit trail   │   │  • Reference ranges│  │
│  └────────────────┘   │   └────────────────┘   └────────────────────┘  │
│                       │                                                  │
│  ┌────────────────┐   │   ┌────────────────┐                            │
│  │  Nextcloud     │◀──┤   │  ERPNext        │                            │
│  │  (eTMF/Docs)   │   └──▶│  (Operations)   │                            │
│  │  • Auto-folder │       │  • Contracts     │                            │
│  │  • Versioning  │       │  • Budgets       │                            │
│  │  • WebDAV      │       │  • Milestones    │                            │
│  └────────────────┘       └────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Dashboard — Data Quality & System Status

**Navigate to**: Dashboard (home page)

### Data Quality Score (circular gauge)
- Shows percentage of resolved queries (green ≥80%, amber ≥50%, red <50%)
- Displays: resolved queries count, open queries count, SAE count
- **"Generate Report"** button (RBAC: admin, study_admin, data_manager only)

### System Status
- Live status of all integrated services:
  - PostgreSQL ✅, Redis ✅, Keycloak SSO ✅
  - OpenClinica EDC ✅, SENAITE LIMS ✅, ERPNext ✅
- Auto-refreshes every 60 seconds

> **Talking point**: *"The Data Quality Score gives an instant snapshot of data cleanliness. 100% means all queries resolved — ready for database lock. The System Status shows all integrated services in real-time. This is your operational cockpit."*

---

## Milestones Tracker (Study Detail Page)

**Navigate to**: Studies → `HACT-PSBI-ETH-2026` → Scroll to **Milestones** section

**Add Milestones** (RBAC: admin, study_admin, ops_manager):

| Milestone | Planned | Status | Actual |
|-----------|---------|--------|--------|
| First Patient In | 2026-06-15 | ✅ Completed | 2026-06-15 |
| 50% Enrollment | 2026-12-01 | 🕐 Planned | — |
| Last Patient In | 2027-06-01 | 🕐 Planned | — |
| Last Patient Out | 2027-07-15 | 🕐 Planned | — |
| Database Lock | 2027-09-01 | 🕐 Planned | — |
| Statistical Analysis Complete | 2027-12-01 | 🕐 Planned | — |
| Final Report | 2028-03-01 | 🕐 Planned | — |

---

## PSBI Visit Schedule — Subject Timeline

| Visit | Day | Window | Forms | Status (Demo Subject) |
|-------|-----|--------|-------|-----------------------|
| **Screening** | Day 0 | — | A1_SCREEN_ENROLL | ✅ Complete |
| **48h Assessment** | Day 2 | ±1 day | B1_RCT2_48H | ✅ Complete |
| **Treatment Day 2** | Day 2 | ±1 day | B2_RCT2_TREATMENT | ✅ Complete |
| **Treatment Day 4** | Day 4 | ±1 day | B2_RCT2_TREATMENT | 🕐 Planned |
| **Treatment Day 8** | Day 8 | ±2 days | B2_RCT2_TREATMENT | 🕐 Planned |
| **Day 15 Outcome** | Day 15 | ±2 days | B3_RCT2_OUTCOME | 🕐 Planned |
| **SAE** | Any time | — | C1_SAE | ⚠️ 1 SAE reported |

---

## Closing Statement for Stakeholders

> *"What you've seen is a complete PSBI neonatal clinical trial lifecycle — 16 steps from OIDC SSO login through study creation, site activation, infant screening, enrollment with consent, 48-hour clinical assessment in OpenClinica, treatment follow-up, CRP lab results from SENAITE, SAE reporting with CIOMS I PDF generation, data queries, ODM XML/CDISC export, milestone tracking, and dual database lock.*
>
> *Security: OIDC PKCE authentication with optional 2FA, role-based access control for 9 user roles, automatic session timeout, and encrypted token refresh.*
>
> *Compliance: ICH-GCP E6(R2) compliant workflows, 21 CFR Part 11 audit trails, CDISC ODM XML 1.3 data export, CIOMS I safety reporting, SDTM-aligned variable naming, and enforced business rules (consent before enrollment, queries before lock).*
>
> *Integration: Django CTMS orchestrates OpenClinica (EDC), SENAITE (LIMS), ERPNext (operations), and Nextcloud (eTMF) — synchronized via Celery tasks and Django signals, all under Keycloak single sign-on.*
>
> *This is production-ready infrastructure for the PSBI neonatal clinical trial in the Horn of Africa."*

---

## Cleanup After Demo (Optional)

```bash
docker exec hact-django-api python manage.py shell -c "
from clinical.models import Study
study = Study.objects.filter(protocol_number='HACT-PSBI-ETH-2026').first()
if study:
    study.delete()
    print('PSBI demo data cleaned up.')
"
```

---

## Test Credentials

All users login at **http://localhost:5173/login** → redirected to Keycloak SSO

| Username | Password | Role | Can Do |
|----------|----------|------|--------|
| `hact-user` | `hact-user` | study_admin | Full access — create studies, enroll, report AEs |
| `dm.sarah` | `Test@2026!` | data_manager | Manage queries, export data, quality reports |
| `lab.manager` | `Test@2026!` | lab_manager | View lab results, reference ranges |
| `safety.officer` | `Test@2026!` | safety_officer | Report AEs, generate CIOMS PDFs |
| `auditor` | `Test@2026!` | auditor | Read-only audit trail access |

> Full credentials table: `docs/Test_Credentials.md`
