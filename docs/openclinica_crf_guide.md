# OpenClinica CRF Implementation Guide — PSBI Study

> Based on analysis of `metadata_specification_for_PSBI_CRF_Draft.xlsx`

---

## 📊 Excel File Summary

Your team lead shared a **7-sheet specification** for the **PSBI (Possible Serious Bacterial Infection)** neonatal clinical trial. This is a dual-arm RCT (RCT 1 + RCT 2) studying treatment approaches for young infants with bacterial infections.

| Sheet | Purpose | Key Content |
|-------|---------|-------------|
| **README** | Overview | File introduction |
| **Form_Summary** | 9 CRF forms at a glance | Form codes, source .docx files, section counts, field counts |
| **Priority_Metadata** | 57 priority fields requiring immediate attention | Curated subset with proposed variable names, data types, codelists, validation rules, SDTM mapping |
| **Extracted_Draft_Fields** | 260 fields extracted from paper CRFs | Raw extraction from Word documents — the full field inventory |
| **Codelists** | 10 controlled terminology lists | Standardized value sets (Yes/No, Sex, AE outcomes, etc.) |
| **Visit_Schedule** | 8 study events | Screening → Day 15 outcome + event-driven SAE |
| **OpenClinica_Notes** | 9-step implementation checklist | Step-by-step instructions from the team lead |

---

## 🏥 What This Study Is About

**PSBI** = Possible Serious Bacterial Infection in young infants (0-59 days old)

- **RCT 1**: Infants with *low* mortality risk signs → treatment comparison
- **RCT 2**: Infants with *moderate* mortality risk signs → treatment comparison
- **Non-enrolled**: Infants screened but not enrolled → outcome tracking only
- **Bilingual forms**: English + Afaan Oromoo (Ethiopian local language)

---

## 📋 Step-by-Step OpenClinica Implementation

### Step 1: Create Study & Sites

> [!IMPORTANT]
> Do this first in OpenClinica Admin → **Create Study**

**Study Setup:**
- **Study Name**: `PSBI Neonatal Treatment Trial` (or per protocol)
- **Protocol ID**: Use your IRB-approved protocol number
- **Phase**: Phase III (or as per protocol)
- **Status**: Design

**Sites to Create:**
Create each participating hospital site. Based on the forms (Afaan Oromoo language), sites are likely in the **Oromia region, Ethiopia**. Create one site per hospital in OpenClinica → Build Study → Sites.

---

### Step 2: Create the 9 eCRF Forms

> [!IMPORTANT]
> In OpenClinica: **Tasks → Build Study → Create CRF**
> Use the `form_code` as the CRF Name/OID for clean referencing.

Here are all 9 forms from the `Form_Summary` sheet:

| # | Form Code | Form Name | Sections | Fields | When Used |
|---|-----------|-----------|----------|--------|-----------|
| 1 | **A1_SCREEN_ENROLL** | Screening, Enrollment, and Pre-enrollment | 15 | 69 | Screening visit |
| 2 | **A2_RCT1_TREATMENT** | RCT 1 Treatment Record | 4 | 14 | Day 2, 4, 8 (RCT 1) |
| 3 | **A3_RCT1_OUTCOME** | RCT 1 Outcome Assessment | 7 | 17 | Day 15 (RCT 1) |
| 4 | **B1_RCT2_48H_ALT** | RCT 2 48-hour Assessment (alt) | 11 | 48 | 48-hour visit (RCT 2) — *duplicate/alternate version* |
| 5 | **B1_RCT2_48H** | RCT 2 48-hour Assessment | 11 | 48 | 48-hour visit (RCT 2) — *primary version* |
| 6 | **B2_RCT2_TREATMENT** | RCT 2 Treatment Record | 4 | 14 | Day 2, 4, 8 (RCT 2) |
| 7 | **B3_RCT2_OUTCOME** | RCT 2 Outcome Assessment | 7 | 18 | Day 15 (RCT 2) |
| 8 | **C1_SAE** | Serious Adverse Event | 6 | 22 | Any time (event-driven) |
| 9 | **N1_NONENR_OUTCOME** | Non-enrolled Outcome | 4 | 10 | Day 15 (non-enrolled) |

