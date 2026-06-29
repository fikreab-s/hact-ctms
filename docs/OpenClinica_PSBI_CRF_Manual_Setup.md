# OpenClinica CE — PSBI RCT 2 Complete Manual Setup Guide

> **Study**: HACT-PSBI-ETH-2026 — RCT 2 PSBI Neonatal Treatment
> **URL**: http://localhost:8082/OpenClinica (or via NGINX proxy)
> **Login**: `root` / your password

---

## Overview: 7-Task Checklist (Do in This Order!)

```
Task 1: Create Study .................. ✅ DONE (you already did this)
Task 2: Create CRFs ................... 📋 DO THIS SECOND (4 forms)
Task 3: Create Event Definitions ...... 📋 DO THIS THIRD (7 events)
Task 4: Create Subject Group Classes .. 📋 OPTIONAL (treatment arms)
Task 5: Create Rules .................. ⏭️ SKIP FOR NOW
Task 6: Create Sites .................. 📋 DO THIS (2 hospitals)
Task 7: Assign Users .................. ✅ DONE (admin exists)
FINAL:  Set Study Status → Available .. 🚀 DO THIS LAST
```

> ⚠️ **IMPORTANT**: You MUST create CRFs (Task 2) BEFORE Event Definitions (Task 3), because events need CRFs assigned to them.

---

## Task 2: Create CRFs (4 Forms)

Go to: **Build Study page** → Click **➕** next to "Create CRF"

For each CRF below, you will:
1. Enter CRF Name → Click Continue
2. Create Version `v1.0` → Click Continue
3. Add items one by one (use the tables below)

---

### CRF 1: A1_SCREEN_ENROLL — Screening & Enrollment

**CRF Name**: `A1_SCREEN_ENROLL`
**Version**: `v1.0`
**Description**: `Screening and Enrollment Form for PSBI RCT 2`

#### Section: Screening Information

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| A1.1 | `SUBJID` | Identification number of the young infant | text | String | Yes | — |
| A1.2 | `SCRDTC` | Date of screening | text | Date | Yes | — |
| A1.3 | `SCRTM` | Time of screening (HH:MM) | text | String | No | — |
| A1.4 | `SCRCONS` | Consent for screening obtained from parent/guardian | radio | Integer | Yes | Yes=1, No=2 |

#### Section: Infant Demographics

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Units | Validation |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------|------------|
| A1.5 | `BRTHDTC` | Date of birth of the infant | text | Date | Yes | — | — | PHI=Yes |
| A1.6 | `AGE` | Age at screening (days) | text | Integer | No | — | days | range(0, 59) |
| A1.7 | `SEX` | Sex of the infant | radio | String | Yes | Male=M, Female=F, Unknown=U | — | — |
| A1.8 | `WEIGHT` | Weight of the infant | text | Real | Yes | — | grams | range(500, 9000) |

#### Section: Eligibility Assessment

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| A1.9 | `INCLMET` | All inclusion criteria met | radio | Integer | Yes | Yes=1, No=2 |
| A1.9a | `INCL1` | Age 0-59 days | radio | Integer | Yes | Yes=1, No=2 |
| A1.9b | `INCL2` | Signs of possible serious bacterial infection | radio | Integer | Yes | Yes=1, No=2 |
| A1.9c | `INCL3` | Parent/guardian willing to provide informed consent | radio | Integer | Yes | Yes=1, No=2 |
| A1.10 | `EXCLMET` | Any exclusion criteria present | radio | Integer | Yes | Yes=1, No=2 |
| A1.10a | `EXCL1` | Weight less than 1500 grams | radio | Integer | Yes | Yes=1, No=2 |
| A1.10b | `EXCL2` | Signs of critical illness requiring intensive care | radio | Integer | Yes | Yes=1, No=2 |
| A1.10c | `EXCL3` | Known congenital malformation incompatible with survival | radio | Integer | Yes | Yes=1, No=2 |

