# HACT CTMS — End-to-End System Workflow &amp; Architecture
## Persona-Based Operational Guide (including Mobile EDC)

> **Version**: 2.0 — June 2026  
> **Prepared for**: Pod Lead Review  
> **Project**: HACT Clinical Trial Management System  
> **Protocol**: PSBI Neonatal Sepsis Trial (PSBI-2026-001)

---

## 1. System Architecture Overview

### 1.1 Platform Components

| # | System | Technology | Primary Function | Users |
|---|--------|-----------|-----------------|-------|
| 1 | **HACT CTMS** | Django 5 + React 18 | Operations Hub — enrollment, safety, monitoring, queries | All personas |
| 2 | **Mobile EDC** | React PWA (offline-first) | Field-level CRF data entry on tablets/phones | CRC, Nurse |
| 3 | **OpenClinica CE** | Java | CRF schema definition + legacy EDC | Data Manager (setup only) |
| 4 | **SENAITE LIMS** | Plone/Python | Laboratory sample tracking &amp; result publishing | Lab Technician |
| 5 | **Nextcloud** | PHP | Electronic Trial Master File (eTMF) document management | Regulatory, CRA |
| 6 | **ERPNext** | Python/Frappe | Site contracts, budgets, payments | Ops Manager |
| 7 | **Keycloak** | Java | Identity &amp; Access Management (SSO, RBAC, 2FA) | IT Admin |
| 8 | **PostgreSQL** | C | Primary relational database | System |
| 9 | **Redis + Celery** | Python | Async task queue, background jobs, Beat scheduler | System |
| 10 | **NGINX** | C | Reverse proxy, TLS termination, static file serving | System |

### 1.2 Key Architectural Principles

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     HACT CTMS ARCHITECTURAL PRINCIPLES                       │
│                                                                              │
│  1. SINGLE SOURCE OF TRUTH — Each system owns specific data exclusively      │
│  2. OFFLINE-FIRST EDC — Mobile EDC works without network via IndexedDB       │
│  3. AUTOMATED INTEGRATION — Celery tasks + webhooks, no manual sync          │
│  4. REGULATORY COMPLIANCE — ICH-GCP E6(R2/R3), 21 CFR Part 11, ALCOA+       │
│  5. ROLE-BASED ACCESS — 9 roles enforce least-privilege via Keycloak RBAC    │
│  6. AUDIT EVERYTHING — Full audit trail on every create/update/delete        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Persona Definitions

### 2.1 The 9 System Roles

| Persona | Role Code | Primary Responsibility | Systems Used Daily |
|---------|-----------|----------------------|-------------------|
| **Clinical Research Coordinator (CRC)** | `site_coordinator` | Screen &amp; enroll subjects, fill CRFs, attend to patients | Mobile EDC, HACT CTMS |
| **Data Manager (DM)** | `data_manager` | Data cleaning, query management, CRF design, exports | HACT CTMS, OpenClinica (setup) |
| **Study Admin / Principal Investigator (PI)** | `study_admin` | Study configuration, oversight, SAE review | HACT CTMS |
| **Safety Officer** | `safety_officer` | AE/SAE reporting, CIOMS generation, expedited reporting | HACT CTMS |
| **Clinical Research Associate (CRA/Monitor)** | `monitor` | Site monitoring, risk-based monitoring dashboard | HACT CTMS |
| **Lab Manager** | `lab_manager` | Lab result review, reference range management | HACT CTMS, SENAITE |
| **Operations Manager** | `ops_manager` | Budget tracking, site contracts, supply chain | HACT CTMS, ERPNext |
| **Regulatory / eTMF Manager** | `auditor` | Document management, audit trail review | HACT CTMS, Nextcloud |
| **System Administrator** | `admin` | User management, system configuration, integrations | Keycloak, HACT CTMS |

### 2.2 Access Matrix

