# OpenClinica CRF Data Entry — User Guide

**Audience:** Site coordinators, data-entry clerks, clinical research assistants, monitors, and data managers who capture or review clinical data in OpenClinica.
**Applies to:** HACT CTMS deployment of **OpenClinica Community Edition 3.13** at
`https://ctms.hacts.org/OpenClinica/`
**Example study used throughout:** `HACT-PSBI-ETH-2026-V2` (OID `S_HACTPSBI`) — the PSBI neonatal RCT.
The same steps apply to **any** study configured on this server.

> This guide covers the **daily data-entry workflow** for normal users. The one-time
> study build (creating studies, CRFs, event definitions, sites) is a Data Manager /
> Study Director task and is documented separately (see *OpenClinica_PSBI_CRF_Manual_Setup.md*
> and the "Building a new study" section near the end of this guide).

---

## 1. Before you start

### 1.1 What you need
- A personal OpenClinica **username and password** (never share accounts — every action is audit-logged against the logged-in user).
- A **role** assigned to you in the correct study/site (your Data Manager sets this up).
- The **source documents** you are transcribing (paper CRF, chart, lab slip, etc.).

### 1.2 The golden rules of clinical data entry
1. **Enter what the source says** — transcribe faithfully; do not interpret or "clean up" values.
2. **One person, one login.** Do not enter data under someone else's account.
3. **Never leave required fields blank** without a documented reason (use the flag/discrepancy note).
4. **Add a Reason for Change** whenever you edit data after it was first saved — this is a regulatory (ALCOA / 21 CFR Part 11) requirement.
5. **Do not delete data.** Corrections are made by editing with a reason; the old value stays in the audit trail.
6. **Sign only what you have verified.** An electronic signature is legally equivalent to a handwritten one.

### 1.3 Roles at a glance (what you can do)
| Role | Enter data | Verify (SDV) | Sign | Manage queries | Build study |
|---|---|---|---|---|---|
| **Data Entry Person / Clinical Research Coordinator** | ✅ | — | — | Respond | — |
| **Investigator** | ✅ | — | ✅ (sign subject casebook) | Respond | — |
| **Monitor** | — | ✅ | — | Raise/close | — |
| **Data Manager** | ✅ | ✅ | — | Raise/answer/close | ✅ |
| **Study Director** | ✅ | ✅ | ✅ | All | ✅ |

---

## 2. Logging in and selecting your study

1. Go to **`https://ctms.hacts.org/OpenClinica/`**.
2. Enter your **User Name** and **Password**, click **Login**.
3. Top-left shows your **current active Study/Site**. If it is not the study you want to work in, click **Change Study/Site**.
4. Choose the correct **study or site** (e.g. `HACT-PSBI-ETH-2026-V2` → site *Adama General Hospital*), click **Change Study**, then **Confirm**.

> **Why the site matters:** if you are a site coordinator, always switch to *your site* (not the parent study) before adding subjects, so subjects are attributed to the right site.

---

## 3. The data-entry lifecycle (overview)

```
 Add Subject  →  Schedule Event  →  Enter CRF data  →  Save / Mark Complete
                                                             │
                     (optional, if configured) Double Data Entry
                                                             │
                                Monitor: Source Data Verification (SDV)
                                                             │
                          Investigator/Director: Sign  →  Data Manager: Lock
```

Each **CRF** moves through statuses shown by coloured icons in the Subject Matrix:

| Icon / status | Meaning |
|---|---|
| **Not Started** | Event scheduled, no data yet |
| **Data Entry Started** | Some fields saved, not complete |
| **Completed** | All required fields entered and marked complete |
| **Signed** | Investigator has signed |
| **Locked** | Data Manager has locked; no further edits without unlock |

---

## 4. Step-by-step: entering CRF data

The example below uses the PSBI **Screening and Enrollment** event with the **A1_SCREEN_ENROLL** CRF, but the pattern is identical for every event/CRF.

### Step 1 — Add the subject (once per subject)
> In this deployment subjects are usually created in the **HACT CTMS frontend** and synced to OpenClinica automatically. Only add a subject directly in OpenClinica if instructed.

1. **Tasks → Subject Matrix** (or **Add Subject**).
2. Click **Add New Subject**.
3. Fill in:
   - **Study Subject ID** — the participant identifier (e.g. `PSBI-ADM-0001`). Use your study's ID convention.
   - **Enrollment Date** — date the participant was enrolled.
   - **Sex / Date of Birth** — if the study collects them.
4. Click **Submit** → **Continue**.