#### Section: Enrollment & Randomization

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Conditional |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------------|
| A1.11 | `ENROLLED` | Subject enrolled in the study | radio | Integer | Yes | Yes=1, No=2 | — |
| A1.12 | `ENRLDTC` | Date of enrollment | text | Date | No | — | Show if ENROLLED=1 |
| A1.13 | `RNDNUM` | Randomization number | text | String | No | — | Show if ENROLLED=1 |
| A1.14 | `TRTARM` | Treatment arm assigned | single-select | Integer | No | Continued Inpatient=1, Oral Amoxicillin=2 | Show if ENROLLED=1 |

**Total items: 18** → When done, click **Save** → Mark Task 2 checkbox for this CRF

---

### CRF 2: B1_RCT2_48H — 48-Hour Assessment

**CRF Name**: `B1_RCT2_48H`
**Version**: `v1.0`
**Description**: `48-Hour Assessment Form for RCT 2`

#### Section: Assessment Information

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| B1.1 | `SUBJID` | Identification number | text | String | Yes | — |
| B1.2 | `ASSESSDTC` | Date of assessment | text | Date | Yes | — |
| B1.3 | `ASSESSTM` | Time of assessment (HH:MM) | text | String | No | — |
| B1.4 | `ASSESSLOC` | Place of assessment | single-select | Integer | Yes | Hospital=1, Health Centre=2, Health Post=3, Home=4, Other=5 |

#### Section: Vital Signs

| # | Item Name | Question Text | Response Type | Data Type | Required | Units | Validation |
|---|-----------|--------------|---------------|-----------|----------|-------|------------|
| B1.5 | `TEMP` | Axillary temperature | text | Real | Yes | °C | range(34.0, 42.0) |
| B1.6 | `RESPRATE` | Respiratory rate | text | Integer | No | breaths/min | range(10, 100) |
| B1.7 | `HEARTRATE` | Heart rate | text | Integer | No | beats/min | range(60, 220) |

#### Section: Clinical Signs Assessment

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| B1.8 | `FEEDDIFF` | Feeding difficulty | single-select | Integer | Yes | No difficulty=1, Some difficulty=2, Not able to feed=3 |
| B1.9 | `CHESTIND` | Severe chest indrawing | radio | Integer | Yes | Yes=1, No=2 |
| B1.10 | `CONVULS` | Convulsions observed | radio | Integer | No | Yes=1, No=2 |
| B1.11 | `LETHARGY` | Lethargy or unconsciousness | radio | Integer | No | Yes=1, No=2 |
| B1.12 | `HYPOTHER` | Hypothermia (<35.5 °C) | radio | Integer | No | Yes=1, No=2 |
| B1.13 | `HYPERTHER` | Hyperthermia (≥38.0 °C) | radio | Integer | No | Yes=1, No=2 |
| B1.14 | `CRITILL` | Any critical illness signs present | radio | Integer | Yes | Yes=1, No=2 |

#### Section: Clinical Decision

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Conditional |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------------|
| B1.15 | `DSCHRG` | Decision: Infant can be discharged | radio | Integer | Yes | Yes=1, No=2 | — |
| B1.16 | `DSCHREASON` | If not discharged, reason for continued treatment | textarea | String | No | — | Show if DSCHRG=2 |

**Total items: 16** → Save → Mark complete

---

### CRF 3: B2_RCT2_TREATMENT — Treatment Record

**CRF Name**: `B2_RCT2_TREATMENT`
**Version**: `v1.0`
**Description**: `Treatment Record Form for RCT 2 (Days 2, 4, 8)`

#### Section: Visit Information

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| B2.1 | `SUBJID` | Identification number | text | String | Yes | — |
| B2.2 | `DAYNUM` | Visit day number | single-select | String | Yes | Day 2=D2, Day 4=D4, Day 8=D8 |
| B2.3 | `VISITDTC` | Date of visit | text | Date | Yes | — |
| B2.4 | `ASSESSLOC` | Place of completing this form | single-select | Integer | Yes | Hospital=1, Health Centre=2, Health Post=3, Home=4, Other=5 |
| B2.5 | `RESPONDENT` | Adult primary respondent present | single-select | Integer | No | Mother=1, Father=2, Grandmother=3, Grandfather=4, Other relative=5, Other=6 |

