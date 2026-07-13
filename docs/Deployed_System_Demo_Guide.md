# HACT CTMS — Deployed System: Stakeholder Live Demo & Testing Guide
## End-to-End Walkthrough on https://ctms.hacts.org/

**Version**: 2.0 — July 2026
**Environment**: Production (Google Cloud)
**Protocol**: HACT-PSBI-ETH-2026 — RCT 2 PSBI Neonatal Treatment

---

## 🌐 Platform Access — All Systems

### Main Application

| System | URL | Username | Password | Purpose |
|--------|-----|----------|----------|---------|
| **HACT CTMS** | https://ctms.hacts.org/ | `hact-user` | `hact-user` | Main clinical trial hub |
| **HACT CTMS** | https://ctms.hacts.org/ | `hact-admin` | `hact-admin` | Admin access |
| **HACT CTMS** | https://ctms.hacts.org/ | `admin` | `Admin@2026!` | Superuser |

### Integrated External Systems

| System | URL | Username | Password | Purpose |
|--------|-----|----------|----------|---------|
| **SENAITE LIMS** | https://ctms.hacts.org/senaite/ | `admin` | `admin` | Laboratory Information Management |
| **Nextcloud eTMF** | https://ctms.hacts.org/nextcloud/ | `admin` | `Admin@2026` | Electronic Trial Master File |
| **ERPNext** | https://ctms.hacts.org/erpnext/ | `Administrator` | `Admin@2026!` | Supply Chain & Finance |
| **OpenClinica** | https://ctms.hacts.org/openclinica/ | `root` | `12345678` | Electronic Data Capture (CRF Schema) |

### Mobile EDC

| System | URL | Username | Password | Purpose |
|--------|-----|----------|----------|---------|
| **Mobile EDC** | https://ctms.hacts.org/edc | `hact-user` | `hact-user` | Bedside CRF entry (tablet/phone) |

---

## Pre-Demo Verification (2 minutes)

Before starting the demo, quickly verify all systems are accessible:

### ✅ Checklist — Open each URL and confirm login works

- [ ] **HACT CTMS** → https://ctms.hacts.org/ → See "Sign in with Keycloak SSO" → Login → Dashboard loads
- [ ] **SENAITE** → https://ctms.hacts.org/senaite/ → Login → Dashboard loads
- [ ] **Nextcloud** → https://ctms.hacts.org/nextcloud/ → Login → Files page loads
- [ ] **ERPNext** → https://ctms.hacts.org/erpnext/ → Login → Home page loads
- [ ] **OpenClinica** → https://ctms.hacts.org/openclinica/ → Login → Task list loads
- [ ] **Mobile EDC** → https://ctms.hacts.org/edc → Login → Subject list loads

> **Tip for demo**: Open all 6 tabs in advance so you can switch between systems smoothly during the presentation.

---

## Demo Flow — 20 Steps Across All Systems

---

### 🔐 ACT 1: Authentication & System Tour (Steps 1–3)

---

#### Step 1 — Login via Keycloak SSO (HACT CTMS)

**URL**: https://ctms.hacts.org/

1. Click **"Sign in with Keycloak SSO"**
2. Enter credentials: `hact-user` / `hact-user`
3. You are redirected back to the HACT CTMS Dashboard

**✅ Expected Result**: Dashboard loads showing:
- Data Quality Score gauge
- System Status panel (PostgreSQL ✅, Redis ✅, etc.)
- Quick navigation sidebar

**🎤 Say to stakeholders**:
> *"We use OIDC Authorization Code with PKCE — the gold standard for browser security. No passwords are stored in the app. Keycloak handles identity, supports 2FA, and issues short-lived JWT tokens that auto-refresh."*

**🔍 What to verify**:
- [ ] Top-right shows logged-in username
- [ ] Sidebar shows all menu items (Dashboard, Studies, Subjects, Safety, Monitoring, etc.)
- [ ] No console errors (F12 → Console tab)

---

#### Step 2 — Quick Tour of the Dashboard

**On the Dashboard page**, point out:

