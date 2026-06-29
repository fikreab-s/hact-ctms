# HACT CTMS — System Architecture & Operations Guide
## How the 6 Systems Work Together (No Duplication)

---

## The #1 Rule: Each System Has ONE Job

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM RESPONSIBILITIES                         │
│                                                                         │
│  HACT CTMS (Django + React)     →  OPERATIONS HUB (single source)      │
│  OpenClinica CE                 →  CRF DATA ENTRY ONLY                 │
│  SENAITE LIMS                   →  LAB RESULTS ONLY                    │
│  Nextcloud                      →  DOCUMENTS ONLY (eTMF)               │
│  ERPNext                        →  CONTRACTS & BUDGETS ONLY            │
│  Keycloak                       →  AUTHENTICATION ONLY (SSO)           │
│                                                                         │
│  ⚠️  Users interact with HACT CTMS for everything EXCEPT:              │
│      • Filling CRF forms → OpenClinica                                 │
│      • Running lab tests → SENAITE                                     │
│      • Uploading regulatory docs → Nextcloud                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Setup vs. Daily Operations — Two Different Phases

### Phase A: ONE-TIME SETUP (Before Trial Starts)

This happens **once** when the Data Manager configures the study. Think of it like building a house — you design the blueprint once, then people live in it daily.

| Step | System | What You Do | Why | Who |
|------|--------|-------------|-----|-----|
| A1 | **OpenClinica** | Create Study, CRFs, Events, Sites | Define the "forms schema" — what data will be captured | Data Manager |
| A2 | **HACT CTMS** | Create Study (links to OC via OID) | Define operations — milestones, dashboard, integrations | Study Admin |
| A3 | **HACT CTMS** | Create Sites | Auto-creates ERPNext records + Nextcloud eTMF folders | Study Admin |
| A4 | **Keycloak** | Create user accounts & assign roles | SSO for all systems | IT Admin |
| A5 | **SENAITE** | Configure lab tests & reference ranges | Define what lab tests are available | Lab Manager |
| A6 | **ERPNext** | Set up contracts & budgets | Financial tracking | Ops Manager |

> **After setup, you NEVER touch OpenClinica admin again** (except to enter CRF data for patients).

### Phase B: DAILY OPERATIONS (During Trial)

This is what happens every day when clinical staff use the system:

| Step | System | What Happens | Who |
|------|--------|-------------|-----|
| B1 | **HACT CTMS** | Login via Keycloak SSO | Everyone |
| B2 | **HACT CTMS** | Screen & enroll new infant | CRC / Nurse |
| B3 | *automatic* | → Subject synced to OpenClinica (Celery task) | System |
| B4 | **OpenClinica** | Fill CRF (clinical data: weight, temp, signs) | CRC / Nurse |
| B5 | *automatic* | → Lab results arrive from SENAITE (webhook) | System |
| B6 | **HACT CTMS** | View lab results (auto-flagged H/L/N) | Clinician |
| B7 | **HACT CTMS** | Report SAE → auto-generate CIOMS PDF | PI / Safety Officer |
| B8 | **HACT CTMS** | Resolve data queries | Data Manager |
| B9 | **HACT CTMS** | Check dashboard — enrollment, quality score | Study Admin |
| B10 | **Nextcloud** | Upload protocol docs, IRB letters | Regulatory |

---

## What Goes Where — The Complete Data Map

### Data That Lives ONLY in HACT CTMS (Django)

| Data | Created By | Used For |
|------|-----------|----------|
| Subject enrollment record | CRC via frontend | Tracking who is enrolled, consent dates |
| Subject status lifecycle | System (screened → enrolled → completed) | Workflow enforcement |
| Adverse Events / SAEs | PI via frontend | Safety reporting, CIOMS generation |
| CIOMS I PDFs | Auto-generated | Regulatory submission to EFDA |
| Data Queries | Data Manager via frontend | Data cleaning before lock |
| Lab Results | Auto-imported from SENAITE webhook | Clinical review, flagging |
| Study milestones | Study Admin via frontend | Timeline tracking |
| Audit trail (operations) | Auto-recorded by Django signals | 21 CFR Part 11 compliance |
| Data quality score | Auto-calculated | Dashboard metric |
| Study lock status | Study Admin | Database freeze |

### Data That Lives ONLY in OpenClinica

| Data | Created By | Used For |
|------|-----------|----------|
| CRF form data (A1, B1, B2, C1) | CRC filling forms | Clinical data capture |
| CRF audit trail | Auto-recorded by OpenClinica | 21 CFR Part 11 for CRF changes |
| ODM XML exports | Data Manager | CDISC regulatory submission |
| CRF edit checks / validation | System | Data quality at entry |
| E-signatures on CRFs | PI | 21 CFR Part 11 sign-off |

### Data That Lives ONLY in SENAITE

| Data | Created By | Used For |
|------|-----------|----------|
| Lab sample records | Lab Technician | Sample tracking |
| Lab test results (raw) | Lab Technician | Testing workflow |
| Reference ranges (lab-side) | Lab Manager | Quality control |

### Data That Lives ONLY in Nextcloud