#### Section: Treatment Information

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Validation |
|---|-----------|--------------|---------------|-----------|----------|-----------------|------------|
| B2.6 | `AMOXGIVEN` | Oral amoxicillin given today | radio | Integer | Yes | Yes=1, No=2 | — |
| B2.7 | `REMTAB` | Remaining tablets/suspension (count or mL) | text | Real | No | — | range(0, 100) |
| B2.8 | `MISSEDDOSES` | Number of missed doses since last visit | text | Integer | No | — | range(0, 20) |
| B2.9 | `OTHABX` | Other antibiotic given (name) | text | String | No | — | — |
| B2.10 | `OTHABXREAS` | Reason for other antibiotic | textarea | String | No | — | — |

#### Section: Clinical Status

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Conditional |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------------|
| B2.11 | `FEEDSTAT` | Feeding status at this visit | single-select | Integer | No | No difficulty=1, Some difficulty=2, Not able to feed=3 | — |
| B2.12 | `TEMP` | Axillary temperature | text | Real | No | — (units: °C) | range(34.0, 42.0) |
| B2.13 | `IMPROVING` | Clinical condition improving | radio | Integer | No | Yes=1, No=2 | — |
| B2.14 | `HOSPREF` | Referred/readmitted to hospital | radio | Integer | No | Yes=1, No=2 | — |
| B2.15 | `HOSPREFREAS` | If referred, reason for referral | textarea | String | No | — | Show if HOSPREF=1 |

**Total items: 15** → Save → Mark complete

---

### CRF 4: C1_SAE — Serious Adverse Event

**CRF Name**: `C1_SAE`
**Version**: `v1.0`
**Description**: `Serious Adverse Event Form — PSBI`

#### Section: SAE Identification

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| C1.1 | `SUBJID` | Identification number of the young infant | text | String | Yes | — |
| C1.2 | `SAERPTDTC` | Date of filling this SAE form | text | Date | Yes | — |
| C1.3 | `SAERPTNUM` | SAE report number (for this subject) | text | Integer | Yes | — |

#### Section: Type of Adverse Event

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Conditional |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------------|
| C1.4 | `ANAPHYL` | Anaphylactic reaction | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.5 | `ALLERGIC` | Other allergic reaction / rash | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.6 | `INJSITE` | Injection site infection / abscess | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.7 | `DIARRHEA` | Diarrhoea with severe dehydration | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.8 | `AESLIFE` | Life-threatening adverse event | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.9 | `AESDEATH` | Death | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.10 | `AEOTHER` | Other serious adverse event | radio | Integer | Yes | Yes=1, No=2 | — |
| C1.10a | `AEOTHERSP` | If other, specify | text | String | No | — | Show if AEOTHER=1 |

#### Section: SAE Dates & Causality

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options |
|---|-----------|--------------|---------------|-----------|----------|-----------------|
| C1.11 | `AESTDTC` | Date of onset of the adverse event | text | Date | Yes | — |
| C1.12 | `AEENDTC` | Date of resolution (leave blank if ongoing) | text | Date | No | — |
| C1.13 | `AEREL` | Relationship to study treatment | single-select | Integer | Yes | Not related=1, Unlikely=2, Possible=3, Probable=4, Definite=5 |

#### Section: Outcome & Action

| # | Item Name | Question Text | Response Type | Data Type | Required | Response Options | Conditional |
|---|-----------|--------------|---------------|-----------|----------|-----------------|-------------|
| C1.14 | `AEACN` | Action taken with study drug | single-select | Integer | Yes | Drug withdrawn=1, Drug interrupted=2, Dose reduced=3, Dose not changed=4, Not applicable=5, Unknown=6 | — |
| C1.15 | `AEOUT` | Outcome of the adverse event | single-select | Integer | Yes | Recovered=1, Recovering=2, Not recovered=3, Fatal=4, Unknown=5 | — |
| C1.16 | `DTHDTC` | If fatal — date of death | text | Date | No | — | Show if AESDEATH=1 |
| C1.17 | `DTHCAUSE` | If fatal — primary cause of death | text | String | No | — | Show if AESDEATH=1 |