| Section | What It Shows | Why It Matters |
|---------|---------------|----------------|
| **Data Quality Score** | Circular gauge (% queries resolved) | Instant readiness indicator for database lock |
| **System Status** | Live health of all integrated services | Operational monitoring — any red = investigate |
| **Quick Stats** | Studies count, subjects, sites | Portfolio overview at a glance |

**🔍 What to verify**:
- [ ] Data Quality Score renders (even if 0% — no data yet)
- [ ] System status shows service health indicators
- [ ] Page is responsive — resize browser to test

---

#### Step 3 — Verify All External Systems Are Live

Open each system in a new tab to prove the full stack is operational:

**Tab 1 — SENAITE LIMS**:
- URL: https://ctms.hacts.org/senaite/
- Login: `admin` / `admin`
- **✅ Verify**: Dashboard loads, "Add Sample" button visible

**Tab 2 — Nextcloud eTMF**:
- URL: https://ctms.hacts.org/nextcloud/
- Login: `admin` / `Admin@2026`
- **✅ Verify**: Files page loads, can create folders

**Tab 3 — ERPNext**:
- URL: https://ctms.hacts.org/erpnext/
- Login: `Administrator` / `Admin@2026!`
- **✅ Verify**: Home page loads, search bar works

**Tab 4 — OpenClinica**:
- URL: https://ctms.hacts.org/openclinica/
- Login: `root` / `12345678`
- **✅ Verify**: Task list loads, can see "Create Study" link

**🎤 Say to stakeholders**:
> *"Six systems, one platform. HACT CTMS is the orchestration hub — it connects to Keycloak for identity, OpenClinica for CRF schema, SENAITE for lab results, Nextcloud for document management, and ERPNext for operations. All deployed on Google Cloud under one domain."*

---

### 👶 ACT 2: Study Setup & Subject Enrollment (Steps 4–7)

---

#### Step 4 — Create the PSBI Study

**In HACT CTMS** → Navigate to **Studies** → Click **"Create Study"**

| Field | Value to Enter |
|-------|----------------|
| Protocol Number | `HACT-PSBI-ETH-2026` |
| Study Name | `RCT 2 — PSBI Neonatal Treatment (Moderate Mortality Risk)` |
| Phase | `Phase III` |
| Sponsor | `Horn of Africa Clinical Trials (HACT)` |
| OpenClinica Study OID | `S_PSBI2026` |
| Start Date | `2026-06-01` |
| End Date | `2028-06-30` |

Click **Create**.

**✅ Expected Result**:
- [ ] Study appears in the study list with status `Planning`
- [ ] Audit Trail records the creation event

**🔍 Then verify eTMF auto-creation**:
- Switch to **Nextcloud tab** → Refresh → Navigate to **Files**
- Look for: `eTMF/HACT-PSBI-ETH-2026/` folder structure
- Should see subfolders: `01_Protocol/`, `02_IRB_Ethics/`, `03_Regulatory/`, `04_Site_Documents/`, etc.

**🎤 Say to stakeholders**:
> *"The moment we created this study, a Celery background task automatically created the Trial Master File folder structure in Nextcloud. No one had to touch Nextcloud manually."*

---

#### Step 5 — Add Clinical Sites

**In HACT CTMS** → Click into the study → Click **"New Site"**

**Site 1:**