### Step 2 — Schedule the event
Data can only be entered against a **scheduled event**.

1. From the **Subject Matrix**, find the subject's row.
2. Under the event column (e.g. *Screening and Enrollment*), click the **calendar / Schedule** icon — or use **Tasks → Schedule Event**.
3. Set the **Start Date** (date the event occurred), optional **Location**, and **Status** (leave *scheduled*).
4. Click **Proceed to Enter Data**.

> **Repeating events (e.g. Serious Adverse Event):** you can schedule the same event more than once for a subject — each occurrence is numbered.

### Step 3 — Open the CRF and enter data
1. You'll see the list of CRFs for that event (e.g. `A1_SCREEN_ENROLL`). Click the **pencil / Enter Data** icon next to it.
2. The CRF opens **section by section** (e.g. *Screening → Demographics → Eligibility → Enrollment*).
3. For each field:
   - **Text / number fields:** type the value exactly as in the source. Respect units shown (e.g. *grams*, *°C*).
   - **Radio buttons (Yes/No):** click the correct option.
   - **Dropdowns (single-select):** pick the matching value (e.g. treatment arm).
   - **Dates:** use the **DD-MMM-YYYY** format (e.g. `02-Feb-2026`) or the date picker.
4. **Validation:** if a value is out of the allowed range (e.g. age not 0–59 days, weight outside 500–9000 g), OpenClinica shows an error — recheck the source and correct, or flag it (Step 6).

### Step 4 — Save
- Click **Save** at the bottom of each section. The CRF status becomes **Data Entry Started**.
- You can **stop and return later** — saved data persists. Reopen from the Subject Matrix.

### Step 5 — Mark complete
1. When all sections are filled, on the final section tick **Mark CRF Complete** (if shown) and click **Save**.
2. The CRF status becomes **Completed**.

### Step 6 — Flag a value / raise a note (discrepancy) when needed
Use this when a value is missing, unusual, illegible, or you need to document a reason.

1. Click the small **flag icon** next to the field.
2. Choose the note type:
   - **Annotation** — informational note (no action needed).
   - **Query** — asks a question that must be answered/resolved.
   - **Reason for Change** — required when you *edit* an already-saved value.
   - **Failed Value / Out of range** — for values outside expected limits.
3. Type a clear description and **Submit**.

### Step 7 — Editing data after saving (Reason for Change)
1. Reopen the CRF (**Enter Data** icon).
2. Change the value.
3. OpenClinica **requires a Reason for Change** — enter it (e.g. "transcription error, corrected against source"). Save.
4. The previous value remains in the **audit trail**.

---

## 5. Double Data Entry (if your CRF requires it)
Some CRFs are configured for **Double Data Entry** for quality (two independent people enter the same data).

1. **First pass:** Data-entry person #1 enters and completes the CRF.
2. **Second pass:** Data-entry person #2 opens the *same* CRF via **Double Data Entry** and re-enters it.
3. Where the two entries **differ**, OpenClinica highlights the field and you reconcile it against the source.
4. When both entries match and are reconciled, the CRF is complete.

---

## 6. Reviewing, verifying, and signing (Monitor / Investigator / Data Manager)

### 6.1 Source Data Verification (SDV) — Monitor
1. **Tasks → Source Data Verification** (or the SDV column in the Subject Matrix).
2. Compare the entered data against the **source documents**.
3. Mark each CRF **SDV Verified** (checkbox / green tick).

### 6.2 Notes & Discrepancies (queries) — everyone
1. **Tasks → Notes & Discrepancies** lists all open items for the study/site.
2. **Site staff** answer queries assigned to them (click the query → **Respond**).
3. **Monitors / Data Managers** review responses and **Close** resolved queries.
4. Target: **zero open queries** before locking.

### 6.3 Signing — Investigator / Study Director
1. Open the subject's record (Subject Matrix → **View**).
2. Review the completed, SDV-verified CRFs.
3. Click **Sign** for the event or the subject casebook.
4. Re-enter your password to apply the **electronic signature** (21 CFR Part 11).

### 6.4 Locking — Data Manager
Once signed and clean, the Data Manager sets the event/CRF status to **Locked**. Locked data cannot be edited without an explicit **Unlock** (which is audit-logged).

---

## 7. Quick reference — icons & where things live

| I want to… | Go to |
|---|---|
| See all subjects and CRF statuses | **Tasks → Subject Matrix** |
| Add a participant | **Subject Matrix → Add New Subject** |
| Schedule a visit/event | **Tasks → Schedule Event** |
| Enter or edit CRF data | Subject Matrix → **pencil** icon on the CRF |
| See/answer queries | **Tasks → Notes & Discrepancies** |
| Verify against source | **Tasks → Source Data Verification** |
| View the audit trail | **Tasks → Study Audit Log** |
| Change study/site | Top-left **Change Study/Site** |