> [!WARNING]
> **B1_RCT2_48H vs B1_RCT2_48H_ALT**: These are two versions of the same form. Clarify with the team lead which version to implement. Likely **B1_RCT2_48H** (v8.1) is the current version and _ALT is a backup/older draft.

---

### Step 3: Define Items Using `proposed_variable` Names

> [!CAUTION]
> **Do NOT use generic names like Q1, Q2, Q3!** The team lead explicitly requires using the `proposed_variable` column as the **Item Name** in OpenClinica.

For each form, create items (fields) in the CRF builder. Here's the mapping from the **Priority_Metadata** sheet — these 57 fields are the **highest priority** to get right:

#### Form A1: Screening & Enrollment (10 priority fields)

| Item Name | Label | Data Type | Control | Required | Codelist | Validation |
|-----------|-------|-----------|---------|----------|----------|------------|
| `SUBJID` | Identification number | text | text input | Yes | — | Unique within study/site |
| `SCRDTC` | Date of screening | date | date picker | Yes | — | Cannot be after enrollment date |
| `SCRTM` | Time of screening | time | time input | No | — | HH:MM 24-hour format |
| `SCRCONS` | Consent for screening obtained | coded | radio (Yes/No) | Yes | YN | If No → stop form |
| `BRTHDTC` | Date of birth | date | date picker | Yes | — | DOB ≤ screening date |
| `SEX` | Sex of infant | coded | radio/dropdown | Yes | SEX | M/F/U |
| `WEIGHT` | Weight of infant today | numeric | numeric input | Yes | UNIT_WEIGHT | Positive; unit = grams |
| `INCLMET` | Inclusion criteria met | coded | radio (Yes/No) | Yes | YN | Must be Yes to enroll |
| `EXCLMET` | Exclusion criteria present | coded | radio (Yes/No) | Yes | YN | If Yes → not eligible |
| `TRTARM` | Treatment arm (randomization) | coded | dropdown | Conditional | TRTARM | Required if enrolled |

#### Forms A2 & B2: Treatment Records (5 priority fields each)

| Item Name | Label | Data Type | Control | Required | Codelist |
|-----------|-------|-----------|---------|----------|----------|
| `DAYNUM` | Day number / visit day | numeric | dropdown/numeric | Yes | VISIT |
| `ASSESSLOC` | Place of completing form | coded | dropdown | Yes | ASSESSLOC |
| `RESPONDENT` | Adult primary respondent | coded | dropdown | Conditional | RESPONDENT |
| `OTHABX` | Other antibiotic name | text | text input | Conditional | — |
| `REMTAB` | Remaining tablets/suspension | numeric | numeric input | Conditional | — |

> [!NOTE]
> Treatment forms are **repeatable** — they're used at Day 2, Day 4, and Day 8. Mark these as repeating CRFs in OpenClinica.

#### Forms A3, B3, B1_48H, N1: Outcome/Assessment (6 priority fields each)

| Item Name | Label | Data Type | Control | Required | Codelist |
|-----------|-------|-----------|---------|----------|----------|
| `ASSESSDTC` | Date of assessment | date | date picker | Yes | — |
| `ASSESSLOC` | Place/mode of assessment | coded | dropdown | Yes | ASSESSLOC |
| `FEEDDIFF` | Difficulty feeding | coded | radio/dropdown | Yes | — |
| `CHESTIND` | Severe chest indrawing | coded | radio (Yes/No) | Yes | YN |
| `TEMP` | Axillary temperature | numeric | numeric input | Conditional | UNIT_TEMP |
| `CRITILL` | Primary outcome: critical illness | coded | radio (Yes/No) | Yes | YN |

#### Form C1: Serious Adverse Event (13 priority fields)