#### Section: Narrative Description

| # | Item Name | Question Text | Response Type | Data Type | Required |
|---|-----------|--------------|---------------|-----------|----------|
| C1.18 | `SAEDESC` | Detailed description of the SAE / death | textarea | String | Yes |
| C1.19 | `SAETRT` | Treatment given for the SAE | textarea | String | No |
| C1.20 | `RPTNAME` | Name of person completing this report | text | String | Yes |
| C1.21 | `RPTDESIG` | Designation / role | text | String | No |

**Total items: 21** → Save → Mark complete

---

## Task 3: Create Event Definitions (7 Events)

Go to: **Build Study page** → Click **➕** next to "Create Event Definitions"

For each event, fill in the form you see (Name, Description, Repeating, Type, Category), then click **Continue** to go through the 4-step workflow:

### Event 1: Screening & Enrollment

| Field | Value |
|-------|-------|
| **Name** | `Screening and Enrollment` |
| **Description** | `Initial screening, consent, eligibility, and enrollment` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `Screening` |

→ Click **Continue** → **Add CRFs**: Select `A1_SCREEN_ENROLL v1.0` → **Continue** → Set Required=Yes → **Confirm & Submit**

---

### Event 2: 48-Hour Assessment

| Field | Value |
|-------|-------|
| **Name** | `48-Hour Assessment` |
| **Description** | `48-hour clinical assessment for RCT 2 subjects` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `Treatment` |

→ **Add CRF**: `B1_RCT2_48H v1.0` → Submit

---

### Event 3: Day 2 Treatment Follow-up

| Field | Value |
|-------|-------|
| **Name** | `Day 2 Treatment Follow-up` |
| **Description** | `Day 2 treatment record` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `Treatment` |

→ **Add CRF**: `B2_RCT2_TREATMENT v1.0` → Submit

---

### Event 4: Day 4 Treatment Follow-up

| Field | Value |
|-------|-------|
| **Name** | `Day 4 Treatment Follow-up` |
| **Description** | `Day 4 treatment record` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `Treatment` |

→ **Add CRF**: `B2_RCT2_TREATMENT v1.0` → Submit

---

### Event 5: Day 8 Treatment Follow-up

| Field | Value |
|-------|-------|
| **Name** | `Day 8 Treatment Follow-up` |
| **Description** | `Day 8 treatment record` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `Treatment` |

→ **Add CRF**: `B2_RCT2_TREATMENT v1.0` → Submit

---

### Event 6: Day 15 Outcome Assessment

| Field | Value |
|-------|-------|
| **Name** | `Day 15 Outcome Assessment` |
| **Description** | `Day 15 primary outcome assessment` |
| **Repeating** | ◉ No |
| **Type** | `Scheduled` |
| **Category** | `FollowUp` |

→ **Add CRF**: `B2_RCT2_TREATMENT v1.0` (reuse treatment form for Day 15 outcome) → Submit

---

### Event 7: Serious Adverse Event ⚠️

| Field | Value |
|-------|-------|
| **Name** | `Serious Adverse Event` |
| **Description** | `Event-driven SAE reporting — can occur anytime` |
| **Repeating** | ◉ **Yes** ⚠️ (SAEs can happen multiple times!) |
| **Type** | `Unscheduled` |
| **Category** | `PreTreatment` |

→ **Add CRF**: `C1_SAE v1.0` → Submit

---

## Task 4: Create Subject Group Classes (Optional)

Click **➕** next to "Create Subject Group Classes"