| Field | Value |
|-------|-------|
| Site Code | `ETH-ADM-001` |
| Name | `Adama General Hospital` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Fikadu Beyene` |

Click **Create** → Repeat for:

**Site 2:**

| Field | Value |
|-------|-------|
| Site Code | `ETH-JIM-002` |
| Name | `Jimma University Medical Center` |
| Country | `Ethiopia` |
| Principal Investigator | `Dr. Meron Tadesse` |

**✅ Expected Result**:
- [ ] Both sites appear under the study
- [ ] Audit trail records both `CREATE Site` events

**🔍 Then verify ERPNext auto-sync**:
- Switch to **ERPNext tab** → Search for `ETH-ADM-001` or navigate to Customer list
- Should see site created as a Customer record

**🔍 Then verify Nextcloud site folders**:
- Switch to **Nextcloud tab** → Navigate to `eTMF/HACT-PSBI-ETH-2026/04_Site_Documents/`
- Should see: `ETH-ADM-001/` and `ETH-JIM-002/` subfolders

**🎤 Say to stakeholders**:
> *"Creating a site triggers two integrations: ERPNext receives it for contract and budget tracking, and Nextcloud creates a site-specific document folder. Zero manual data entry across systems."*

---

#### Step 6 — Screen & Enroll a Newborn Subject

**In HACT CTMS** → Navigate to **Subjects** → Click **"New Subject"**

| Field | Value | Clinical Meaning |
|-------|-------|-----------------|
| Study | `HACT-PSBI-ETH-2026` | Select the PSBI study |
| Site | `ETH-ADM-001 — Adama General Hospital` | Enrolling site |
| Subject Identifier | `ETH-ADM-001-0001` | Country-Hospital-Sequential |
| Screening Number | `SCR-0001` | Pre-enrollment screening ID |

Click **Create** → Subject appears with status `screened`.

**Now enroll**: Click on subject → Click **"Enroll"**

| Field | Value |
|-------|-------|
| Consent Signed Date | `2026-06-15` |
| Enrollment Date | `2026-06-15` |

Click **Enroll** → Status changes to `enrolled`.

**✅ Expected Result**:
- [ ] Subject status = `enrolled`
- [ ] Consent date recorded
- [ ] Audit trail shows: `CREATE Subject` → `UPDATE Subject (screened → enrolled)`

**🔍 Then verify OpenClinica sync**:
- Switch to **OpenClinica tab** → Navigate to Subject Matrix
- Subject `ETH-ADM-001-0001` should appear (created via Celery SOAP sync)

**🎤 Say to stakeholders**:
> *"ICH-GCP rule enforced: you cannot enroll without a consent date — the system rejects it. When enrollment succeeds, the subject is automatically pushed to OpenClinica for CRF data capture."*

---

#### Step 7 — 📱 Mobile EDC: Bedside Data Capture (KEY FEATURE)

> ⭐ **Show this on a tablet, phone, or narrow browser window**

**URL**: https://ctms.hacts.org/edc

*(Or resize your browser to mobile width — about 400px)*

1. **Login** with `hact-user` / `hact-user`
2. **Subject List** → See `ETH-ADM-001-0001` in the list
3. **Tap the subject** → Visit Schedule opens

**Visit Schedule shows:**

| Visit | Due Date | Status | Action |
|-------|----------|--------|--------|
| Screening & Enrollment | 2026-06-15 | ✅ Complete | View |
| 48-hour Assessment | 2026-06-17 | 🔵 Due | Fill CRF |
| Day 2 Treatment | 2026-06-17 | 🔵 Due | Fill CRF |

4. **Tap "Fill CRF"** on 48-hour Assessment
5. **Fill the CRF** with these values:

| Field | Value |
|-------|-------|
| Assessment Date | `2026-06-17` |
| Place of Assessment | `Hospital` |
| Difficulty Feeding | `No difficulty` |
| Severe Chest Indrawing | `No` |
| Axillary Temperature (°C) | `37.2` |
| Critical Illness Signs | `No` |

6. **E-Sign** → Enter PIN to sign the CRF
7. **Tap Submit** → Data saved to backend

**✅ Expected Result**:
- [ ] CRF form loads with touch-friendly inputs
- [ ] Form submits successfully
- [ ] Status bar shows **"Submitted ✅"**
- [ ] Back on Visit Schedule, the visit shows as complete

**🔍 Offline Mode Demo** (optional but impressive):
1. Turn off WiFi / enable Airplane mode on the device
2. Status bar shows **📴 Offline Mode**
3. Fill another CRF → Data saved to IndexedDB locally
4. Turn WiFi back on → **"Syncing 1 pending..."** → ✅ Synced!

**🎤 Say to stakeholders**:
> *"This is our Mobile EDC — a Progressive Web App designed for nurses to use at the infant's bedside on a tablet. If the hospital WiFi goes down, no problem. Data is stored locally with a unique UUID and syncs automatically when connectivity returns. This is critical for Ethiopian healthcare facilities."*

---

### 🔬 ACT 3: Lab, Safety & Expedited Reporting (Steps 8–12)

---

#### Step 8 — Lab Results from SENAITE

**In SENAITE** → https://ctms.hacts.org/senaite/

1. Login: `admin` / `admin`
2. Click **"Add Sample"** (or **"Samples" → "Add"**)
3. Fill sample details:

| Field | Value |
|-------|-------|
| Client / Patient | `ETH-ADM-001-0001` |
| Sample Type | `Blood` |
| Date Sampled | `2026-06-15` |

4. Add analyses: **CRP**, **Hemoglobin**, **WBC**, **Platelets**
5. Enter results:

| Test | Value | Unit | Expected Flag |
|------|-------|------|---------------|
| C-Reactive Protein (CRP) | `12.5` | mg/L | 🔴 HIGH (ref: 0–5) |
| Hemoglobin | `14.8` | g/dL | 🟢 Normal |
| WBC Count | `18.2` | 10³/μL | 🟢 Normal (neonatal) |
| Platelet Count | `280` | 10³/μL | 🟢 Normal |

6. Click **"Publish"** → Results flow to HACT CTMS via webhook

**✅ Expected Result**:
- [ ] SENAITE shows results as "Published"
- [ ] Switch to **HACT CTMS** → **Lab** page → Results appear automatically
- [ ] CRP flagged as 🔴 HIGH

> **Note**: If SENAITE webhook isn't configured yet, verify the Lab page in HACT CTMS shows any previously loaded results. The integration architecture is: `SENAITE → webhook POST → Django → auto-flag H/L/N → display`.

**🎤 Say to stakeholders**:
> *"The lab technician never leaves SENAITE, the clinician never leaves CTMS. When the tech publishes results, they flow automatically. CRP > 5 mg/L confirms the bacterial infection diagnosis in this neonate."*

---

#### Step 9 — Report a Serious Adverse Event

**In HACT CTMS** → Navigate to **Safety** → Click **"Report AE"**

| Field | Value |
|-------|-------|
| Subject | `ETH-ADM-001-0001` |
| AE Term | `Diarrhoea with severe dehydration` |
| Onset Date | `2026-06-20` |
| Severity | `Severe` |
| SAE? | `Yes — SAE` |
| SAE Criteria | `Requires hospitalization` |
| Causality | `Possible` |
| Outcome | `Recovering` |
| Action Taken | `Drug interrupted, IV fluids administered` |
| Description | `Infant developed watery diarrhoea on Day 5. Severe dehydration requiring IV rehydration. Amoxicillin suspended.` |

Click **Submit**.

**✅ Expected Result**:
- [ ] SAE appears in the Safety dashboard / table
- [ ] No errors on submit (check browser console if issues)
- [ ] Audit trail records `CREATE AdverseEvent`

**🎤 Say to stakeholders**:
> *"This SAE form follows the C1_SAE CRF specification. The system auto-computes the regulatory reporting deadline — 15 days for hospitalization, 7 days for death or life-threatening."*

---

#### Step 10 — Generate CIOMS I PDF

**In the Safety page** → Find the SAE you just created

1. Click the **"CIOMS"** button (purple) on the SAE row
2. System generates CIOMS I form PDF
3. PDF downloads automatically

**✅ Expected Result**:
- [ ] PDF downloads successfully
- [ ] PDF contains: Subject ID, AE term, onset date, causality, narrative
- [ ] Ready for submission to EFDA

**🎤 Say to stakeholders**:
> *"The CIOMS I form is the international standard for expedited safety reporting. Instead of manually filling a Word template, the system generates it automatically from the structured data — no transcription errors."*

---

#### Step 11 — ⏱️ SAE Expedited Reporting Timeline (KEY FEATURE)

**In HACT CTMS** → Navigate to **Monitoring** → Scroll to **"SAE Expedited Reporting Timeline"**

**✅ Expected Result** — You should see:

| SAE | Subject | Onset | Deadline | Remaining | Status |
|-----|---------|-------|----------|-----------|--------|
| Diarrhoea (severe dehydration) | ETH-ADM-001-0001 | Jun 20 | **Jul 05** | X days | Pending |

**Demonstrate the color-coded urgency:**

| Color | Meaning | When |
|-------|---------|------|
| 🟢 Green | Plenty of time | > 50% of deadline remaining |
| 🟡 Yellow | Act soon | 10%–50% remaining |
| 🔴 Red | Urgent | < 10% remaining |
| ⚫ Black | OVERDUE | Past deadline — regulatory violation |

**Click "Mark Reported"**:
1. Confirm submission to EFDA
2. Status changes: `Pending` → ✅ `On Time`
3. `reported_to_authority_at` timestamp recorded

**🔍 What to verify**:
- [ ] SAE appears with correct deadline (15 days from onset)
- [ ] Color coding matches remaining time
- [ ] "Mark Reported" button works and updates status
- [ ] After marking, status shows ✅ On Time

**🎤 Say to stakeholders**:
> *"ICH E6(R3) and EFDA regulations require expedited reporting — 7 days for fatal, 15 days for other serious events. This dashboard tracks every SAE with a live countdown. Celery Beat checks every 6 hours and sends escalating email alerts at 50%, 90%, and overdue. No more missed deadlines."*

---

#### Step 12 — CRF Data Entry in OpenClinica

**In OpenClinica** → https://ctms.hacts.org/openclinica/

Login: `root` / `12345678`

1. Navigate to **Subject Matrix**
2. Find `ETH-ADM-001-0001` (should be synced from HACT CTMS)
3. **Schedule Event**: `Screening & Enrollment` → Date: `2026-06-15`
4. **Enter CRF Data** → Open `A1_SCREEN_ENROLL`:

| Field | Value |
|-------|-------|
| `SUBJID` | `ETH-ADM-001-0001` |
| `SCRDTC` | `2026-06-15` |
| `SCRCONS` | `1` (Yes) |
| `BRTHDTC` | `2026-06-10` |
| `SEX` | `F` |
| `WEIGHT` | `2850` |
| `INCLMET` | `1` (Yes) |
| `EXCLMET` | `2` (No) |
| `TRTARM` | `Oral Amoxicillin` |

5. **Mark as Complete** → ✅

**✅ Expected Result**:
- [ ] CRF opens and accepts data
- [ ] All field validations work (numeric, date, required)
- [ ] CRF marked as complete with audit trail

> **Note**: If the subject hasn't been synced to OpenClinica yet, you can manually create it: Add Subject → Enter `ETH-ADM-001-0001`. This verifies OpenClinica is functional.

**🎤 Say to stakeholders**:
> *"OpenClinica stores the canonical CRF schema — the formal structure for each form. Variable names like SUBJID, BRTHDTC, SEX are SDTM-aligned for regulatory submission."*

---

### 🛡️ ACT 4: Risk-Based Monitoring (Steps 13–14) — KEY FEATURE

---

#### Step 13 — 📊 RBM Dashboard: Study Risk Overview

**In HACT CTMS** → Navigate to **Monitoring**

**✅ Expected Result** — 6 KPI Summary Cards:

| KPI | Expected Value | Color |
|-----|---------------|-------|
| Total Sites | 2 | Blue |
| Enrollment Rate | 1+ subject(s) | Blue |
| Overdue SAEs | 0 | Green (or red if overdue) |
| Open Queries | 0–1 | Green/Yellow |
| Protocol Deviations | 0 | Green |
| Data Completeness | % | Green/Yellow/Red |

**🔍 What to verify**:
- [ ] All 6 KPI cards render with correct values
- [ ] Study selector dropdown works (select PSBI study)
- [ ] Cards use color coding (green = good, yellow = warning, red = critical)

**🎤 Say to stakeholders**:
> *"This is ICH E6(R3) risk-based monitoring. Instead of flying monitors to every site quarterly, we give them a real-time risk overview. Green means no action needed. Yellow means investigate. Red means intervene immediately."*

---

#### Step 14 — 🗺️ Site Risk Heatmap: Click to Expand KPIs

**On the same Monitoring page** → Scroll to **"Site Risk Heatmap"**

**✅ Expected Result**:

| Site | Risk Score | Level |
|------|-----------|-------|
| ETH-ADM-001 — Adama General | XX/100 | 🟢/🟡/🔴 |
| ETH-JIM-002 — Jimma University | XX/100 | 🟢/🟡/🔴 |

**Click on a site row** → Expanded KPI details appear:

| KPI | Value | Weight | Risk Contribution |
|-----|-------|--------|-------------------|
| Open Queries | X | 30% | XX pts |
| Overdue SAEs | X | 25% | XX pts |
| Protocol Deviations | X | 20% | XX pts |
| Enrollment Rate | X | 15% | XX pts |
| Data Entry Timeliness | X days | 10% | XX pts |

**🔍 What to verify**:
- [ ] Both sites appear in the heatmap
- [ ] Risk scores calculate correctly
- [ ] Clicking a row expands KPI details
- [ ] Color coding matches risk level (0–30: green, 31–60: yellow, 61+: red)

**🎤 Say to stakeholders**:
> *"Each site gets a weighted risk score from 0 to 100. The monitor focuses on the highest-risk site first. This reduces monitoring costs by 40–60% while maintaining data quality — exactly what ICH E6(R3) recommends."*

---

### 📊 ACT 5: Data Quality, Queries & Document Management (Steps 15–18)

---

#### Step 15 — Data Queries: Raise, Answer, Close

**In HACT CTMS** → Navigate to **Queries**

**Option A — If queries exist**: Review, answer, and close them.

**Option B — Create a test query** (via Subjects page):
1. Go to **Subjects** → Click on `ETH-ADM-001-0001`
2. Find a form instance → Click to open → Look for query option
3. Or create via the Queries page if a "New Query" button exists

**Query workflow**:
1. **Open** → Query text: `Weight 2850g — please confirm measured on calibrated scale per SOP.`
2. **Answer** → `Confirmed — Seca 354 scale, calibrated 2026-06-01, certificate on file.`
3. **Close** → Status: ✅ Closed

**✅ Expected Result**:
- [ ] Queries page loads
- [ ] Query lifecycle works: Open → Answered → Closed
- [ ] Audit trail records query events

**🎤 Say to stakeholders**:
> *"Data queries are the backbone of clinical data cleaning. Every query has a complete audit trail — who raised it, who answered, who closed it, and when. All queries must be closed before database lock."*

---

#### Step 16 — Nextcloud eTMF: Document Management

**In Nextcloud** → https://ctms.hacts.org/nextcloud/

Login: `admin` / `Admin@2026`

1. Navigate to **Files** → Look for `eTMF/` folder (or create it)
2. If auto-created by HACT CTMS: Browse `eTMF/HACT-PSBI-ETH-2026/`
3. **Upload a test document**:
   - Navigate to `01_Protocol/`
   - Click **"+"** → Upload → Select any PDF (e.g., "PSBI_Protocol_v3.0.pdf")
4. **Show versioning**: Upload the same file again → Nextcloud keeps both versions

**✅ Expected Result**:
- [ ] eTMF folder structure exists (auto-created or manually created)
- [ ] Can upload documents
- [ ] Version history available
- [ ] Site-specific folders exist under `04_Site_Documents/`

**🎤 Say to stakeholders**:
> *"Nextcloud serves as our electronic Trial Master File. Protocol documents, IRB approvals, site agreements — all version-controlled and ready for regulatory inspection. Folders were created automatically when the study and sites were set up in HACT CTMS."*

---

#### Step 17 — ERPNext: Operations & Finance Tracking

**In ERPNext** → https://ctms.hacts.org/erpnext/

Login: `Administrator` / `Admin@2026!`

1. **Search** for `ETH-ADM-001` → Should find it as a Customer (auto-synced from HACT CTMS)
2. **Show capabilities**:
   - Navigate to **Selling → Customer** → View site record
   - Navigate to **Projects** → Can track study milestones
   - Navigate to **Accounting** → Can track budgets and invoices

**✅ Expected Result**:
- [ ] ERPNext loads and is functional
- [ ] Site records exist (if auto-synced)
- [ ] Can navigate to Projects, Accounting modules

**🎤 Say to stakeholders**:
> *"ERPNext handles the operational side — contracts, budgets, payments, and supply chain. When a site is created in HACT CTMS, it automatically appears here as a Customer for financial tracking."*

---

#### Step 18 — Audit Trail: Complete Regulatory Record

**In HACT CTMS** → Navigate to **Audit**

**✅ Expected Result** — Chronological trail of everything done during the demo:

| Timestamp | User | Action | Model | Details |
|-----------|------|--------|-------|---------|
| (time) | hact-user | LOGIN | Session | OIDC PKCE via Keycloak |
| (time) | hact-user | CREATE | Study | HACT-PSBI-ETH-2026 |
| (time) | hact-user | CREATE | Site | ETH-ADM-001 |
| (time) | hact-user | CREATE | Site | ETH-JIM-002 |
| (time) | hact-user | CREATE | Subject | ETH-ADM-001-0001 |
| (time) | hact-user | UPDATE | Subject | screened → enrolled |
| (time) | hact-user | CREATE | FormInstance | 📱 CRF via Mobile EDC |
| (time) | hact-user | CREATE | AdverseEvent | SAE reported |
| (time) | hact-user | CREATE | CiomsForm | CIOMS I PDF generated |
| (time) | hact-user | UPDATE | AdverseEvent | SAE marked as reported |
| (time) | hact-user | CREATE/CLOSE | Query | Data query lifecycle |

**🔍 What to verify**:
- [ ] Audit page loads with records
- [ ] Each action shows: user, timestamp, action type, affected model
- [ ] Records are immutable (no edit/delete buttons)
- [ ] Can filter by model, user, or date

**🎤 Say to stakeholders**:
> *"21 CFR Part 11 compliance: every action has a timestamp, authenticated user identity, and before/after values. This trail is immutable. When an EFDA inspector asks 'who changed this and when?' — we produce this instantly."*

---

### 🔒 ACT 6: Export, Lock & Final Summary (Steps 19–20)

---

#### Step 19 — Data Export & Database Lock

**Export Data**:
1. Navigate to **Studies** → Click `HACT-PSBI-ETH-2026`
2. Click **"CSV"** → Downloads ZIP with study data
3. Click **"ODM XML"** → Downloads CDISC ODM 1.3.2 XML (if available)

**Database Lock** (if all queries are closed):
1. On the Study Detail page → Click **"Move to locked"**
2. System verifies: all queries must be closed first
3. Once locked → Banner shows **"Study Locked — All data is frozen"**

**✅ Expected Result**:
- [ ] CSV export downloads successfully
- [ ] Lock button appears (admin/study_admin only)
- [ ] Lock enforces query closure prerequisite
- [ ] After lock, data modification is blocked

**🎤 Say to stakeholders**:
> *"The database lock freezes all data for regulatory submission. Both Django CTMS and OpenClinica are locked independently but consistently — a 'double-lock' that guarantees dataset integrity."*

---

#### Step 20 — Closing Summary: Full System Integration

**Show this final diagram to stakeholders** (draw on whiteboard or show diagram):

```
                          ┌─────────────────────┐
                          │   🔐 Keycloak SSO    │
                          │   OIDC PKCE + 2FA    │
                          └──────────┬──────────┘
                                     │ JWT Tokens
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │  📱 Mobile EDC     │ │  🖥️ HACT CTMS      │ │  👁️ Monitoring    │
    │  (Bedside/Tablet)  │ │  (Desktop/Web)     │ │  (RBM Dashboard)  │
    │  Offline-First     │ │  React SPA         │ │  ICH E6(R3)       │
    │  IndexedDB + Sync  │ │  Full Management   │ │  Risk Heatmap     │
    └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  🐍 Django REST API  │
                          │  + Celery Workers    │
                          │  + PostgreSQL        │
                          └──────────┬──────────┘
                                     │
              ┌──────────┬───────────┼───────────┬──────────┐
              │          │           │           │          │
    ┌─────────▼───┐ ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐ ┌──▼───────┐
    │ OpenClinica │ │ SENAITE │ │Nextcloud│ │ ERPNext │ │📧 Email  │
    │ EDC/CRF     │ │  LIMS   │ │  eTMF  │ │  Ops    │ │SAE Alerts│
    │ SOAP API    │ │ Webhook │ │ WebDAV │ │REST API │ │  SMTP    │
    └─────────────┘ └─────────┘ └────────┘ └─────────┘ └──────────┘