| Item Name | Label | Data Type | Control | Required | Codelist |
|-----------|-------|-----------|---------|----------|----------|
| `SUBJID` | Identification number | text | text input | Yes | — |
| `SAERPTDTC` | Date of filling SAE form | date | date picker | Yes | — |
| `ANAPHYL` | Anaphylactic reaction | coded | radio (Yes/No) | Yes | YN |
| `ALLERGIC` | Other allergic reaction/rash | coded | radio (Yes/No) | Yes | YN |
| `INJSITE` | Injection site infection/abscess | coded | radio (Yes/No) | Yes | YN |
| `DIARRHEA` | Diarrhoea with severe dehydration | coded | radio (Yes/No) | Yes | YN |
| `AESLIFE` | Life threatening AE | coded | radio (Yes/No) | Yes | YN |
| `AESTDTC` | Date of onset | date | date picker | Yes | — |
| `AEENDTC` | Date of resolution | date | date picker | Conditional | — |
| `AEACN` | Action taken | coded | dropdown | Yes | AEACN |
| `AEOUT` | Outcome of event | coded | dropdown | Yes | AEOUT |
| `DTHDTC` | Date of death | date | date picker | Conditional | — |
| `SAEDESC` | Brief description of SAE/death | text | textarea | Yes | — |

---

### Step 4: Mark Repeatable Forms/Sections

> [!IMPORTANT]
> These forms can have **multiple instances** per subject:

| Form | Why Repeatable |
|------|---------------|
| **A2_RCT1_TREATMENT** | Used at Day 2, Day 4, Day 8 |
| **B2_RCT2_TREATMENT** | Used at Day 2, Day 4, Day 8 |
| **C1_SAE** | Can occur anytime, multiple SAEs possible |

In OpenClinica: When assigning CRFs to events, check **"Allow multiple CRF instances"** or create them as repeating groups within the CRF.

---

### Step 5: Configure Visit Schedule (Study Events)

> [!IMPORTANT]
> In OpenClinica: **Tasks → Build Study → Create Study Event**

Create these 8 events from the `Visit_Schedule` sheet:

| Event Code | Event Name | Type | Forms Assigned | Notes |
|------------|-----------|------|----------------|-------|
| **SCR** | Screening | Scheduled | A1_SCREEN_ENROLL | Required before enrollment |
| **BL** | Baseline/Enrollment | Scheduled | A1_SCREEN_ENROLL | May be same day as screening |
| **D2** | Day 2 Follow-up | Scheduled | A2_RCT1_TREATMENT, B2_RCT2_TREATMENT | Visit window TBD |
| **D4** | Day 4 Follow-up | Scheduled | A2_RCT1_TREATMENT, B2_RCT2_TREATMENT | Visit window TBD |
| **D8** | Day 8 Follow-up | Scheduled | A2_RCT1_TREATMENT, B2_RCT2_TREATMENT | Visit window TBD |
| **48H** | 48-hour Assessment | Scheduled | B1_RCT2_48H | RCT 2 subjects only; window TBD |
| **D15** | Day 15 Outcome | Scheduled | A3_RCT1_OUTCOME, B3_RCT2_OUTCOME, N1_NONENR_OUTCOME | Enrolled + non-enrolled |
| **SAE** | Serious Adverse Event | Unscheduled | C1_SAE | Event-driven, can occur anytime |

> [!NOTE]
> **Which treatment form to show**: RCT 1 subjects get `A2_RCT1_TREATMENT`; RCT 2 subjects get `B2_RCT2_TREATMENT`. You'll need conditional CRF assignment or use event-level rules in OpenClinica to show the correct form based on the randomization arm (`TRTARM`).

---

### Step 6: Create Codelists (Response Options)

> [!IMPORTANT]
> In OpenClinica CRF builder: Define these as **Response Sets** when building each CRF.

From the `Codelists` sheet — create these 10 standardized value sets:

