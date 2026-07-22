# HACT CTMS — Deployed System Manual Test-Execution Guide

## Browser-Only, Normal-User Walkthrough of https://ctms.hacts.org/

**Environment:** Production (Google Cloud) — https://ctms.hacts.org/
**Protocol used for testing:** HACT-PSBI-ETH-2026 (RCT 2 PSBI Neonatal Treatment) — this is one example study used to exercise the platform
**Based on:** `docs/Stakeholder_Demo_Guide.md` (20-step lifecycle), rewritten for a normal user clicking through a real browser
**Scope:** HACT CTMS React frontend, Mobile EDC, and the external tools (SENAITE, Nextcloud, ERPNext, OpenClinica) — no `docker exec` or backend-shell shortcuts

| Field | Value |
|-------|-------|
| Tester name | __________________________ |
| Date / time | __________________________ |
| Browser + version | __________________________ |
| Device (desktop / tablet) | __________________________ |

---

## How to Use This Guide

Work through the steps in order. For each step:

1. Perform the **Action** (exact click path).
2. Compare what you see against the **Expected result**.
3. Where a step lists **Cross-system verification**, switch to that tool's tab and confirm the automatic sync happened.
4. Record the outcome in the **Result** line.

**Result legend (tick one per step):**

- `[ ] Pass` — behaved exactly as expected
- `[ ] Fail` — did not behave as expected (write what happened in Notes)
- `[ ] Blocked` — could not perform the step (e.g., button missing, prior step failed)

> Tip: Open all system tabs in advance (main app + the 4 external tools) so you can switch between them quickly when verifying cross-system sync.

---

## Access & Credentials

### Main Application

| System | URL | Username | Password |
|--------|-----|----------|----------|
| HACT CTMS | https://ctms.hacts.org/ | `hact-user` | `hact-user` |
| HACT CTMS (admin) | https://ctms.hacts.org/ | `hact-admin` | `hact-admin` |
| HACT CTMS (superuser) | https://ctms.hacts.org/ | `admin` | `Admin@2026!` |
| Mobile EDC | https://ctms.hacts.org/edc | `hact-user` | `hact-user` |

> This walkthrough uses `hact-user` / `hact-user` by default (full access). Use an admin account only where a step notes it is required.

### Integrated External Systems

| System | URL | Username | Password | Purpose |
|--------|-----|----------|----------|---------|
| SENAITE LIMS | https://ctms.hacts.org/senaite/ | `admin` | `admin` | Laboratory information |
| Nextcloud eTMF | https://ctms.hacts.org/nextcloud/ | `admin` | `Admin@2026!` | Document management |
| ERPNext | https://ctms.hacts.org/erpnext/ | `Administrator` | `Admin@2026!` | Supply & finance |
| OpenClinica | https://ctms.hacts.org/openclinica/ | `root` | `Admin@2026!` | Electronic data capture |

### Administrative / Infrastructure

| Panel | URL | Username | Password | Purpose |
|-------|-----|----------|----------|---------|
| Keycloak Admin Console | https://ctms.hacts.org/auth/admin/ | `admin` | `<KEYCLOAK_ADMIN_PASSWORD>` | SSO realm & user administration |

> The Keycloak admin password is intentionally shown as a placeholder here. Keep the real value in your own private notes / password manager — do not commit it to the repository. The main test flow does not require the Keycloak admin console; it is only listed for completeness.

---

## Pre-Test Verification (2 minutes)

Open each URL and confirm it loads before starting the walkthrough.

| # | Check | URL | Expected | Result |
|---|-------|-----|----------|--------|
| P1 | Main app loads | https://ctms.hacts.org/ | Login screen with **"Sign in with Keycloak SSO"** button | `[ ] Pass  [ ] Fail` |
| P2 | Backend healthy | https://ctms.hacts.org/api/health/ | JSON `{"status": "healthy"}` | `[ ] Pass  [ ] Fail` |
| P3 | Mobile EDC loads | https://ctms.hacts.org/edc | Login / mobile subject list | `[ ] Pass  [ ] Fail` |
| P4 | SENAITE loads | https://ctms.hacts.org/senaite/ | Redirects to `/senaite/login`; SENAITE LIMS login page renders | `[ ] Pass  [ ] Fail` |
| P5 | Nextcloud loads | https://ctms.hacts.org/nextcloud/ | Nextcloud login page | `[ ] Pass  [ ] Fail` |
| P6 | ERPNext loads | https://ctms.hacts.org/erpnext/ | ERPNext login / home page | `[ ] Pass  [ ] Fail` |
| P7 | OpenClinica loads | https://ctms.hacts.org/openclinica/ | OpenClinica login page | `[ ] Pass  [ ] Fail` |