```
                    Dashboard  Studies  Subjects  Queries  Safety  Lab  Monitoring  Audit  Integrations  Mobile EDC
                    ─────────  ───────  ────────  ───────  ──────  ───  ──────────  ─────  ────────────  ──────────
CRC (site_coord)       ✅        ✅       ✅        ✅       ─       ─       ─         ─         ─            ✅
Data Manager           ✅        ✅       ✅        ✅       ─       ─       ✅        ─         ─            ✅
Study Admin / PI       ✅        ✅       ✅        ✅       ✅      ✅      ✅        ✅        ✅           ✅
Safety Officer         ✅        ✅       ─         ─        ✅      ─       ✅        ─         ─            ✅
Monitor (CRA)          ✅        ✅       ✅        ✅       ─       ─       ✅        ─         ─            ✅
Lab Manager            ✅        ✅       ─         ─        ─       ✅      ─         ─         ─            ✅
Ops Manager            ✅        ─        ─         ─        ─       ─       ─         ─         ─            ─
Auditor                ✅        ✅       ─         ─        ─       ─       ─         ✅        ─            ─
Admin                  ✅        ✅       ✅        ✅       ✅      ✅      ✅        ✅        ✅           ✅
```

---

## 3. End-to-End System Workflow

### 3.1 Phase A: One-Time Study Setup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE A: STUDY SETUP (One-Time)                       │
│                                                                              │
│  WHO: Study Admin + Data Manager + IT Admin                                  │
│  WHEN: Before first patient enrollment                                       │
│  DURATION: 1-2 days                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  Step A1 ─── IT Admin ──── Keycloak
  │           Create user accounts, assign roles (CRC, DM, PI, etc.)
  │           Configure 2FA policies
  │
  Step A2 ─── Data Manager ── OpenClinica
  │           Create Study (OID: S_PSBI2026)
  │           Build CRF forms: Screening, 48h Assessment, Day 4, Day 8
  │           Define Events: Screening, Treatment, Follow-up
  │           Configure edit checks and validation rules
  │
  Step A3 ─── Study Admin ─── HACT CTMS
  │           Create Study (links to OC via Study OID)
  │           Create Sites (auto-triggers: ERPNext customer + Nextcloud eTMF folder)
  │           Set milestones and enrollment targets
  │
  Step A4 ─── Lab Manager ─── SENAITE LIMS
  │           Configure lab test catalog (CRP, Blood Culture, CBC)
  │           Set reference ranges per test
  │           Configure webhook → HACT CTMS
  │
  Step A5 ─── Ops Manager ─── ERPNext
  │           Set up site contracts and study budgets
  │           Link to HACT sites (auto-created in A3)
  │
  Step A6 ─── Study Admin ─── HACT CTMS
              Verify all integrations are connected (Integrations page)
              Run integration health check
              ✅ SETUP COMPLETE — Ready for enrollment