| Data | Created By | Used For |
|------|-----------|----------|
| Protocol documents | Regulatory team | eTMF Zone 1 |
| IRB/Ethics approvals | Regulatory team | eTMF Zone 2 |
| Site documents | Site staff | eTMF Zone 4 |
| Monitoring reports | CRA | eTMF Zone 7 |

### Data That Lives ONLY in ERPNext

| Data | Created By | Used For |
|------|-----------|----------|
| Site contracts | Ops Manager | Legal/financial |
| Study budgets | Ops Manager | Cost tracking |
| Invoices / payments | Finance | Site payments |

### Data That Lives ONLY in Keycloak

| Data | Created By | Used For |
|------|-----------|----------|
| User accounts | IT Admin | Authentication |
| Roles & permissions | IT Admin | RBAC |
| SSO sessions & tokens | System | Security |
| 2FA configuration | Each user | MFA |

---

## The "Duplication" Question — Answered

### Q: "Why do I create Study in BOTH HACT CTMS and OpenClinica?"

**A: Because they serve completely different purposes:**

| | HACT CTMS | OpenClinica |
|--|-----------|-------------|
| **What the study record holds** | Protocol number, sponsor, milestones, budget link, dashboard data, lock status | CRF definitions, events, form schema, validation rules |
| **Why it exists** | To run the trial operationally | To capture clinical CRF data |
| **Who touches it daily** | Everyone (dashboard, queries, SAEs) | Only CRF data entry staff |
| **Connected to** | ERPNext, Nextcloud, SENAITE, Keycloak | Nothing (standalone EDC) |

**They are linked by the Study OID** (`S_PSBI2026`). You enter this OID in HACT CTMS once, and from that point the systems know they're talking about the same study.

### Q: "Why do I create Sites in BOTH systems?"

**A: Because HACT CTMS sites trigger 3 automatic actions that OpenClinica doesn't do:**

```
When you create a site in HACT CTMS:
  ├── ✅ ERPNext: Creates a "Customer" record for contracts & payments
  ├── ✅ Nextcloud: Creates eTMF/HACT-PSBI-ETH-2026/04_Site_Documents/ETH-ADM-001/
  └── ✅ Audit Trail: Records who created the site and when

When you create a site in OpenClinica:
  └── ✅ Tells OpenClinica which subjects belong to which site
      (that's all — no integrations)
```

### Q: "Why don't I create Subjects in OpenClinica manually?"

**A: You don't! This is already automated:**

```
CRC clicks "Enroll" in HACT CTMS
  │
  ├── Django saves subject → PostgreSQL
  │
  └── Celery task fires automatically:
      sync_subject_to_openclinica(subject_id)
        │
        └── SOAP API call to OpenClinica
            → Creates subject ETH-ADM-001-0001
            → Ready for CRF data entry
```

The subject appears in OpenClinica **without anyone touching OpenClinica**. Zero duplication.

---

## Real-World Daily Workflow — A CRC's Typical Day

### Scenario: Clinical Research Coordinator (CRC) at Adama General Hospital

```
08:00  🔐 Open browser → go to HACT CTMS (http://localhost)
       → Click "Sign in with Keycloak SSO"
       → Enter credentials → Dashboard loads
       → See: 12 enrolled, 3 open queries, 1 SAE pending

08:15  👶 New infant arrives — mother brought 4-day-old with fever
       → HACT CTMS → Subjects → "New Subject"
       → Enter: ID = ETH-ADM-001-0005, Screening # = SCR-0005
       → Click "Create" → Status: screened
       → Check consent → Click "Enroll"
       → ✅ Subject auto-appears in OpenClinica (no manual step!)

08:30  📋 Fill Screening CRF → Open OpenClinica tab
       → Subject Matrix → ETH-ADM-001-0005 is already there!
       → Schedule "Screening and Enrollment" event
       → Fill A1_SCREEN_ENROLL:
         • DOB: 2026-06-09, Sex: M, Weight: 3200g
         • Inclusion met: Yes, Exclusion: No
         • Treatment arm: Oral Amoxicillin
       → Mark Complete

09:00  🔬 Lab tech runs CRP in SENAITE → publishes result
       → Webhook fires → Django receives CRP = 8.2 mg/L (HIGH)
       → CRC sees it on HACT CTMS Lab page: 🔴 CRP 8.2 (HIGH)
       → No manual entry — it appeared automatically

10:00  📋 48-hour assessment for yesterday's patient (ETH-ADM-001-0004)
       → Open OpenClinica → Subject Matrix → ETH-ADM-001-0004
       → Schedule "48-Hour Assessment" event
       → Fill B1_RCT2_48H:
         • Temp: 37.1°C, Feeding: normal, CRITILL: No
         • Decision: Can be discharged ✅

11:00  ⚠️ Infant ETH-ADM-001-0003 develops diarrhoea
       → HACT CTMS → Safety → "Report AE"
       → Fill SAE form → severity: Severe, causality: Possible
       → Click Submit → CIOMS I PDF auto-generated
       → Download PDF → send to EFDA within 15 days

14:00  📊 Data Manager calls: "Resolve query on weight for 0001"
       → HACT CTMS → Queries → Open query
       → Answer: "Confirmed — Seca 354 scale, calibrated 2026-06-01"
       → Close query ✅

16:00  📈 Check Dashboard before leaving
       → Enrollment: 13/300 (4.3%)
       → Data Quality: 92% (2 open queries remaining)
       → All systems: ✅ online
       → Log out
```