> **Note on SENAITE:** Visiting `https://ctms.hacts.org/senaite/` in a browser correctly redirects you to the login page (`/senaite/login`). This is expected behavior for an unauthenticated visitor — it is not an error.

---

## Test Execution — 20 Steps

---

### Act 1: Authentication & Study Setup (Steps 1–4)

---

#### Step 1 — SSO Login with Keycloak (PKCE)

- **System / URL:** HACT CTMS — https://ctms.hacts.org/
- **Action:**
  1. Click **"Sign in with Keycloak SSO"**.
  2. On the Keycloak login page, enter `hact-user` / `hact-user`.
  3. (If 2FA is enabled) enter the OTP from your authenticator app.
  4. Wait for the redirect back to the app.
- **Expected result:** You are redirected to the HACT CTMS Dashboard. Top-right shows the logged-in username. The sidebar shows navigation items (Dashboard, Studies, Subjects, Safety, Monitoring, Lab, Queries, Audit, Integrations). No error toast.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 2 — Create the Study

- **System / URL:** HACT CTMS — Studies → **Create Study**
- **Action:** Fill and submit:

  | Field | Value |
  |-------|-------|
  | Protocol Number | `HACT-PSBI-ETH-2026` |
  | Study Name | `RCT 2 — PSBI Neonatal Treatment (Moderate Mortality Risk)` |
  | Phase | `Phase III` |
  | Sponsor | `Horn of Africa Clinical Trials (HACT)` |
  | OpenClinica Study OID | `S_PSBI2026` |
  | Start Date | `2026-06-01` |
  | End Date | `2028-06-30` |

  Then click **Create**.