```

### 3.2 Phase B: Daily Clinical Operations

The following shows the complete data flow for a single subject from screening through completion.

---

#### B1: Subject Screening &amp; Enrollment (CRC via Mobile EDC)

```
  CRC at hospital ward (tablet/phone)
  │
  ├── Opens Mobile EDC (http://localhost:5173/edc)
  │   └── Works OFFLINE if no network — data stored in IndexedDB
  │
  ├── Tap "Enroll New Subject"
  │   ├── Enter: Subject ID (ETH-ADM-001-0005)
  │   ├── Enter: Screening # (SCR-0005)
  │   ├── Enter: Consent date, DOB, Sex
  │   └── Tap "Enroll" ──────────────────────┐
  │                                           │
  │   ┌───────────────────────────────────────┘
  │   │
  │   ▼  BACKEND PROCESSING (automatic)
  │   ├── Django creates Subject record (status: enrolled)
  │   ├── Celery task: sync_subject_to_openclinica()
  │   │   └── SOAP API → Subject appears in OpenClinica
  │   └── Audit trail: "Subject enrolled by CRC [user] at [timestamp]"
  │
  ├── Visit Schedule auto-generated for enrolled subject
  │   ├── V1: Screening & Enrollment (Day 0) — Due today
  │   ├── V2: 48-Hour Assessment (Day 2)
  │   ├── V3: Day 4 Follow-up
  │   ├── V4: Day 8 Follow-up
  │   └── Each visit shows assigned CRF forms
  │
  └── CRC taps V1 → sees assigned CRFs → starts data entry
```

#### B2: CRF Data Entry (CRC via Mobile EDC)

```
  CRC filling CRF on Mobile EDC (tablet at bedside)
  │
  ├── Tap Subject → Tap Visit → Tap Form (e.g., A1_SCREENING)
  │
  ├── Fill fields with validation:
  │   ├── DOB: [date picker] ← must be ≤ 59 days before enrollment
  │   ├── Weight: [number] ← range check: 1500-6000g
  │   ├── Temperature: [number] ← range: 35.0-42.0°C
  │   ├── Inclusion criteria: [radio] Yes/No
  │   ├── Exclusion criteria: [radio] Yes/No
  │   └── Treatment arm: [dropdown] Oral Amox / Injectable Gentamicin
  │
  ├── E-Signature (21 CFR Part 11):
  │   ├── Enter PIN or password
  │   ├── Meaning: "I confirm this data is accurate"
  │   └── Cryptographic hash stored with submission
  │
  ├── Tap "Submit CRF" ──────────────────────┐
  │                                           │
  │   ┌───────────────────────────────────────┘
  │   ▼  IF ONLINE:
  │   ├── POST /api/v1/edc/submit/ → Django saves to PostgreSQL
  │   ├── FormInstance created (status: submitted → signed)
  │   ├── ItemResponse records created for each field
  │   └── Audit trail: field-level change tracking
  │
  │   ▼  IF OFFLINE:
  │   ├── Data saved to IndexedDB (encrypted)
  │   ├── Sync badge shows "1 pending sync"
  │   └── Auto-syncs when network returns (background sync)
  │
  └── Visit status updates: "Due" → "Completed" ✅
```

#### B3: Lab Result Processing (Lab Tech → System → Clinician)

```
  Lab Technician at SENAITE LIMS
  │
  ├── Receives blood sample for ETH-ADM-001-0005
  ├── Runs CRP test → enters result: 8.2 mg/L
  ├── Publishes result in SENAITE
  │
  └── WEBHOOK fires automatically ──────────┐
                                             │
      ┌──────────────────────────────────────┘
      ▼  HACT CTMS (Django)
      ├── POST /api/v1/lab/webhook/senaite/
      ├── Creates LabResult record:
      │   ├── Subject: ETH-ADM-001-0005
      │   ├── Test: CRP
      │   ├── Value: 8.2 mg/L
      │   ├── Reference: 0-5.0 mg/L
      │   └── Flag: 🔴 HIGH (auto-calculated)
      │
      └── CRC/Clinician sees on HACT CTMS Lab page:
          "CRP 8.2 mg/L — HIGH" (no manual entry needed)
```

#### B4: Safety Reporting (PI/Safety Officer via HACT CTMS)

```
  Safety Officer / PI on HACT CTMS
  │
  ├── Navigate to Safety page → "Report AE"
  ├── Fill AE form:
  │   ├── Subject: ETH-ADM-001-0005
  │   ├── AE Term: "Severe diarrhoea with dehydration"
  │   ├── Start date: 2026-06-15
  │   ├── Severity: Severe
  │   ├── Serious: Yes (SAE)
  │   ├── SAE Criteria: Required hospitalization
  │   ├── Causality: Possible
  │   └── Outcome: Recovering
  │
  ├── Submit ────────────────────────────────┐
  │                                           │
  │   ┌───────────────────────────────────────┘
  │   ▼  BACKEND PROCESSING (automatic)
  │   ├── AdverseEvent record created
  │   ├── compute_deadline() → 15-day reporting deadline
  │   ├── reporting_status = "pending"
  │   ├── CIOMS I PDF auto-generated (if SAE)
  │   │
  │   ▼  CELERY BEAT (every 6 hours)
  │   ├── check_sae_reporting_deadlines()
  │   ├── At 50% elapsed → email notification ⚠️
  │   ├── At 90% elapsed → urgent email notification 🔴
  │   └── Past deadline → status = "overdue", escalation email
  │
  └── Monitoring Dashboard shows:
      ├── SAE Expedited Reporting Timeline
      ├── Countdown timer: "12.5 days remaining"
      └── "Mark Reported" button when submitted to EFDA
```

#### B5: Data Cleaning (Data Manager via HACT CTMS)

```
  Data Manager on HACT CTMS
  │
  ├── Navigate to Queries page
  ├── Review open queries (auto-generated or manual)
  │
  ├── Example query: "Weight 320g for Subject 0005 — please verify"
  │   ├── CRC answers: "Typo — correct weight is 3200g"
  │   ├── DM reviews → closes query
  │   └── Audit trail records entire conversation
  │
  ├── Data Quality Score updates automatically
  │   └── Dashboard shows: "92% — 2 queries remaining"
  │
  └── When all queries resolved:
      └── Study Admin can initiate database lock
```

#### B6: Risk-Based Monitoring (CRA/Monitor via HACT CTMS)

```
  Clinical Research Associate (Monitor) on HACT CTMS
  │
  ├── Navigate to Monitoring page (/monitoring)
  │
  ├── SECTION 1: Study Risk Overview
  │   ├── Total Sites: 2
  │   ├── High Risk: 0 | Medium Risk: 1 | Low Risk: 1
  │   ├── Overdue SAEs: 0
  │   └── Open Queries: 3
  │
  ├── SECTION 2: Site Risk Heatmap
  │   ├── ETH-ADM-001: Score 78 (Medium Risk)
  │   │   ├── Enrollment Rate: 0.35 subj/month (below target)
  │   │   ├── Query Rate: 1.5 open/subject (acceptable)
  │   │   ├── AE Reporting: 0.8 AEs/subject (acceptable)
  │   │   ├── CRF Completion: 85% (below 95% target)
  │   │   └── Overdue SAEs: 0 (good)
  │   │
  │   └── ETH-JMC-002: Score 92 (Low Risk)
  │       ├── All KPIs within acceptable ranges ✅
  │       └── No action required
  │
  └── SECTION 3: SAE Expedited Reporting Timeline
      ├── SAE-1: "Severe diarrhoea" — 12.5d remaining (green)
      └── SAE-2: "Neonatal death" — 2.1d remaining (red, urgent)
```

---

## 4. Complete Data Flow Architecture

```
                            ┌─────────────────────┐
                            │    KEYCLOAK SSO      │
                            │  ┌───────────────┐   │
                            │  │ 9 RBAC Roles  │   │
                            │  │ OIDC + 2FA    │   │
                            │  └───────────────┘   │
                            └─────────┬───────────┘
                                      │ JWT Tokens (OIDC PKCE)
                    ┌─────────────────┼──────────────────┐
                    │                 │                    │
                    ▼                 ▼                    ▼
    ┌──────────────────┐  ┌─────────────────────┐  ┌──────────────────┐
    │   MOBILE EDC     │  │    HACT CTMS        │  │   HACT CTMS      │
    │   (React PWA)    │  │   (React SPA)       │  │  (Django REST)   │
    │                  │  │                     │  │                  │
    │ • Offline-first  │  │ • Dashboard         │  │ • REST API       │
    │ • IndexedDB      │  │ • Studies/Subjects  │  │ • Celery Workers │
    │ • E-Signature    │  │ • Safety/Lab        │  │ • Beat Scheduler │
    │ • CRF forms      │  │ • Monitoring (RBM)  │  │ • Audit Signals  │
    │ • Background     │  │ • Queries/Audit     │  │ • Webhooks       │
    │   sync           │  │                     │  │                  │
    └───────┬──────────┘  └─────────┬───────────┘  └────────┬─────────┘
            │  HTTP POST             │  API calls           │
            │  /api/v1/edc/*         │                      │
            └────────────────────────┘                      │
                                                            │
                         ┌──────────────────────────────────┤
                         │              POSTGRESQL          │
                         │    ┌─────────────────────────┐   │
                         │    │ Studies, Sites, Subjects │   │
                         │    │ Form Instances, Items    │   │
                         │    │ Adverse Events, Queries  │   │
                         │    │ Lab Results, Audit Logs  │   │
                         │    │ CIOMS Forms, Milestones  │   │
                         │    └─────────────────────────┘   │
                         └──────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                    │
          Celery: SOAP API    Celery: WebDAV       Celery: REST API
          (auto-sync)         (auto-create)        (auto-create)
                    │                   │                    │
                    ▼                   ▼                    ▼
          ┌──────────────┐   ┌──────────────┐    ┌──────────────┐
          │ OPENCLINICA  │   │  NEXTCLOUD   │    │   ERPNEXT    │
          │    (EDC)     │   │   (eTMF)     │    │   (Finance)  │
          │              │   │              │    │              │
          │ CRF schema   │   │ Protocol     │    │ Contracts    │
          │ definition   │   │ documents    │    │ Budgets      │
          │ (setup only) │   │ IRB letters  │    │ Payments     │
          └──────────────┘   │ Site docs    │    └──────────────┘
                             └──────────────┘
                    ▲
                    │ Webhook POST (auto-push lab results)
                    │
          ┌──────────────┐
          │   SENAITE    │
          │   (LIMS)     │
          │              │
          │ Lab samples  │
          │ Test results │
          │ QC workflow  │
          └──────────────┘
```

---

## 5. Mobile EDC — Offline-First Architecture

### 5.1 Why Mobile EDC Exists

| Challenge | Solution |
|-----------|----------|
| CRCs work at bedsides with unreliable WiFi | **Offline-first PWA** — works without network |
| Paper CRFs cause transcription errors | **Direct digital entry** with real-time validation |
| OpenClinica UI is not mobile-friendly | **Touch-optimized React PWA** for tablets/phones |
| Need 21 CFR Part 11 e-signatures | **PIN-based e-signature** with cryptographic hash |

### 5.2 Mobile EDC Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE EDC (React PWA)                     │
│                                                               │
│   ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │
│   │  Enroll   │    │  Visit   │    │  CRF Form Entry      │  │
│   │  Subject  │    │ Schedule │    │  with Validation      │  │
│   └─────┬────┘    └────┬─────┘    │  + E-Signature        │  │
│         │              │           └──────────┬───────────┘  │
│         │              │                      │               │
│         └──────────────┼──────────────────────┘               │
│                        │                                      │
│                        ▼                                      │
│              ┌─────────────────────┐                         │
│              │    ONLINE?          │                          │
│              └──┬──────────────┬──┘                          │
│            YES  │              │  NO                          │
│                 ▼              ▼                               │
│    ┌─────────────────┐  ┌─────────────────┐                 │
│    │ POST to Django   │  │ Save to          │                │
│    │ /api/v1/edc/*    │  │ IndexedDB        │                │
│    │                  │  │ (encrypted)      │                │
│    │ → Immediate      │  │                  │                │
│    │   confirmation   │  │ "1 pending sync" │                │
│    └─────────────────┘  └────────┬──────────┘                │
│                                  │                            │
│                          When network returns:                │
│                                  │                            │
│                          ┌───────▼──────────┐                │
│                          │ Background Sync   │                │
│                          │ Replay queue      │                │
│                          │ Deduplicate by    │                │
│                          │ submission_uuid   │                │
│                          └──────────────────┘                │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 5.3 Mobile EDC vs. OpenClinica — What Changed

| Before (v1.0) | After (v2.0 with Mobile EDC) |
|----------------|------------------------------|
| CRC opens OpenClinica on desktop to fill CRFs | CRC uses Mobile EDC on tablet at bedside |
| No offline support — needs stable WiFi | Works fully offline, syncs when connected |
| Desktop-only UI, not touch-friendly | Touch-optimized for tablets and phones |
| Separate login to OpenClinica | Same Keycloak SSO as HACT CTMS |
| No integrated e-signature | Built-in 21 CFR Part 11 e-signature |
| OpenClinica used daily for data entry | OpenClinica used only for CRF schema setup |

---

## 6. Persona Workflow Narratives

### 6.1 A Day in the Life: CRC (Clinical Research Coordinator)

**Persona**: Nurse Tigist at Addis Ababa Medical Center  
**Device**: Samsung Galaxy Tab A (Android tablet)  
**Network**: Hospital WiFi (intermittent)

```
07:30  🔐 ARRIVE at hospital → Open Mobile EDC on tablet
       → Login with Keycloak SSO → Dashboard loads
       → See: 8 enrolled subjects, 2 visits due today

08:00  👶 NEW INFANT arrives — mother brings 3-day-old with fever
       → Mobile EDC → "Enroll New Subject"
       → Enter: ETH-ADM-001-0006, consent signed ✅
       → Tap "Enroll" → Subject created instantly
       → Visit schedule appears: V1 (Screening) due today

08:15  📋 FILL SCREENING CRF at bedside (V1: A1_SCREENING)
       → Mobile EDC → Subject 0006 → V1 → A1_SCREENING
       → Enter: DOB, Sex (M), Weight (2800g), Temp (38.2°C)
       → Inclusion criteria met: Yes
       → Treatment arm: Oral Amoxicillin
       → E-Sign with PIN → Submit ✅
       → Visit status: "Due" → "Completed"

09:00  📋 48-HOUR ASSESSMENT for yesterday's patient (0005)
       → Mobile EDC → Subject 0005 → V2 → B1_48H_ASSESSMENT
       → Enter: Temp (37.1°C), Feeding (normal), CRITILL (No)
       → Decision: Can be discharged ✅
       → E-Sign → Submit ✅
       ⚠️ WiFi drops! → "1 pending sync" badge appears
       → Continues working — data saved to IndexedDB

10:00  🔬 LAB RESULTS arrive automatically (no action needed)
       → Open HACT CTMS on desktop
       → Lab page: CRP 8.2 mg/L for Subject 0006 — flagged 🔴 HIGH
       → No manual entry — SENAITE webhook delivered it

11:00  ⚠️ Subject 0003 develops severe reaction
       → Informs PI → PI reports SAE on HACT CTMS Safety page
       → CRC continues patient care

12:00  📱 WIFI RETURNS → Mobile EDC auto-syncs
       → "1 pending sync" → "0 pending syncs" ✅
       → All data safely in PostgreSQL

14:00  📊 DATA MANAGER calls: "Resolve query on weight for 0001"
       → HACT CTMS → Queries → Open query
       → Answer: "Confirmed 3200g — Seca 354 scale, calibrated"
       → Query closed ✅

16:00  📈 CHECK DASHBOARD before leaving
       → Enrollment: 9/300 subjects
       → Data quality: 94%
       → All systems: ✅ online
       → Logout
```

**CRC's systems used**: Mobile EDC (70%), HACT CTMS (30%), Others (0%)

---

### 6.2 A Day in the Life: Data Manager

**Persona**: Abebe, MSc Biostatistics  
**Device**: Desktop computer  
**Location**: HACT Data Center, Addis Ababa

```
08:00  🔐 LOGIN to HACT CTMS via Keycloak SSO
       → Dashboard: 3 new queries auto-generated overnight
       → Data quality score: 91% (was 93% yesterday)

08:30  📊 REVIEW MONITORING DASHBOARD
       → Navigate to /monitoring
       → Site Risk Heatmap:
         ETH-ADM-001: Score 78 (Medium) — CRF completion at 85%
         ETH-JMC-002: Score 92 (Low) — all KPIs green
       → Note: ETH-ADM-001 needs attention on CRF completion

09:00  🔍 RESOLVE DATA QUERIES
       → Queries page → 3 open queries
       → Q1: "Temperature 42.5°C for Subject 0003 — verify"
         → Contact CRC → Confirmed correct (high fever)
         → Close query with note: "Verified with CRC Tigist"
       → Q2: "Weight 320g — likely missing digit"
         → Contact CRC → Should be 3200g
         → Close query: "Corrected from 320g to 3200g"
       → Q3: "Consent date after enrollment date"
         → Contact site → Data entry error
         → Close query: "CRC to correct in Mobile EDC"

10:00  📋 REVIEW CRF SUBMISSIONS
       → Check form instances from Mobile EDC
       → All submissions have e-signatures ✅
       → Cross-reference with visit schedule completeness

11:00  📤 EXPORT DATA for interim analysis
       → HACT CTMS → Studies → PSBI study → Export
       → Choose format: CSV for SAS import
       → Generate → Download zip with all tables

14:00  📧 RESPOND to sponsor query on data discrepancy rate
       → Run quality report: Discrepancy rate = 2.1%
       → Below threshold (5%) → respond with report

16:00  📈 END OF DAY CHECK
       → Data quality: 94% (improved from 91%)
       → 0 open queries remaining
       → All CRFs for today submitted and signed
       → Logout
```

**DM's systems used**: HACT CTMS (95%), OpenClinica Admin (5% — setup only)

---

### 6.3 A Day in the Life: Safety Officer

**Persona**: Dr. Miriam, MD, Safety Officer  
**Device**: Desktop computer

```
08:00  🔐 LOGIN → Check SAE Expedited Reporting Timeline
       → /monitoring → SAE Timeline section
       → 1 pending SAE: "Severe diarrhoea" — 12.5 days remaining (green)
       → 0 overdue SAEs ✅

09:00  ⚠️ PI reports new SAE via HACT CTMS Safety page
       → AE Term: "Neonatal death due to septic shock"
       → SAE Criteria: Death → 7-DAY DEADLINE auto-computed
       → Reporting deadline: 2026-07-03

09:30  📋 PREPARE CIOMS I FORM for EFDA submission
       → Safety page → SAE record → "Generate CIOMS PDF"
       → Auto-populated with subject data, AE details, causality
       → Review → Download PDF
       → Submit to EFDA via email

10:00  ✅ MARK SAE AS REPORTED
       → /monitoring → SAE Timeline → "Mark Reported"
       → Status changes: "Pending" → "On Time"
       → reported_to_authority_at timestamp recorded

14:00  📊 WEEKLY SAFETY REVIEW
       → Review all AEs across study
       → Check for patterns: any sites with unusual AE rates?
       → Monitoring dashboard shows: ETH-ADM-001 AE rate = 0.8/subject (normal)
       → No safety signals detected
```

---

### 6.4 A Day in the Life: Monitor (CRA)

**Persona**: Sara, Clinical Research Associate  
**Device**: Laptop (remote monitoring)

```
08:00  🔐 LOGIN → Navigate to /monitoring (Risk-Based Monitoring)

08:15  📊 STUDY RISK OVERVIEW
       → Total Sites: 2
       → Overall Risk: Medium (1 site medium, 1 low)
       → Overdue SAEs: 0 | Open Queries: 2

09:00  🔍 SITE RISK DEEP DIVE
       → Click ETH-ADM-001 row → expand KPIs
       → Enrollment Rate: 0.35/month (score: 18) — 🔴 HIGH RISK
       → Query Rate: 1.5/subject (score: 100) — 🟢
       → CRF Completion: 85% (score: 89) — 🟢
       → Action: Schedule call with PI to discuss enrollment barriers

10:00  📋 REVIEW SAE TIMELINE
       → 1 SAE with 7-day deadline — submitted to EFDA (On Time) ✅
       → No action needed

14:00  📝 PREPARE MONITORING REPORT
       → Export monitoring data for sponsor report
       → Document risk findings and recommended actions
       → Upload to Nextcloud eTMF (Zone 7: Monitoring)

16:00  📧 SEND FOLLOW-UP LETTER to ETH-ADM-001
       → Subject: "Action Required: Enrollment Rate Below Target"
       → Attach risk score screenshot from monitoring dashboard
```

---

## 7. System Integration Map

### 7.1 What Gets Synced Automatically vs. Manually

| Data Flow | Direction | Method | Trigger | Frequency |
|-----------|-----------|--------|---------|-----------|
| Subject enrollment | HACT CTMS → OpenClinica | SOAP API via Celery | On enrollment | Instant |
| Lab results | SENAITE → HACT CTMS | Webhook POST | On result publish | Instant |
| eTMF folders | HACT CTMS → Nextcloud | WebDAV via Celery | On site creation | One-time |
| Site records | HACT CTMS → ERPNext | REST API via Celery | On site creation | One-time |
| SSO auth | Keycloak → All systems | OIDC PKCE | On every login | Per session |
| Mobile EDC CRFs | Mobile EDC → Django | REST API | On submit/sync | Instant/Batch |
| SAE deadline alerts | Django → Email | SMTP via Celery Beat | Every 6 hours | Periodic |
| Integration health | Django → All systems | REST/SOAP | Every 10 minutes | Periodic |

### 7.2 Data Ownership — No Duplication Rule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA OWNERSHIP MATRIX                                 │
│                                                                              │
│  HACT CTMS OWNS:                    │  EXTERNAL SYSTEMS OWN:                │
│  ─────────────────                  │  ──────────────────────               │
│  ✅ Subject enrollment records      │  ✅ CRF form schema (OpenClinica)     │
│  ✅ Subject status lifecycle        │  ✅ Raw lab test workflow (SENAITE)    │
│  ✅ Adverse Events / SAEs           │  ✅ Regulatory documents (Nextcloud)   │
│  ✅ CIOMS I PDFs                    │  ✅ Contracts & budgets (ERPNext)      │
│  ✅ Data Queries                    │  ✅ User identities & roles (Keycloak)│
│  ✅ Lab Results (imported copy)     │                                        │
│  ✅ CRF data (via Mobile EDC)       │                                        │
│  ✅ Study milestones                │                                        │
│  ✅ Full audit trail                │                                        │
│  ✅ Risk monitoring scores          │                                        │
│  ✅ SAE reporting timelines         │                                        │
│                                     │                                        │
│  MOBILE EDC is part of HACT CTMS — same database, same API                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Regulatory Compliance Mapping

| Requirement | Standard | HACT CTMS Implementation |
|-------------|----------|-------------------------|
| Electronic signatures | 21 CFR Part 11 | Mobile EDC e-signature with PIN + cryptographic hash |
| Audit trail | 21 CFR Part 11 | Django audit signals on all model changes |
| Data integrity (ALCOA+) | ICH E6(R2) | Timestamped, attributable records with audit trail |
| Risk-based monitoring | ICH E6(R3) | Centralized monitoring dashboard with per-site KPIs |
| Expedited SAE reporting | ICH E6(R2) / FDA 21 CFR 312.32 | Auto-computed 7/15-day deadlines with email alerts |
| CIOMS I reporting | WHO/CIOMS | Auto-generated PDF from adverse event data |
| Role-based access | GCP | 9 roles in Keycloak with route-level enforcement |
| Data backup | GCP | PostgreSQL automated backups, Redis persistence |
| System validation | GCP | IQ/OQ/PQ documentation framework |

---

## 9. Deployment Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                               │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  NGINX   │  │ Django   │  │ Celery   │  │  Celery Beat     │   │
│  │  :80/443 │──│ Gunicorn │──│ Worker   │  │  (Scheduler)     │   │
│  │  Proxy   │  │ :8000    │  │          │  │  SAE deadlines   │   │
│  └──────────┘  └──────────┘  └──────────┘  │  Integration     │   │
│       │                │          │         │  health checks   │   │
│       │                │          │         └──────────────────┘   │
│       │         ┌──────┴──────┐   │                                │
│       │         │  PostgreSQL │   │                                │
│       │         │    :5432    │   │                                │
│       │         └─────────────┘   │                                │
│       │                           │                                │
│       │         ┌─────────────┐   │                                │
│       │         │    Redis    │───┘                                │
│       │         │    :6379    │   Task queue + caching             │
│       │         └─────────────┘                                    │
│       │                                                            │
│  ┌────┴─────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Keycloak │  │ SENAITE  │  │Nextcloud │  │ ERPNext  │          │
│  │  :8080   │  │  :8081   │  │  :8082   │  │  :8083   │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                    │
│  ┌──────────┐                                                      │
│  │OpenClinica│                                                     │
│  │  :8084   │                                                      │
│  └──────────┘                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 10. Summary: Three Golden Rules

### Rule 1: HACT CTMS + Mobile EDC = The Hub
All clinical operations flow through HACT CTMS and its Mobile EDC. CRCs use the Mobile EDC for bedside data entry. Everyone else uses the HACT CTMS web dashboard. All data lives in one PostgreSQL database.

### Rule 2: External Systems Are Specialists
OpenClinica defines CRF schemas (setup). SENAITE pushes lab results (automatic). Nextcloud stores documents. ERPNext tracks finances. Keycloak handles identity. Each system does ONE job.

### Rule 3: Mobile EDC Replaced Daily OpenClinica Use
Before: CRCs logged into OpenClinica daily to fill CRFs (desktop only, no offline).  
After: CRCs use Mobile EDC on tablets at the bedside (offline-first, e-signatures, touch-optimized).  
OpenClinica is now a setup-only tool for Data Managers.

---

*Document prepared for HACT CTMS Pod Lead review — June 2026*