### Notice: The CRC Touched Only 2 Systems All Day

| System | Time Spent | What They Did |
|--------|-----------|--------------|
| **HACT CTMS** | 80% of time | Login, enroll, lab review, SAE, queries, dashboard |
| **OpenClinica** | 20% of time | Fill CRF forms (clinical data only) |
| SENAITE | 0% | Lab tech handled it; results arrived automatically |
| Nextcloud | 0% | Regulatory staff handles documents separately |
| ERPNext | 0% | Ops manager handles contracts separately |
| Keycloak | 0% | Just the SSO login — transparent to user |

---

## Architecture Diagram — Data Flow

```
                         ┌──────────────────┐
                         │    KEYCLOAK SSO   │
                         │  (Authentication) │
                         └────────┬─────────┘
                                  │ OIDC PKCE tokens
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    HACT CTMS (Django + React)                │
│                    ══════════════════════                    │
│                                                              │
│  React Frontend ──► Django REST API ──► PostgreSQL           │
│                          │                                   │
│                    Celery Workers                             │
│                    ┌─────┼──────┐                            │
│                    │     │      │                             │
│               ┌────▼──┐ │  ┌───▼────┐                       │
│               │Sync   │ │  │eTMF    │                       │
│               │Subject│ │  │Folders │                       │
│               │to OC  │ │  │Create  │                       │
│               └───┬───┘ │  └───┬────┘                       │
│                   │     │      │                              │
└───────────────────┼─────┼──────┼────────────────────────────┘
                    │     │      │
         SOAP API   │     │      │  WebDAV API
         (auto)     │     │      │  (auto)
                    ▼     │      ▼
          ┌──────────┐   │   ┌──────────┐
          │OpenClinica│   │   │Nextcloud │
          │   (EDC)   │   │   │  (eTMF)  │
          │           │   │   │          │
          │ CRF Data  │   │   │Documents │
          │ Entry     │   │   │Version   │
          │ Only      │   │   │Control   │
          └──────────┘   │   └──────────┘
                         │
              Webhook    │    REST API
              (auto)     │    (auto)
                         │
               ┌─────────┴──────────┐
               │                    │
          ┌────▼─────┐      ┌──────▼───┐
          │ SENAITE  │      │ ERPNext  │
          │  (LIMS)  │      │  (Ops)   │
          │          │      │          │
          │Lab Tests │      │Contracts │
          │Results   │      │Budgets   │
          └──────────┘      └──────────┘
```

**All arrows are AUTOMATIC** — Celery tasks and webhooks handle data flow. No manual copy-paste between systems.

---

## What Gets Synced Automatically vs. What's Manual

| Data Flow | Direction | Method | Manual or Auto? |
|-----------|-----------|--------|----------------|
| Subject enrollment | HACT CTMS → OpenClinica | SOAP API (Celery) | ✅ **Automatic** |
| Lab results | SENAITE → HACT CTMS | Webhook POST | ✅ **Automatic** |
| eTMF folders | HACT CTMS → Nextcloud | WebDAV API (Celery) | ✅ **Automatic** |
| Site records | HACT CTMS → ERPNext | REST API (Celery) | ✅ **Automatic** |
| SSO authentication | Keycloak → all systems | OIDC PKCE | ✅ **Automatic** |
| | | | |
| Study setup | Admin → OpenClinica | Manual (one-time) | ⚡ **One-time manual** |
| CRF setup | Admin → OpenClinica | Manual (one-time) | ⚡ **One-time manual** |
| Site setup in OC | Admin → OpenClinica | Manual (one-time) | ⚡ **One-time manual** |
| Study setup | Admin → HACT CTMS | Manual (one-time) | ⚡ **One-time manual** |
| Site setup | Admin → HACT CTMS | Manual (one-time) | ⚡ **One-time manual** |
| | | | |
| CRF data entry | CRC → OpenClinica | Manual (daily) | 📋 **Daily manual** |
| SAE reporting | PI → HACT CTMS | Manual (when needed) | 📋 **When needed** |
| Query resolution | DM → HACT CTMS | Manual (daily) | 📋 **Daily manual** |
| Document upload | Regulatory → Nextcloud | Manual (as needed) | 📋 **As needed** |

---

## Summary: The 3 Rules

### Rule 1: HACT CTMS is the Hub
All roads lead through HACT CTMS. Users login here, manage here, report here. It's the operational nerve center.

### Rule 2: OpenClinica is the Form Filler
OpenClinica's only daily job is CRF data entry. Everything else (enrollment, safety, labs, queries, dashboard) happens in HACT CTMS.

### Rule 3: Setup ≠ Operations
Creating studies/CRFs/sites in OpenClinica is a **one-time admin setup** — like installing an app. Using the system daily is different — and there's zero duplication in daily use.
