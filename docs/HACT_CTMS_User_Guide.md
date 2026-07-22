# HACT CTMS — General User Guide

### A complete, role-by-role guide to using the HACT Clinical Trial Management System and its integrated tools

**Audience:** Anyone new to the HACT platform — study administrators, data managers, site coordinators, monitors, safety officers, lab managers, operations managers, and auditors.
**What you'll learn:** What every tool does, who uses it and when, how the systems talk to each other, and the exact sequential steps to run a clinical study from creation to database lock.

> **Companion documents**
> - `docs/Deployed_System_Test_Execution_Guide.md` — a 20-step, click-by-click walkthrough you can use to validate a deployed environment.
> - `docs/SENAITE_Lab_Integration_Guide.md` — deep dive on the laboratory (LIMS) integration.
> - `docs/OpenClinica_CRF_Data_Entry_User_Guide.md` — CRF data-entry reference for OpenClinica.

---

## Table of Contents

1. [What is HACT CTMS?](#1-what-is-hact-ctms)
2. [The HACT ecosystem at a glance](#2-the-hact-ecosystem-at-a-glance)
3. [Getting started — access & login](#3-getting-started--access--login)
4. [Navigating the application](#4-navigating-the-application)
5. [User roles & permissions](#5-user-roles--permissions)
6. [The CTMS modules explained](#6-the-ctms-modules-explained)
7. [The external tools explained](#7-the-external-tools-explained)
8. [How the systems interact (data-flow map)](#8-how-the-systems-interact-data-flow-map)
9. [End-to-end workflow: creating & running a new study](#9-end-to-end-workflow-creating--running-a-new-study)
10. [Compliance & good practice](#10-compliance--good-practice)
11. [Troubleshooting & FAQ](#11-troubleshooting--faq)
12. [Glossary](#12-glossary)
13. [Quick reference](#13-quick-reference)

---

## 1. What is HACT CTMS?

**HACT CTMS** (Horn of Africa Clinical Trials — Clinical Trial Management System) is the central web platform for planning, running, monitoring, and closing out clinical studies. It is the **single pane of glass** that ties together the specialised systems a modern trial needs:

- **Study & site management** — define protocols, activate sites, and track milestones.
- **Subject management** — screen, enroll (with consent), and follow participants.
- **Electronic data capture (EDC)** — collect case-report-form (CRF) data at the bedside, even offline.
- **Laboratory results** — receive analysed lab results and auto-flag abnormal values.
- **Pharmacovigilance (safety)** — record adverse events and generate regulatory (CIOMS) reports.
- **Risk-based monitoring (RBM)** — score site risk and track expedited SAE reporting deadlines.
- **Data quality** — raise and resolve data queries.
- **Document management (eTMF)** — auto-provision the electronic Trial Master File.
- **Audit & compliance** — an append-only audit trail for every action.

CTMS does not replace the specialist systems — it **orchestrates** them. When you act in CTMS (e.g., enroll a subject), CTMS automatically pushes the right information to the right downstream tool (e.g., creates the subject in the EDC), and pulls results back (e.g., lab values from the LIMS).

---

## 2. The HACT ecosystem at a glance

HACT is composed of the **CTMS core** plus **five integrated external tools**, all behind a **single sign-on** provider.

| System | Role in the trial | Who mainly uses it |
|--------|-------------------|--------------------|
| **HACT CTMS** (this app) | Orchestration, study/subject/safety/monitoring, dashboards | All roles |
| **Keycloak** | Single Sign-On (SSO) identity provider — authentication & 2FA | Everyone (login); Admins (user management) |
| **OpenClinica** | Electronic Data Capture (EDC) — CRF definitions & clinical data | Data managers, site coordinators |
| **SENAITE** | Laboratory Information Management System (LIMS) — sample & result workflow | Lab managers, lab technicians |
| **Nextcloud** | eTMF — electronic Trial Master File document storage | Study admins, monitors, regulatory staff |
| **ERPNext** | Supply chain & finance — sites as customers, contracts, inventory | Operations managers, finance |

### Architecture (conceptual)

```
                       ┌──────────────────────────┐
                       │        Keycloak SSO       │  ← everyone authenticates here
                       └────────────┬─────────────┘
                                    │ (OIDC / PKCE)
                                    ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                          HACT CTMS core                          │
   │   Studies · Subjects · Safety · Monitoring · Lab · Queries ·     │
   │   Audit · Dashboard · Integrations   (+ Mobile EDC front-end)    │
   └───┬───────────────┬───────────────┬───────────────┬─────────────┘
       │ enroll →      │ create site → │ study/site →  │ sample ↔ result
       ▼               ▼               ▼               ▼
  ┌─────────┐    ┌─────────┐     ┌──────────┐    ┌──────────┐
  │OpenClin.│    │ ERPNext │     │ Nextcloud│    │ SENAITE  │
  │  (EDC)  │    │ (supply)│     │  (eTMF)  │    │  (LIMS)  │
  └─────────┘    └─────────┘     └──────────┘    └──────────┘
```

**Key idea:** you work primarily in CTMS. The arrows are automatic syncs performed by CTMS background tasks — you rarely log in to the external tools except for their specialist work (entering CRF data in OpenClinica, running lab analyses in SENAITE, filing documents in Nextcloud, managing supply in ERPNext).

---

## 3. Getting started — access & login

### 3.1 URLs

| System | URL |
|--------|-----|
| HACT CTMS (main app) | `https://ctms.hacts.org/` |
| Mobile EDC | `https://ctms.hacts.org/edc` |
| OpenClinica | `https://ctms.hacts.org/openclinica/` |
| SENAITE | `https://ctms.hacts.org/senaite/` |
| Nextcloud (eTMF) | `https://ctms.hacts.org/nextcloud/` |
| ERPNext | `https://ctms.hacts.org/erpnext/` |
| Keycloak Admin | `https://ctms.hacts.org/auth/admin/` |

> Credentials are environment-specific. For a deployed test environment, see the credentials table in `docs/Deployed_System_Test_Execution_Guide.md`. **Never** store real passwords in shared documents or the repository — use your organisation's password manager.

### 3.2 Signing in (SSO)

1. Open `https://ctms.hacts.org/`.
2. Click **"Sign in with Keycloak SSO"**.
3. Enter your username and password on the Keycloak page.
4. If two-factor authentication (2FA) is enabled for your account, enter the one-time code from your authenticator app.
5. You are redirected to the **Dashboard**. Your username appears at the top-right.

Because HACT uses **OpenID Connect with PKCE**, your CTMS session and the external tools share the same identity provider. Your **role(s)** (assigned in Keycloak) determine what you can see and do — see [Section 5](#5-user-roles--permissions).

### 3.3 Logging out

Use the account menu at the top-right → **Sign out**. This ends your CTMS session. For shared devices, also sign out of any external tool tabs you opened.

---

## 4. Navigating the application

The left **sidebar** is your main navigation. The items you see depend on your role(s):

| Sidebar item | Path | Purpose |
|--------------|------|---------|
| **Dashboard** | `/` | KPIs, data-quality score, system health |
| **Studies** | `/studies` | Create/manage studies, sites, milestones; export & lock |
| **Subjects** | `/subjects` | Screen, enroll, and follow participants |
| **Queries** | `/queries` | Data-clarification queries |
| **Safety** | `/safety` | Adverse events & CIOMS reports |
| **Laboratory** | `/lab` | Lab results, samples, SENAITE sync |
| **Monitoring** | `/monitoring` | RBM dashboard, site risk heatmap, SAE timelines |
| **Audit Trail** | `/audit` | Append-only record of every action |
| **Integrations** | `/integrations` | Health & status of external systems |
| **Mobile EDC** | `/edc` | Touch-friendly bedside CRF capture |

If you try to open a page your role can't access, CTMS shows an **Access Denied** message rather than an error.

---

## 5. User roles & permissions

HACT defines **9 roles**. A user may hold more than one; their effective access is the **union** of all their roles. A **superuser** (system administrator) bypasses all restrictions.

### 5.1 The roles

| Role | Purpose |
|------|---------|
| **Admin** (`admin`) | Full platform administration. |
| **Study Admin** (`study_admin`) | Manages studies end-to-end: create/edit studies & sites, lock database, export, view everything. |
| **Data Manager** (`data_manager`) | Owns data quality: subjects, queries, exports, EDC data entry. |
| **Site Coordinator** (`site_coordinator`) | Site-level enrollment, consent, EDC data entry, answering queries. |
| **Monitor** (`monitor`) | Risk-based monitoring; reviews subjects, queries, and site risk. |
| **Safety Officer** (`safety_officer`) | Pharmacovigilance: adverse events, CIOMS, SAE timelines. |
| **Lab Manager** (`lab_manager`) | Laboratory results, sample registration, SENAITE sync. |
| **Ops Manager** (`ops_manager`) | Operations & milestones (supply/finance-facing). |
| **Auditor** (`auditor`) | Read-only inspection of the audit trail. |

### 5.2 Page access by role

| Page | admin | study_admin | data_manager | site_coordinator | monitor | safety_officer | lab_manager | ops_manager | auditor |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Studies (read) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | – | ✅ |
| Subjects | ✅ | ✅ | ✅ | ✅ | ✅ | ✅* | – | – | – |
| Queries | ✅ | ✅ | ✅ | ✅ | ✅ | – | – | – | – |
| Safety | ✅ | ✅ | – | – | – | ✅ | – | – | – |
| Laboratory | ✅ | ✅ | – | – | – | – | ✅ | – | – |
| Monitoring | ✅ | ✅ | ✅ | – | ✅ | ✅ | – | – | – |
| Audit Trail | ✅ | ✅ | – | – | – | – | – | – | ✅ |
| Integrations | ✅ | ✅ | – | – | – | – | – | – | – |
| Mobile EDC | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

\* Safety officers can view a subject's detail (for AE context) but not the full subjects list workflow.

### 5.3 Key actions by role

| Action | Allowed roles |
|--------|---------------|
| Create / edit study, transition study state, create site | admin, study_admin |
| Create subject | admin, study_admin, data_manager |
| Enroll / withdraw subject | admin, study_admin, data_manager, site_coordinator |
| Create query | admin, study_admin, data_manager |
| Answer query | admin, study_admin, data_manager, site_coordinator |
| Close query | admin, study_admin, data_manager |
| Report adverse event, generate CIOMS | admin, study_admin, safety_officer |
| Import lab CSV, register sample, sync lab results | admin, study_admin, lab_manager |
| Export CSV / ODM, generate quality report | admin, study_admin, data_manager |
| Manage milestones | admin, study_admin, ops_manager |
| Enroll / submit CRF via Mobile EDC | admin, study_admin, data_manager, site_coordinator |
| Export audit trail | admin, study_admin, auditor |
| View integrations status | admin, study_admin |

> If a button you expect is missing, it is almost always **role-gated**. Ask an administrator to grant the appropriate role, or perform that step with an admin/study_admin account.

---

## 6. The CTMS modules explained

Each module below lists its **purpose**, **primary users**, and **what you can do**.

### 6.1 Dashboard (`/`)
- **Purpose:** At-a-glance health of your trials.
- **Users:** All roles.
- **What you see:** A **Data Quality Score** gauge (percentage of resolved queries with colour banding) and a **System Status** panel showing the health of PostgreSQL, Redis, Keycloak, OpenClinica, SENAITE, and ERPNext. The panel auto-refreshes periodically.

### 6.2 Studies (`/studies`)
- **Purpose:** The lifecycle home for each protocol.
- **Users:** Admin/Study Admin (manage); everyone else (read).
- **What you can do:**
  - **Create Study** (protocol number, name, phase, sponsor, OpenClinica Study OID, dates).
  - **Add Sites** to a study (site code, name, country, principal investigator).
  - **Milestones** tracking (Ops Manager).
  - **Export** study data as **CSV (ZIP)** or **CDISC ODM 1.3.2 XML**.
  - **Transition study state:** `Planning → Active → Locked` (database lock).
- **Study states:**
  | State | Meaning |
  |-------|---------|
  | **Planning** | Study created; setup in progress. |
  | **Active** | Enrollment & data capture allowed. |
  | **Locked** | Database frozen — no further edits/enrollment. |

### 6.3 Subjects (`/subjects`)
- **Purpose:** Manage trial participants through their status lifecycle.
- **Users:** Data Manager, Site Coordinator (+ Admin/Study Admin); Monitor (read).
- **Subject states:** `Screened → Enrolled → Completed` (or `Withdrawn`).
- **What you can do:**
  - **New Subject** (screen/register): study, site, subject identifier, screening number → status `Screened`.
  - **Enroll:** record **consent signed date** and enrollment date → status `Enrolled`. *Enrollment is blocked without a consent date* (a built-in GCP business rule).
  - **Withdraw** a subject.
  - **360° subject view:** visits, adverse events, and lab results for one participant.

### 6.4 Mobile EDC (`/edc`)
- **Purpose:** Bedside/point-of-care CRF data capture on a phone or tablet.
- **Users:** Site Coordinators & Data Managers primarily (accessible to all).
- **What you can do:**
  - Open a subject's **Visit Schedule** and tap **Fill CRF** for a visit (e.g., *48-hour Assessment*).
  - Complete the form with touch-friendly inputs; cross-field validations run live.
  - Provide an **e-signature** (PIN/password re-entry) before submitting.
  - **Offline mode:** if the network drops, the app shows *Offline Mode* and saves drafts locally; when connectivity returns it shows *Syncing…* and uploads queued forms.

### 6.5 Queries (`/queries`)
- **Purpose:** Formal data-clarification workflow.
- **Users:** Data Manager (create/close); Site Coordinator (answer); Monitor (read).
- **Query lifecycle:** `Open → Answered → Closed`. Every transition is audited. **Open queries block database lock.**

### 6.6 Safety (`/safety`)
- **Purpose:** Pharmacovigilance — record and report adverse events (AEs / SAEs).
- **Users:** Safety Officer (+ Admin/Study Admin).
- **What you can do:**
  - **Report AE:** subject, AE term, onset date, severity, SAE flag + criteria, causality, outcome, action taken, and narrative.
  - **Generate CIOMS:** produce a downloadable **CIOMS I** PDF for expedited regulatory reporting.

### 6.7 Laboratory (`/lab`)
- **Purpose:** Receive and review analysed lab results from the LIMS; register samples.
- **Users:** Lab Manager (+ Admin/Study Admin).
- **What you can do:**
  - View the **Results** tab — imported results with **H/L/N flags** (High / Low / Normal) against reference ranges, plus the **Source** SENAITE sample ID.
  - View the **Samples** tab — collected samples and their SENAITE IDs.
  - **Register Sample** — creates a `SampleCollection` in CTMS which is auto-pushed to SENAITE.
  - **Sync from SENAITE** — on-demand pull of published results (in addition to the automatic webhook + 15-minute background pull).
  - **Import CSV** — bulk-import results.
- See `docs/SENAITE_Lab_Integration_Guide.md` for the full lab workflow.

### 6.8 Monitoring (`/monitoring`)
- **Purpose:** Risk-based monitoring (RBM) and expedited-safety oversight.
- **Users:** Monitor, Safety Officer, Data Manager (+ Admin/Study Admin).
- **What you see:**
  - **RBM study overview** — 6 KPI cards (Total Sites, Enrollment Rate, Overdue SAEs, Open Queries, Protocol Deviations, Data Completeness), colour-coded.
  - **Site Risk Heatmap** — a 0–100 risk score per site; click a site to expand its weighted KPI breakdown (Open Queries 30%, Overdue SAEs 25%, Protocol Deviations 20%, Enrollment 15%, Data Timeliness 10%).
  - **SAE Expedited Reporting Timeline** — deadline countdowns colour-coded (green → yellow → red → black/overdue) with a **Mark Reported** action.

### 6.9 Audit Trail (`/audit`)
- **Purpose:** Tamper-evident, **append-only** record of every significant action.
- **Users:** Auditor (+ Admin/Study Admin).
- **What you can do:** Review entries chronologically (user + timestamp + action + object), filter by action type/model, and **export** the audit trail. Records **cannot be edited or deleted**.

### 6.10 Integrations (`/integrations`)
- **Purpose:** Operational visibility into the external systems.
- **Users:** Admin/Study Admin.
- **What you see:** Connection health and status for OpenClinica, SENAITE, ERPNext, and Nextcloud, useful for diagnosing sync issues.

---

## 7. The external tools explained

### 7.1 Keycloak — Single Sign-On (SSO)
- **What it is:** The identity provider that authenticates every user and issues the tokens CTMS uses.
- **When/why:** Every login goes through Keycloak. **User accounts, passwords, 2FA, and role assignments** are managed here.
- **Who uses it directly:** Administrators (to create users and assign the 9 HACT roles). Regular users only interact with the login page.
- **Interaction with CTMS:** CTMS reads your roles from the SSO token to enforce the permissions in [Section 5](#5-user-roles--permissions).

### 7.2 OpenClinica — Electronic Data Capture (EDC)
- **What it is:** A regulatory-grade EDC where **CRF definitions** live and clinical data is captured/validated.
- **When/why:** Detailed CRF data entry and validation (screening, treatment follow-up, etc.), and CDISC ODM data extraction.
- **Who uses it directly:** Data Managers and Site Coordinators.
- **Interaction with CTMS:** When you **enroll** a subject in CTMS, CTMS **automatically creates that subject** in OpenClinica (matched by the study's **Unique Protocol ID**). Visits scheduled in CTMS create the corresponding events in OpenClinica.
- **Prerequisite:** The OpenClinica study, events, and CRFs must be set up once per protocol (see Appendix A of the test-execution guide and `docs/OpenClinica_CRF_Data_Entry_User_Guide.md`).

### 7.3 SENAITE — Laboratory Information Management System (LIMS)
- **What it is:** The lab system that manages samples through **Receive → Analyse → Submit → Verify → Publish**.
- **When/why:** Whenever biological samples are analysed and results must flow back into the trial record.
- **Who uses it directly:** Lab Managers and lab technicians.
- **Interaction with CTMS:**
  - **CTMS → SENAITE:** Registering a sample in CTMS auto-creates the corresponding AnalysisRequest in SENAITE (with a lab Contact so reports can be published).
  - **SENAITE → CTMS:** When results are **Published**, they flow back to CTMS (instantly via the results-published **webhook**, plus a **15-minute** scheduled pull and an on-demand **Sync** button). CTMS maps them to the subject, dedupes by analysis UID, and flags values **H/L/N** against reference ranges.
- See `docs/SENAITE_Lab_Integration_Guide.md`.

### 7.4 Nextcloud — eTMF (electronic Trial Master File)
- **What it is:** Secure document storage with version history.
- **When/why:** All regulatory/site/monitoring documents for a study live here in a standard folder structure.
- **Who uses it directly:** Study Admins, Monitors, regulatory staff.
- **Interaction with CTMS:** When you **create a study**, CTMS auto-provisions the eTMF folder tree; when you **add a site**, CTMS creates that site's document subfolder:
  ```
  eTMF/<PROTOCOL>/
    01_Protocol/  02_IRB_Ethics/  03_Regulatory/
    04_Site_Documents/ <SITE_CODE>/ …
    05_Data_Management/ 06_Safety/ 07_Monitoring/ 08_Central_Lab/
  ```

### 7.5 ERPNext — Supply Chain & Finance
- **What it is:** An ERP for procurement, inventory, and finance.
- **When/why:** Sites are represented as **Customers**; contracts and supply/finance are managed here.
- **Who uses it directly:** Operations Managers and finance staff.
- **Interaction with CTMS:** When you **add a site** in CTMS, a corresponding **Customer** record is created in ERPNext. A contract-signed webhook can activate the site back in CTMS.

---

## 8. How the systems interact (data-flow map)

The power of HACT is automatic cross-system synchronisation. The table shows what happens downstream when you perform each CTMS action.

| You do this in CTMS | CTMS automatically… | Verify in… |
|---------------------|---------------------|------------|
| **Create a study** | Provisions the **eTMF** folder tree | Nextcloud |
| **Add a site** | Creates a **Customer** in ERPNext + site subfolder in eTMF | ERPNext, Nextcloud |
| **Enroll a subject** | Creates the **subject** in OpenClinica (EDC) | OpenClinica → Subject Matrix |
| **Schedule a visit** | Creates the **event** in OpenClinica | OpenClinica |
| **Register a lab sample** | Creates the **AnalysisRequest** in SENAITE | SENAITE |
| **(Lab) Publish results in SENAITE** | Pulls results into CTMS, maps to subject, flags H/L/N | CTMS → Laboratory |
| **Any significant action** | Writes an **append-only audit** entry | CTMS → Audit Trail |

> Syncs run as background tasks and are usually a few seconds behind. Lab results also have a 15-minute scheduled fallback. If something doesn't appear, refresh and allow a moment before treating it as an issue; the **Integrations** page shows connection health.

---

## 9. End-to-end workflow: creating & running a new study

This is the **sequential, start-to-finish** procedure to stand up a new study and run it through to database lock. Each step notes **who** performs it and any **cross-system effect**. (For an exact click-by-click script with a worked example protocol, use `docs/Deployed_System_Test_Execution_Guide.md`.)

### Phase 0 — Prerequisites (one-time, per environment)
- **Admin (Keycloak):** create user accounts and assign the appropriate HACT role(s).
- **Data Manager / Admin (OpenClinica):** set up the OpenClinica study, events, and CRFs for the protocol (matched by the Study OID you'll enter in CTMS). See the OpenClinica setup appendix.
- **Lab Manager (SENAITE):** one-time lab setup — Client, Sample Types, Analysis Categories/Services, and a lab **Contact with an email** (required so result reports can be published).

---

### Phase 1 — Create the study *(Study Admin / Admin)*

**Step 1 — Create the Study**
- Go to **Studies → Create Study**.
- Fill: **Protocol Number**, **Study Name**, **Phase**, **Sponsor**, **OpenClinica Study OID**, **Start/End dates**.
- Click **Create**. The study appears with status **Planning**.
- **Cross-system:** the **eTMF** folder tree is auto-created in Nextcloud; an audit entry `CREATE Study` is written.

**Step 2 — Add clinical sites**
- Open the study → **New Site**. Add each site (**Site Code**, **Name**, **Country**, **Principal Investigator**).
- **Cross-system:** each site becomes a **Customer** in ERPNext and gets a subfolder under `04_Site_Documents/` in the eTMF.

**Step 3 — Verify the eTMF (optional but recommended)**
- In Nextcloud, open `eTMF/<PROTOCOL>/` and confirm the folder tree and site subfolders exist. Upload the approved protocol PDF into `01_Protocol/`.

**Step 4 — Activate the study**
- When setup is complete, transition the study **Planning → Active** (Studies → study header). Enrollment and data capture are now allowed.

---

### Phase 2 — Enroll & capture data *(Site Coordinator / Data Manager)*

**Step 5 — Screen/register a subject**
- **Subjects → New Subject**: choose the study & site, enter a **Subject Identifier** and **Screening Number** → status **Screened**.

**Step 6 — Enroll with consent**
- Open the subject → **Enroll**: enter **Consent Signed Date** and **Enrollment Date** → status **Enrolled**.
- **Business rule:** enrollment is **rejected without a consent date**.
- **Cross-system:** the subject is auto-created in **OpenClinica**; audit records `UPDATE Subject screened → enrolled`.

**Step 7 — Capture CRF data (Mobile EDC)**
- In **Mobile EDC**, open the subject's **Visit Schedule** → **Fill CRF** for the due visit → complete fields → **e-sign** → **Submit**.
- Offline is supported (drafts sync when back online).

**Step 8/9 — Detailed CRF entry & validation (OpenClinica)**
- Data Managers complete/validate detailed CRFs in OpenClinica (screening, treatment follow-up), scheduling events and marking forms complete.

---

### Phase 3 — Labs & safety *(Lab Manager / Safety Officer)*

**Step 10 — Lab results**
- **Option A (CTMS-first):** in **Laboratory → Register Sample**, register a sample for the subject; CTMS pushes it to SENAITE. The lab then processes it.
- **Option B (SENAITE-first):** the lab creates the sample directly in SENAITE.
- Either way, the lab runs the workflow **Receive → enter results → Submit → Verify → Publish**. On **Publish**, results flow back to CTMS automatically and appear on the **Laboratory** page, flagged **H/L/N**.

**Step 11 — Report an SAE + CIOMS**
- **Safety → Report AE**: complete the AE/SAE form and submit. On the SAE row, click **CIOMS** to download the regulatory PDF.

**Step 12 — Expedited SAE timeline**
- **Monitoring → SAE Expedited Reporting Timeline**: review the deadline countdown; when filed with the authority, click **Mark Reported** (status → *On Time*).

---

### Phase 4 — Monitoring *(Monitor)*

**Step 13 — RBM overview & site heatmap**
- **Monitoring**: select the study; review the 6 KPI cards and the **Site Risk Heatmap**; click a site to expand its weighted risk breakdown.

---

### Phase 5 — Data quality, export & lock *(Data Manager → Study Admin)*

**Step 14 — Query lifecycle**
- **Queries** (or from a subject's completed form): **create** a query → site **answers** → data manager **closes** it (`Open → Answered → Closed`). All open queries must be closed before lock.

**Step 15 — Export**
- Studies → study: **CSV** (ZIP) and **ODM XML** (CDISC ODM 1.3.2) downloads. Optionally extract a dataset from OpenClinica as well.

**Step 16 — Database lock** *(Admin / Study Admin)*
- Ensure **all queries are Closed**. In the study header, click **Move to locked** and confirm.
- If any query is still open, the lock is **rejected**. Once locked, a **"Study Locked — All data is frozen"** banner appears and further edits/enrollment are blocked.

**Step 17 — Audit review & sign-off**
- **Audit Trail**: confirm the expected entries exist (study/site/subject creation, enrollment, form submissions, AE/CIOMS, query transitions, study lock), each with user + timestamp. Records are append-only.

---

### Workflow summary (who does what)

| Phase | Lead role | CTMS module | Downstream effect |
|-------|-----------|-------------|-------------------|
| Create study | Study Admin | Studies | eTMF folders (Nextcloud) |
| Add sites | Study Admin | Studies | Customers (ERPNext) + site folders |
| Activate | Study Admin | Studies | — |
| Screen/enroll | Site Coordinator / Data Manager | Subjects | Subject in OpenClinica |
| CRF capture | Site Coordinator | Mobile EDC / OpenClinica | Clinical data in EDC |
| Labs | Lab Manager | Laboratory | Samples/results ↔ SENAITE |
| Safety | Safety Officer | Safety / Monitoring | CIOMS PDF |
| Monitoring | Monitor | Monitoring | Risk scores |
| Queries | Data Manager / Site Coordinator | Queries | — |
| Export & lock | Study Admin | Studies | ODM/CSV; frozen DB |
| Audit | Auditor | Audit Trail | — |

---

## 10. Compliance & good practice

- **GCP consent gate:** subjects cannot be enrolled without a recorded consent date.
- **E-signatures:** CRF submission in the Mobile EDC requires signature re-authentication (21 CFR Part 11-style).
- **Append-only audit:** every significant action is logged with user + timestamp and cannot be altered or deleted.
- **Database lock integrity:** a study cannot be locked while data queries remain open, preventing premature freezing of unresolved data.
- **Least privilege:** use the narrowest role that lets a person do their job; hold admin rights to as few people as possible.
- **Secrets hygiene:** keep passwords and integration secrets (e.g., the SENAITE webhook secret) in a password manager, never in shared docs or the repo.

---

## 11. Troubleshooting & FAQ

| Symptom | Likely cause / fix |
|---------|--------------------|
| A button (e.g., *Create Study*, *Move to locked*, *Report AE*) is missing | The action is **role-gated**. Use an account with the right role (see §5.3) or ask an admin to assign it. |
| Access Denied on a page | Your role can't access that module (§5.2). |
| Enrolled subject not in OpenClinica | Confirm the study's **OpenClinica Study OID** matches an existing OpenClinica study and the one-time OC setup is done; allow a few seconds for the sync. |
| Lab results don't appear on the Lab page | Confirm the sample was **Published** in SENAITE (not just Verified). Results arrive via webhook or the 15-min pull — try **Sync from SENAITE**. The subject's identifier must match a CTMS subject. |
| SENAITE publish fails with an `EmailAddress` error | The sample's **Contact** has no email. Ensure the client's lab Contact has an email address. |
| eTMF folders missing after creating a study | The folder task runs in the background; refresh Nextcloud after a few seconds. |
| SENAITE root URL "redirects" | `.../senaite/` → `/senaite/login` for unauthenticated users is **normal**, not an error. |
| Study won't lock | Some data **queries are still Open** — close them first. |

---

## 12. Glossary

| Term | Meaning |
|------|---------|
| **CTMS** | Clinical Trial Management System — the HACT core app. |
| **EDC** | Electronic Data Capture (OpenClinica). |
| **LIMS** | Laboratory Information Management System (SENAITE). |
| **eTMF** | Electronic Trial Master File — the study's document repository (Nextcloud). |
| **CRF** | Case Report Form — the structured form for capturing clinical data. |
| **AE / SAE** | Adverse Event / Serious Adverse Event. |
| **CIOMS** | Standard international form for expedited safety reporting. |
| **RBM** | Risk-Based Monitoring. |
| **ODM** | CDISC Operational Data Model — a standard clinical-data XML format. |
| **SSO / OIDC / PKCE** | Single Sign-On via OpenID Connect with the PKCE flow (Keycloak). |
| **Study OID** | The OpenClinica study identifier CTMS uses to match the EDC study. |
| **H/L/N flag** | Lab result flagged High / Low / Normal vs. its reference range. |

---

## 13. Quick reference

### System URLs
| System | URL |
|--------|-----|
| CTMS | `https://ctms.hacts.org/` |
| Mobile EDC | `https://ctms.hacts.org/edc` |
| OpenClinica | `https://ctms.hacts.org/openclinica/` |
| SENAITE | `https://ctms.hacts.org/senaite/` |
| Nextcloud | `https://ctms.hacts.org/nextcloud/` |
| ERPNext | `https://ctms.hacts.org/erpnext/` |
| Keycloak Admin | `https://ctms.hacts.org/auth/admin/` |

### The 9 roles (cheat sheet)
`admin` · `study_admin` · `data_manager` · `site_coordinator` · `monitor` · `safety_officer` · `lab_manager` · `ops_manager` · `auditor`

### The golden path
**Create study → Add sites → Activate → Screen → Enroll (consent) → Capture CRFs (EDC) → Labs (SENAITE) → Safety (AE/CIOMS) → Monitor (RBM) → Resolve queries → Export → Lock → Audit review.**

---

*This guide describes the HACT CTMS platform and its integrations at a functional level. Screens and controls may vary slightly by deployment/build. For exact, environment-specific credentials and a validation checklist, see `docs/Deployed_System_Test_Execution_Guide.md`.*