| Codelist Name | Label | Values | Usage Notes |
|---------------|-------|--------|-------------|
| **YN** | Yes/No | `1=Yes; 2=No` | Use consistently across all Yes/No fields |
| **SEX** | Sex | `M=Male; F=Female; U=Undetermined/Unknown` | Aligns with SDTM CT |
| **ASSESSLOC** | Assessment Location | `Home; Hospital; Health facility/clinic; Telephone/video call; Other` | Used in treatment & outcome forms |
| **RESPONDENT** | Adult Respondent | `Mother; Father; Other; NA` | Treatment follow-up forms |
| **AEOUT** | AE Outcome | `Resolved; Improved; Unchanged; Worsened; Death; Lost to follow-up` | Align with CDISC CT |
| **AEACN** | Action Taken | `None; Reduce dosage; Discontinue therapy; Hospitalized; Other` | Maps to SDTM AEACN |
| **UNIT_WEIGHT** | Weight Units | `grams` | Standardize to grams |
| **UNIT_TEMP** | Temperature Units | `C; F` | Prefer Celsius; require unit field |
| **TRTARM** | Treatment Arm | *Study-specific — to be defined per protocol* | Randomization assignment |
| **VISIT** | Visit Codes | `SCR; BL; D2; D4; D8; D15; 48H; SAE` | Must match visit schedule |

> [!CAUTION]
> **Stored values matter!** For Yes/No, use `1`/`2` as the stored database values (not "Yes"/"No" strings). This makes data extraction and SDTM mapping cleaner.

---

### Step 7: Add Edit Checks (Validation Rules)

In OpenClinica: **Tasks → Build Study → Create Rule** (or use the Rules Designer)

#### Critical Validation Rules to Implement:

**Date Logic:**
| Rule | Fields | Logic |
|------|--------|-------|
| DOB before screening | `BRTHDTC` vs `SCRDTC` | `BRTHDTC <= SCRDTC` |
| Screening before enrollment | `SCRDTC` vs enrollment date | `SCRDTC <= enrollment date` |
| SAE onset before resolution | `AESTDTC` vs `AEENDTC` | `AESTDTC <= AEENDTC` |
| SAE form date after onset | `SAERPTDTC` vs `AESTDTC` | `SAERPTDTC >= AESTDTC` |
| Death date required if fatal | `DTHDTC` | Required when `AEOUT = Death` |

**Conditional Logic:**
| Rule | Condition | Action |
|------|-----------|--------|
| Stop if no consent | `SCRCONS = No` | Hide remaining form sections or show warning |
| Not eligible if exclusion | `EXCLMET = Yes` | Block enrollment |
| Must meet inclusion | `INCLMET = Yes` | Required for randomization |
| Treatment arm required | If subject enrolled | `TRTARM` becomes required |

**Range Checks:**
| Field | Validation |
|-------|------------|
| `WEIGHT` | Positive value; realistic range for neonates (500–6000 grams) |
| `TEMP` | Human temperature range (35.0–42.0°C) |
| `REMTAB` | Non-negative value |

---

### Step 8: Assign Role-Based Access

In OpenClinica: **Tasks → Administration → Users**

| Role | Form Access | Notes |
|------|-------------|-------|
| **Research Assistant (RA)** | All clinical CRFs (A1-N1) | Primary data entry |
| **Data Manager** | All CRFs + queries | Data review and query resolution |
| **Safety Officer** | C1_SAE priority access | SAE form review and CIOMS generation |
| **Monitor / CRA** | Read-only all CRFs | Source data verification |
| **PI / Investigator** | Sign/lock forms | 21 CFR Part 11 electronic signatures |

---

### Step 9: Test with Dummy Subjects

> [!IMPORTANT]
> Before going live, enter 2-3 test subjects covering these scenarios:

| Test Scenario | What to Test |
|--------------|--------------|
| **RCT 1 full pathway** | SCR → BL → D2 → D4 → D8 → D15 with A-forms |
| **RCT 2 full pathway** | SCR → BL → 48H → D2 → D4 → D8 → D15 with B-forms |
| **Non-enrolled subject** | SCR → screen failure → N1 outcome |
| **SAE event** | Any subject + C1_SAE form (unscheduled event) |
| **Consent refused** | SCR → consent = No → form should stop |
| **Edit check firing** | Enter invalid dates, out-of-range values |

Then test data extraction from OpenClinica → PostgreSQL.

---

### Step 9 (Final): Prepare SDTM Mapping