```

**🎤 Closing statement**:

> *"What you've seen today is a complete PSBI neonatal clinical trial lifecycle — 20 steps across 6 integrated systems, all deployed on Google Cloud at ctms.hacts.org.*
>
> *From Keycloak SSO authentication, through study creation with automatic eTMF provisioning, site activation with ERPNext sync, infant enrollment with OpenClinica integration, bedside data capture on our offline-first Mobile EDC, SENAITE lab results via webhooks, SAE reporting with automated CIOMS I PDF generation and expedited deadline tracking, risk-based monitoring with site heatmaps, data queries, CDISC-compliant exports, and database lock.*
>
> *Compliance: ICH-GCP E6(R2/R3), 21 CFR Part 11 audit trails, CDISC ODM XML, CIOMS I safety reporting, SDTM-aligned variables, and risk-based monitoring.*
>
> *This is production-ready infrastructure for the PSBI neonatal clinical trial in the Horn of Africa."*

---

## Quick Reference: Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Login fails at Keycloak | Verify credentials match the table above. Try `hact-admin` / `hact-admin` |
| Dashboard shows empty | Create a study first (Step 4). Data populates after enrollment |
| Mobile EDC shows no subjects | Ensure subject is enrolled (Step 6). Check site assignment |
| SENAITE login fails | Use `admin` / `admin` — note lowercase |
| Nextcloud login fails | Use `admin` / `Admin@2026` — no exclamation mark |
| ERPNext login fails | Use `Administrator` (capital A) / `Admin@2026!` — with exclamation |
| OpenClinica login fails | Use `root` / `12345678` |
| SAE submit returns 400 error | Ensure all required fields are filled, especially Subject |
| RBM shows "No sites found" | Select the correct study from the dropdown |
| Site risk scores show 0 | Normal — risk accumulates as data is entered |

---

## Demo Timing Guide

| Act | Steps | Duration | Focus |
|-----|-------|----------|-------|
| **Act 1** — Auth & Tour | 1–3 | 5 min | Security, system overview |
| **Act 2** — Study & Enrollment | 4–7 | 10 min | Study setup, Mobile EDC ⭐ |
| **Act 3** — Lab & Safety | 8–12 | 12 min | Lab integration, SAE timeline ⭐ |
| **Act 4** — RBM | 13–14 | 5 min | Risk monitoring ⭐ |
| **Act 5** — Data Quality | 15–18 | 8 min | Queries, docs, audit |
| **Act 6** — Export & Lock | 19–20 | 5 min | Export, lock, closing |
| **Total** | | **~45 min** | |

> **Tip**: For a 20-minute quick demo, focus on Steps 1, 4, 6, 7 (Mobile EDC), 9, 11 (SAE Timeline), 13 (RBM), and 20 (closing).

---

## Credentials Quick Reference (Print This Page)

```
╔══════════════════════════════════════════════════════════════════════╗
║                    HACT CTMS — LOGIN CREDENTIALS                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  HACT CTMS:     https://ctms.hacts.org/                             ║
║    hact-user  / hact-user       (Full Access)                       ║
║    hact-admin / hact-admin      (Admin)                             ║
║    admin      / Admin@2026!     (Superuser)                         ║
║                                                                     ║
║  Mobile EDC:    https://ctms.hacts.org/edc                          ║
║    hact-user  / hact-user                                           ║
║                                                                     ║
║  SENAITE:       https://ctms.hacts.org/senaite/                     ║
║    admin      / admin                                               ║
║                                                                     ║
║  Nextcloud:     https://ctms.hacts.org/nextcloud/                   ║
║    admin      / Admin@2026                                          ║
║                                                                     ║
║  ERPNext:       https://ctms.hacts.org/erpnext/                     ║
║    Administrator / Admin@2026!                                      ║
║                                                                     ║
║  OpenClinica:   https://ctms.hacts.org/openclinica/                 ║
║    root       / 12345678                                            ║
║                                                                     ║
╚══════════════════════════════════════════════════════════════════════╝
```