**Common icons:** ✏️ Enter/Edit · 🔍/👁 View · 🗓 Schedule · 🚩 Flag/Discrepancy · 🔒 Lock · 🔓 Unlock · ✍ Sign

---

## 8. Do's and Don'ts

**Do**
- Switch to the **correct study/site** before every session.
- Save each section as you go.
- Use **DD-MMM-YYYY** dates.
- Add a **Reason for Change** for every post-save edit.
- Resolve queries promptly.

**Don't**
- Don't share logins or enter data for another person under your account.
- Don't guess values — flag missing/unclear data instead.
- Don't try to delete rows/values — correct with a reason.
- Don't sign data you haven't reviewed.
- Don't edit **Locked** CRFs without asking the Data Manager to unlock.

---

## 9. For the future — other OpenClinica tasks

### 9.1 Building a **new study** (Data Manager / Study Director)
The daily data entry above assumes the study is already built. To set up a **new** study, the build sequence (done once) is:

1. **Create the study** — *Tasks → Build Study → Create a New Study* (or Administer Studies → Create a New Study). Note the generated **Study OID** (OpenClinica truncates it to ~8 characters, e.g. `S_HACTPSBI`).
   - In HACT CTMS, set the **matching OID** on the study record (Study detail → *Edit study* → *OpenClinica Study OID*) so subjects sync from CTMS to OpenClinica.
2. **Create CRFs** — *Tasks → CRFs → Create a New CRF* → upload an **Excel CRF definition**.
   - Use the official **`CRF_Design_Template_v3.9.xls`** (5 sheets: `CRF`, `Sections`, `Groups`, `Items`, `Instructions`).
   - Save it as a **classic `.xls`** (BIFF8). Modern `.xlsx` written by some tools is rejected by this OpenClinica version.
   - Validation expressions must be written as **`func: range(min, max)`** (not bare `range(...)`).
   - Every item's `SECTION_LABEL` must exist in the *Sections* sheet; groups are recommended.
   - See *OpenClinica_CRF_Template_Fill_Guide.md* for the column-by-column rules.
3. **Create Event Definitions** — *Build Study → Create Event Definitions*: name, type (Scheduled / Unscheduled / Common), repeating (Yes/No), category, then assign the CRF(s) to each event.
4. **Create Sites** — *Build Study → Create Sites*: site name, **Unique Protocol ID**, PI, expected enrollment.
   - **Match the site's Unique Protocol ID to the CTMS site code** (e.g. `ETH-ADM-V2-001`) so CTMS→OpenClinica subject sync targets the right site.
5. **Set the study status to *Available*** — *Build Study → Set Study Status → Available → Save*. Subjects cannot be added while the study is in *Design/Pending*.
6. **Assign users & roles** — *Tasks → Users*: give each team member the correct role at the correct site.

### 9.2 Importing data in bulk
- **Tasks → Import Data** accepts an **ODM XML** file to load many responses at once (used by the CTMS integration and for migrations). Manual entry (this guide) is for day-to-day capture.

### 9.3 Extracting data for analysis
- **Tasks → Create Dataset** → define which events/CRFs/items to include → **View Datasets** → download as **CSV / Excel / ODM XML / SPSS**.

### 9.4 Audit trail
- **Tasks → Study Audit Log** shows every create/edit/delete with user, timestamp, old value, new value, and reason. This is the compliance record — review it during monitoring.

---

## 10. How this fits with HACT CTMS

In the HACT platform, OpenClinica is the **EDC (Electronic Data Capture)** system of record for clinical form data. In normal operation:

- Studies, sites, and subjects are created in the **CTMS frontend** and **sync into OpenClinica** automatically (a subject enrolled in CTMS appears in the OpenClinica Subject Matrix).
- Form data captured through the **CTMS mobile EDC (PWA)** syncs to OpenClinica in the background.
- You would use the **OpenClinica UI directly** (this guide) for: source data verification, monitoring, query management, signing, locking, dataset extraction, and any manual/legacy data entry.

> If a subject you enrolled in CTMS does **not** appear in OpenClinica, tell your administrator — it usually means the OpenClinica **web-services credentials** or the **study OID mapping** need attention, not a data-entry mistake.

---

*Document owner: HACT CTMS team · Keep this guide with the study's essential documents (eTMF → Study Management).*