- **Expected result:** The study appears in the Studies list with status `Planning`.
- **Cross-system verification:**
  - **Nextcloud** (https://ctms.hacts.org/nextcloud/ → Files): an `eTMF/HACT-PSBI-ETH-2026/` folder structure appears (`01_Protocol/` … `08_Central_Lab/`). It may take a few seconds (created by a background task). Refresh if needed.
  - **Audit** (CTMS → Audit page): a `CREATE Study` entry is recorded for your user.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

> If the study protocol already exists from a prior test, either reuse it or use a slightly different Protocol Number (e.g., append your initials) to avoid a duplicate-key error.

---

#### Step 3 — Add Clinical Sites

- **System / URL:** HACT CTMS — click into `HACT-PSBI-ETH-2026` → **New Site**
- **Action:** Create two sites:

  **Site 1**
  | Field | Value |
  |-------|-------|
  | Site Code | `ETH-ADM-001` |
  | Name | `Adama General Hospital` |
  | Country | `Ethiopia` |
  | Principal Investigator | `Dr. Fikadu Beyene` |

  **Site 2**
  | Field | Value |
  |-------|-------|
  | Site Code | `ETH-JIM-002` |
  | Name | `Jimma University Medical Center` |
  | Country | `Ethiopia` |
  | Principal Investigator | `Dr. Meron Tadesse` |

- **Expected result:** Both sites appear under the study.
- **Cross-system verification:**
  - **ERPNext** (https://ctms.hacts.org/erpnext/ → search `ETH-ADM-001` or Customer list): each site appears as a Customer record.
  - **Nextcloud** (`eTMF/HACT-PSBI-ETH-2026/04_Site_Documents/`): subfolders `ETH-ADM-001/` and `ETH-JIM-002/` appear.
  - **Audit:** two `CREATE Site` entries recorded.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 4 — Verify Automated eTMF in Nextcloud

- **System / URL:** Nextcloud — https://ctms.hacts.org/nextcloud/ (login `admin` / `Admin@2026!`)
- **Action:** Go to **Files** → open `eTMF/HACT-PSBI-ETH-2026/`.
- **Expected result:** The folder tree exists and includes the site subfolders under `04_Site_Documents/`:
  ```
  eTMF/HACT-PSBI-ETH-2026/
    01_Protocol/  02_IRB_Ethics/  03_Regulatory/
    04_Site_Documents/ ETH-ADM-001/  ETH-JIM-002/
    05_Data_Management/ 06_Safety/ 07_Monitoring/ 08_Central_Lab/
  ```
  (Optional) upload any test PDF into `01_Protocol/` to confirm write access + version history.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

### Act 2: Screening, Enrollment & Bedside Data Capture (Steps 5–9)

---

#### Step 5 — Screen & Register a Subject

- **System / URL:** HACT CTMS — Subjects → **New Subject**
- **Action:** Fill and create:

  | Field | Value |
  |-------|-------|
  | Study | `HACT-PSBI-ETH-2026` |
  | Site | `ETH-ADM-001 — Adama General Hospital` |
  | Subject Identifier | `ETH-ADM-001-0001` |
  | Screening Number | `SCR-0001` |

- **Expected result:** Subject appears with status `screened` (not yet enrolled).
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 6 — Enroll the Subject with Consent

- **System / URL:** HACT CTMS — click the subject `ETH-ADM-001-0001` → **Enroll**
- **Action:** Fill and confirm:

  | Field | Value |
  |-------|-------|
  | Consent Signed Date | `2026-06-15` |
  | Enrollment Date | `2026-06-15` |

  Click **Enroll**.
- **Expected result:** Status changes to `enrolled`; consent date recorded.
- **Business-rule check:** Try clicking Enroll with the Consent Signed Date left blank first — the system should **reject** enrollment without a consent date. (Then fill it and proceed.)
- **Cross-system verification:**
  - **OpenClinica** (https://ctms.hacts.org/openclinica/ → Subject Matrix): subject `ETH-ADM-001-0001` appears (synced automatically). May take a few seconds.
  - **Audit:** `UPDATE Subject — screened → enrolled`.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 7 — Bedside Data Capture via Mobile EDC

- **System / URL:** Mobile EDC — https://ctms.hacts.org/edc (use a tablet/phone, or resize the browser to ~400px wide)
- **Action:**
  1. Log in with `hact-user` / `hact-user`.
  2. In the **Subject List**, tap `ETH-ADM-001-0001` → the Visit Schedule opens.
  3. Tap **"Fill CRF"** on the **48-hour Assessment** visit.
  4. Complete the CRF:

     | Field | Value |
     |-------|-------|
     | Assessment Date | `2026-06-17` |
     | Place of Assessment | `Hospital` |
     | Difficulty Feeding | `No difficulty` |
     | Severe Chest Indrawing | `No` |
     | Axillary Temperature (°C) | `37.2` |
     | Critical Illness Signs | `No` |

  5. Provide the **e-signature** (PIN / password re-entry) when prompted.
  6. Tap **Submit**.
- **Expected result:** CRF loads with touch-friendly inputs; submits successfully; status shows **Submitted**; the visit shows complete on the schedule.
- **Optional offline check:** Enable airplane mode → status bar shows **Offline Mode** → fill another CRF (saves locally) → re-enable network → app shows **Syncing…** then confirms sync.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 8 — Verify Subject Sync in OpenClinica

- **System / URL:** OpenClinica — https://ctms.hacts.org/openclinica/ (login `root` / `Admin@2026!`)
- **Action:** Go to **Subject Matrix** (View Subjects).
- **Expected result:** Subject `ETH-ADM-001-0001` is present (created automatically from the CTMS enrollment — no manual entry).
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

> If the subject is not present, confirm the study's OpenClinica Study OID (`S_PSBI2026`) matches an existing OpenClinica study and that the one-time OpenClinica setup (Appendix A) was done.

---

#### Step 9 — Screening CRF Data Entry in OpenClinica

- **System / URL:** OpenClinica — https://ctms.hacts.org/openclinica/
- **Action:**
  1. Subject Matrix → click `ETH-ADM-001-0001`.
  2. Schedule the **Screening & Enrollment** event for `2026-06-15`.
  3. Open `A1_SCREEN_ENROLL v1.0` and enter:

     | Item | Value |
     |------|-------|
     | `SUBJID` | `ETH-ADM-001-0001` |
     | `SCRDTC` | `2026-06-15` |
     | `SCRCONS` | `1` (Yes) |
     | `BRTHDTC` | `2026-06-10` |
     | `SEX` | `F` |
     | `WEIGHT` | `2850` |
     | `INCLMET` | `1` (Yes) |
     | `EXCLMET` | `2` (No) |
     | `TRTARM` | `Oral Amoxicillin` |

  4. **Mark as Complete**.
- **Expected result:** CRF accepts the data, field validations work (numeric/date/required), and the CRF is marked complete.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

### Act 3: Lab Results & Safety (Steps 10–13)

---

#### Step 10 — Lab Results from SENAITE (via the SENAITE UI)

> This is the normal-user path: enter and publish results in SENAITE, then confirm they appear in the CTMS Lab page. (No shell shortcuts.)

- **System / URL:** SENAITE — https://ctms.hacts.org/senaite/ (login `admin` / `admin`)
- **Action:**
  1. Click **Add Sample** (or **Samples → Add**).
  2. Enter sample details:

     | Field | Value |
     |-------|-------|
     | Client / Patient | `ETH-ADM-001-0001` |
     | Sample Type | `Blood` |
     | Date Sampled | `2026-06-15` |

  3. Add analyses: **CRP**, **Hemoglobin**, **WBC**, **Platelets**.
  4. Enter results and **Publish**:

     | Test | Value | Unit | Expected flag |
     |------|-------|------|---------------|
     | C-Reactive Protein (CRP) | `12.5` | mg/L | HIGH (ref 0–5) |
     | Hemoglobin | `14.8` | g/dL | Normal |
     | WBC Count | `18.2` | 10^3/uL | Normal (neonatal) |
     | Platelet Count | `280` | 10^3/uL | Normal |

- **Expected result:** SENAITE marks the results **Published**.
- **Cross-system verification:** Switch to **HACT CTMS → Lab** page. The results appear automatically (via webhook / scheduled pull) with CRP flagged **HIGH** in red. Then click the Subject ID to see the 360° subject view (visits, AEs, labs).
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

> Timing note: the CTMS pulls SENAITE results on a schedule (approximately every 15 minutes) in addition to the webhook. If results do not appear immediately on the Lab page, wait and refresh. If they never appear, record this as a finding (SENAITE→CTMS lab integration).

---

#### Step 11 — Report a Serious Adverse Event + CIOMS PDF

- **System / URL:** HACT CTMS — Safety → **Report AE**
- **Action:** Fill and submit:

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

  Then, on the SAE row, click the **CIOMS** button.
- **Expected result:** SAE appears in the Safety table with no submit error. Clicking **CIOMS** generates and downloads a CIOMS I PDF containing the subject ID, AE term, onset date, causality, and narrative.
- **Cross-system verification:** **Audit** page records `CREATE AdverseEvent`.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 12 — SAE Expedited Reporting Timeline

- **System / URL:** HACT CTMS — Monitoring → **SAE Expedited Reporting Timeline**
- **Action:** Locate the SAE from Step 11; review the deadline and countdown; then click **Mark Reported** and confirm submission to the authority (EFDA).
- **Expected result:** The SAE shows a **15-day** deadline (hospitalization criterion) with a color-coded countdown (green >50% remaining, yellow 10–50%, red <10%, black overdue). After **Mark Reported**, status changes from `Pending` to `On Time` and a reported timestamp is recorded.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 13 — Treatment Follow-up in OpenClinica

- **System / URL:** OpenClinica — https://ctms.hacts.org/openclinica/
- **Action:**
  1. Subject Matrix → `ETH-ADM-001-0001`.
  2. Schedule **Day 2 Treatment Follow-up** for `2026-06-17`.
  3. Open `B2_RCT2_TREATMENT v1.0` and enter:

     | Item | Value |
     |------|-------|
     | `DAYNUM` | `D2` |
     | `ASSESSLOC` | `Hospital` |
     | `RESPONDENT` | `Mother` |
     | `OTHABX` | *(empty)* |
     | `REMTAB` | `8` |

  4. **Mark as Complete**. (Optionally repeat for Day 4 and Day 8.)
- **Expected result:** CRF accepts and completes with validation working.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

### Act 4: Risk-Based Monitoring (Steps 14–15)

---

#### Step 14 — RBM Dashboard: Study Risk Overview

- **System / URL:** HACT CTMS — Monitoring
- **Action:** Select the `HACT-PSBI-ETH-2026` study from the study selector; review the 6 KPI cards.
- **Expected result:** Six KPI cards render with color coding, e.g.:

  | KPI | Expected |
  |-----|----------|
  | Total Sites | 2 |
  | Enrollment Rate | 1+ subject |
  | Overdue SAEs | 0 (green) |
  | Open Queries | 0–1 |
  | Protocol Deviations | 0 (green) |
  | Data Completeness | a percentage |

- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 15 — Site Risk Heatmap (Click to Expand)

- **System / URL:** HACT CTMS — Monitoring → **Site Risk Heatmap**
- **Action:** Review the per-site risk scores; click a site row (e.g., `ETH-ADM-001`) to expand its KPI breakdown.
- **Expected result:** Both sites appear with a 0–100 risk score and level (green/yellow/red). Clicking a row expands the weighted KPI detail (Open Queries 30%, Overdue SAEs 25%, Protocol Deviations 20%, Enrollment 15%, Data Timeliness 10%).
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

### Act 5: Data Quality, Export & Lock (Steps 16–20)

---

#### Step 16 — Raise & Resolve a Data Query (via the UI)

> Normal-user path (no shell). Query creation location can vary by build — try the Queries page first, then the subject/form-instance view.

- **System / URL:** HACT CTMS — Queries (and/or Subjects → subject → form instance)
- **Action:**
  1. Open the **Queries** page. If a **New Query** control is available, raise a query with text: `Weight 2850g — please confirm this was measured on a calibrated scale per SOP.` (If there is no create control on the Queries page, open the subject `ETH-ADM-001-0001` → a completed form instance → raise the query from the item/response there.)
  2. On the open query, click **Answer** and enter: `Confirmed — Seca 354 scale, calibrated 2026-06-01, certificate on file.`
  3. Click **Close**.
- **Expected result:** The query moves through `Open → Answered → Closed`; each transition is recorded in the Audit trail.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes (record where query creation is available in the UI):** ______________________________________________

---

#### Step 17 — Data Export (CDISC ODM / CSV)

- **System / URL:** HACT CTMS — Studies → `HACT-PSBI-ETH-2026`
- **Action:**
  1. Click **CSV** → confirm a ZIP of study data downloads.
  2. Click **ODM XML** → confirm a CDISC ODM 1.3.2 XML downloads.
  3. (Optional) In OpenClinica: **Tasks → Extract Data → Create Dataset** → ODM XML 1.3 → generate and download.
- **Expected result:** Both downloads succeed and open as valid files (ZIP contains data files; XML is well-formed CDISC ODM).
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 18 — Database Lock

- **System / URL:** HACT CTMS — Studies → `HACT-PSBI-ETH-2026` (requires admin / study_admin)
- **Action:**
  1. Confirm all queries are **Closed** (Step 16).
  2. Click **"Move to locked"** in the Study Detail header and confirm.
  3. (Optional) In OpenClinica: **Tasks → Lock Study**.
- **Expected result:** If any query is still open, the lock is **rejected** with a message. Once all queries are closed, the study locks and a **"Study Locked — All data is frozen"** banner appears; further edits/enrollment are blocked.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

> If your logged-in role cannot see the lock control, log in with an admin account (`hact-admin` / `hact-admin` or `admin` / `Admin@2026!`) for this step.

---

#### Step 19 — Audit Trail Review

- **System / URL:** HACT CTMS — Audit
- **Action:** Review the chronological audit entries generated by this test; try filtering by action type / model. Confirm there are no edit/delete controls (append-only).
- **Expected result:** Entries exist for the actions you performed (CREATE Study, CREATE Site x2, CREATE Subject, UPDATE Subject enrolled, FormInstance submit, AdverseEvent, CIOMS, Query open/close, Study locked), each with user + timestamp. Records cannot be edited or deleted.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

#### Step 20 — Dashboard Summary & System Health

- **System / URL:** HACT CTMS — Dashboard (home)
- **Action:** Review the Data Quality Score gauge and the System Status panel; wait ~60s to confirm it auto-refreshes.
- **Expected result:** Data Quality Score renders (percentage of resolved queries with color banding). System Status shows the integrated services (PostgreSQL, Redis, Keycloak, OpenClinica, SENAITE, ERPNext) with health indicators, refreshing periodically.
- **Result:** `[ ] Pass  [ ] Fail  [ ] Blocked`
- **Notes:** ______________________________________________

---

## Known Notes / Gotchas

| Topic | What to expect |
|-------|----------------|
| SENAITE root URL | `https://ctms.hacts.org/senaite/` redirects (302) to `/senaite/login` for unauthenticated users — this is normal, not a 500/error. |
| SENAITE assets over HTTPS | SENAITE may generate some asset URLs as `http://…`; browsers auto-upgrade these to HTTPS (HSTS is enabled). If a first-time visit ever shows broken styling, hard-refresh. |
| Lab result timing | CTMS pulls SENAITE results on a schedule (~15 min) plus webhook; allow time before treating a missing result as a failure. |
| Login credential casing | SENAITE `admin`/`admin` (lowercase). ERPNext username is `Administrator` (capital A). OpenClinica is `root`. Passwords are case-sensitive. |
| Query creation location | Depending on the deployed build, a query may be raised from the Queries page or from a subject's completed form instance — note where you found it. |
| Role-gated controls | Some controls (Generate Report, Move to locked, add Milestone) are limited to admin/study_admin/data_manager roles. Switch to an admin login if a control is missing. |
| Production data | This walkthrough creates real records in production. If re-running, either reuse the existing study or vary the Protocol Number to avoid duplicate-key errors. See cleanup note in Appendix B. |

---

## Results Summary

| Step | Area | Status | Notes |
|------|------|--------|-------|
| P1–P7 | Pre-test reachability | | |
| 1 | SSO login | | |
| 2 | Create study (+ eTMF auto-folder) | | |
| 3 | Add sites (+ ERPNext + Nextcloud sync) | | |
| 4 | Verify eTMF in Nextcloud | | |
| 5 | Screen subject | | |
| 6 | Enroll subject (+ OpenClinica sync) | | |
| 7 | Mobile EDC CRF (+ offline) | | |
| 8 | Subject sync in OpenClinica | | |
| 9 | Screening CRF in OpenClinica | | |
| 10 | SENAITE lab → CTMS Lab page | | |
| 11 | Report SAE + CIOMS PDF | | |
| 12 | SAE expedited timeline | | |
| 13 | Treatment CRF in OpenClinica | | |
| 14 | RBM study overview | | |
| 15 | Site risk heatmap | | |
| 16 | Data query lifecycle | | |
| 17 | Data export (ODM/CSV) | | |
| 18 | Database lock | | |
| 19 | Audit trail | | |
| 20 | Dashboard & system health | | |

**Overall result:** `[ ] All Pass`   `[ ] Pass with issues`   `[ ] Blocked`

**Go / No-Go for stakeholders:** ______________________________________________

**Tester sign-off:** ____________________________   **Date:** ____________

---

## Appendix A — OpenClinica One-Time Setup (Prerequisite)

OpenClinica-side steps (Steps 8, 9, 13, 17) require the study, events, and CRFs to exist in OpenClinica. On the deployed system this may already be configured. If OpenClinica shows no study/CRFs, an admin must complete the one-time setup first:

- Create study `HACT-PSBI-ETH-2026` with Study OID `S_PSBI2026`.
- Define events: `SE_SCREENING`, `SE_48H`, `SE_DAY2/4/8`, `SE_DAY15`, `SE_SAE`.
- Build CRFs: `A1_SCREEN_ENROLL`, `B1_RCT2_48H`, `B2_RCT2_TREATMENT`, `C1_SAE` and assign them to events.

Full field-level definitions are in `docs/Stakeholder_Demo_Guide.md` (OpenClinica Pre-Setup section) and `docs/OpenClinica_PSBI_CRF_Manual_Setup.md`.

---

## Appendix B — Cleanup After Testing (Optional)

Test data created in production (study, sites, subject, SAE, query) can be left in place for demo continuity, or removed by an administrator. There is no user-facing bulk-delete in the frontend; deletion of a study and its related records is an administrative action. If you need the environment reset, coordinate with the system administrator rather than deleting piecemeal through the UI (to avoid partial/inconsistent state).