The `Priority_Metadata` sheet includes `sdtm_domain` and `sdtm_variable` columns. These are early guides for CDISC SDTM compliance:

| SDTM Domain | Fields Mapped | Purpose |
|-------------|--------------|---------|
| **DM** (Demographics) | SUBJID, BRTHDTC, SEX, TRTARM | Subject demographics |
| **SV** (Subject Visits) | SCRDTC, ASSESSDTC, DAYNUM | Visit dates and schedule |
| **DS** (Disposition) | SCRCONS, INCLMET, EXCLMET | Enrollment disposition |
| **VS** (Vital Signs) | WEIGHT, TEMP | Vital sign measurements |
| **FA** (Findings About) | FEEDDIFF, CHESTIND, ASSESSLOC, CRITILL | Clinical assessments |
| **AE** (Adverse Events) | AESTDTC, AEENDTC, AEACN, AEOUT, AESLIFE, SAEDESC | SAE reporting |
| **CM** (Con Meds) | OTHABX | Concomitant medications |
| **EX** (Exposure) | REMTAB | Treatment compliance |
| **IE** (Inclusion/Exclusion) | INCLMET, EXCLMET | Eligibility criteria |

> [!NOTE]
> SDTM mapping will be finalized later. For now, using the `proposed_variable` names from the specification ensures the variable names are already SDTM-aligned, making future mapping much easier.

---

## 📂 Full Field Inventory

Beyond the 57 priority fields, the **Extracted_Draft_Fields** sheet contains **260 fields** extracted from the paper CRFs. These are the raw extractions with `TBD` status markers — they need clinical/DM team review before implementation. The priority fields above cover the most critical ones.

---

## ⚡ Quick-Start Checklist for OpenClinica

```
☐ 1. Create study in OpenClinica (Admin → Create Study)
☐ 2. Add sites (Build Study → Sites)
☐ 3. Create 10 codelists as response sets
☐ 4. Build CRF: A1_SCREEN_ENROLL (69 fields, 15 sections)
☐ 5. Build CRF: A2_RCT1_TREATMENT (14 fields, 4 sections, repeatable)
☐ 6. Build CRF: A3_RCT1_OUTCOME (17 fields, 7 sections)
☐ 7. Build CRF: B1_RCT2_48H (48 fields, 11 sections)
☐ 8. Build CRF: B2_RCT2_TREATMENT (14 fields, 4 sections, repeatable)
☐ 9. Build CRF: B3_RCT2_OUTCOME (18 fields, 7 sections)
☐ 10. Build CRF: C1_SAE (22 fields, 6 sections, repeatable)
☐ 11. Build CRF: N1_NONENR_OUTCOME (10 fields, 4 sections)
☐ 12. Clarify B1_RCT2_48H_ALT vs B1_RCT2_48H with team lead
☐ 13. Create 8 study events (visit schedule)
☐ 14. Assign CRFs to events
☐ 15. Add edit checks (date logic, range checks, conditional logic)
☐ 16. Configure role-based access
☐ 17. Enter 2-3 test subjects
☐ 18. Test data extraction to PostgreSQL
☐ 19. Review SDTM mapping columns for future compliance
```

---

## ❓ Questions to Clarify with Team Lead

> [!WARNING]
> Before proceeding, get answers to these:

1. **B1_RCT2_48H vs B1_RCT2_48H_ALT** — Which version should be implemented? Are both needed or is _ALT a deprecated draft?
2. **Visit windows** — Day 2, 4, 8, 48H, and D15 visit windows are marked "TBD". What are the allowed day ranges (e.g., Day 8 ± 2 days)?
3. **TRTARM codelist** — Treatment arm values are "study-specific" and TBD. What are the exact arm names/codes?
4. **Screening + Baseline same day?** — Visit_Schedule notes these "may be same day." Should SCR and BL be separate events or combined?
5. **Conditional form assignment** — How to handle showing A-forms (RCT 1) vs B-forms (RCT 2) per subject? Manual assignment or rule-based?
6. **260 draft fields** — All marked "Needs review from clinical/DM team." Should you implement all 260 now or only the 57 priority fields first?