| Field | Value |
|-------|-------|
| **Name** | `RCT 2 Treatment Arms` |
| **Type** | `Arm` |
| **Group 1 Name** | `Continued Inpatient Treatment` |
| **Group 1 Description** | `Standard hospital-based injectable antibiotic treatment` |
| **Group 2 Name** | `Discharged on Oral Amoxicillin` |
| **Group 2 Description** | `Discharged at 48h with oral amoxicillin` |

→ Submit

---

## Task 5: Create Rules — SKIP FOR NOW

You can add validation rules later.

---

## Task 6: Create Sites (2 Hospitals)

Click **➕** next to "Create Sites"

### Site 1:
| Field | Value |
|-------|-------|
| **Site Name** | `Adama General Hospital` |
| **Unique Protocol ID** | `ETH-ADM-001` |
| **Principal Investigator** | `Dr. Fikadu Beyene` |
| **Expected Enrollment** | `150` |
| **Status** | `Available` |

### Site 2:
| Field | Value |
|-------|-------|
| **Site Name** | `Jimma University Medical Center` |
| **Unique Protocol ID** | `ETH-JIM-002` |
| **Principal Investigator** | `Dr. Meron Tadesse` |
| **Expected Enrollment** | `150` |
| **Status** | `Available` |

---

## 🚀 FINAL STEP: Set Study Status → Available

Back on the **Build Study** page:

1. Set Study Status dropdown → **Available**
2. Click **Save Status**

✅ Your study is now live and ready for subject enrollment!

---

## Quick Reference: All Codelists Used

### YN (Yes/No)
| Label | Value |
|-------|-------|
| Yes | 1 |
| No | 2 |

### SEX
| Label | Value |
|-------|-------|
| Male | M |
| Female | F |
| Unknown | U |

### ASSESSLOC (Place of Assessment)
| Label | Value |
|-------|-------|
| Hospital | 1 |
| Health Centre | 2 |
| Health Post | 3 |
| Home | 4 |
| Other | 5 |

### RESPONDENT (Primary Caregiver)
| Label | Value |
|-------|-------|
| Mother | 1 |
| Father | 2 |
| Grandmother | 3 |
| Grandfather | 4 |
| Other relative | 5 |
| Other | 6 |

### TRTARM (Treatment Arm)
| Label | Value |
|-------|-------|
| Continued Inpatient Treatment | 1 |
| Discharged on Oral Amoxicillin | 2 |

### FEEDSTATUS (Feeding Status)
| Label | Value |
|-------|-------|
| No difficulty | 1 |
| Some difficulty | 2 |
| Not able to feed at all | 3 |

### AEACN (Action Taken)
| Label | Value |
|-------|-------|
| Drug withdrawn | 1 |
| Drug interrupted | 2 |
| Dose reduced | 3 |
| Dose not changed | 4 |
| Not applicable | 5 |
| Unknown | 6 |

### AEOUT (Outcome)
| Label | Value |
|-------|-------|
| Recovered | 1 |
| Recovering | 2 |
| Not recovered | 3 |
| Fatal | 4 |
| Unknown | 5 |

### AEREL (Causality)
| Label | Value |
|-------|-------|
| Not related | 1 |
| Unlikely | 2 |
| Possible | 3 |
| Probable | 4 |
| Definite | 5 |

### VISIT (Visit Day)
| Label | Value |
|-------|-------|
| Day 2 | D2 |
| Day 4 | D4 |
| Day 8 | D8 |

---

## Summary: Item Count per CRF

| CRF | Items | Sections |
|-----|-------|----------|
| A1_SCREEN_ENROLL | 18 | 4 (Screening, Demographics, Eligibility, Enrollment) |
| B1_RCT2_48H | 16 | 4 (Assessment, Vitals, Clinical Signs, Decision) |
| B2_RCT2_TREATMENT | 15 | 3 (Visit Info, Treatment, Clinical Status) |
| C1_SAE | 21 | 5 (ID, Type, Dates, Outcome, Narrative) |
| **Total** | **70** | **16** |
