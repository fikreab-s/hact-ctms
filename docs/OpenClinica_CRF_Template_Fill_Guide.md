# How to Fill the OpenClinica CRF Template (v3.9) for PSBI

> **Template file**: `CRF_Design_Template_v3.9.xls`
> **You need to create 4 copies** — one for each CRF. Rename each copy before editing.

---

## Step 0: Create 4 Copies of the Template

```
Copy CRF_Design_Template_v3.9.xls → A1_SCREEN_ENROLL_v1.0.xls
Copy CRF_Design_Template_v3.9.xls → B1_RCT2_48H_v1.0.xls
Copy CRF_Design_Template_v3.9.xls → B2_RCT2_TREATMENT_v1.0.xls
Copy CRF_Design_Template_v3.9.xls → C1_SAE_v1.0.xls
```

---

## The Template Has 4 Sheets — Here's What Each Does

| Sheet | Purpose | How Many Rows to Fill |
|-------|---------|----------------------|
| **CRF** | CRF name and version (1 row only) | 1 row |
| **Sections** | Visual sections/headers on the form | 3-5 rows per CRF |
| **Groups** | Item groups | 3-5 rows per CRF |
| **Items** | The actual data fields (this is the big one!) | 15-21 rows per CRF |

> ⚠️ **The "Instructions" sheet** is just documentation — DO NOT edit it. Leave it as is.

---

## Sheet 1: CRF — Fill Just 1 Row

### Columns in the CRF Sheet

| Column | What to Put | Required? |
|--------|------------|-----------|
| **CRF_NAME** | Name of the form | ✅ Yes |
| **VERSION** | Version label | ✅ Yes |
| **VERSION_DESCRIPTION** | What this form captures | ✅ Yes |
| **REVISION_NOTES** | Notes about this version | No |

### What to Fill

#### File: A1_SCREEN_ENROLL_v1.0.xls

| CRF_NAME | VERSION | VERSION_DESCRIPTION | REVISION_NOTES |
|----------|---------|---------------------|----------------|
| `A1_SCREEN_ENROLL` | `v1.0` | `Screening and Enrollment Form for PSBI RCT 2` | `Initial version` |

#### File: B1_RCT2_48H_v1.0.xls

| CRF_NAME | VERSION | VERSION_DESCRIPTION | REVISION_NOTES |
|----------|---------|---------------------|----------------|
| `B1_RCT2_48H` | `v1.0` | `48-Hour Assessment Form for RCT 2` | `Initial version` |

#### File: B2_RCT2_TREATMENT_v1.0.xls

| CRF_NAME | VERSION | VERSION_DESCRIPTION | REVISION_NOTES |
|----------|---------|---------------------|----------------|
| `B2_RCT2_TREATMENT` | `v1.0` | `Treatment Record Form for RCT 2 (Days 2, 4, 8)` | `Initial version` |

#### File: C1_SAE_v1.0.xls

| CRF_NAME | VERSION | VERSION_DESCRIPTION | REVISION_NOTES |
|----------|---------|---------------------|----------------|
| `C1_SAE` | `v1.0` | `Serious Adverse Event Form` | `Initial version` |

---

## Sheet 2: Sections — Define Visual Sections

### Columns in the Sections Sheet

| Column | What to Put | Required? |
|--------|------------|-----------|
| **SECTION_LABEL** | Short code (no spaces, used to link items) | ✅ Yes |
| **SECTION_TITLE** | Display title shown on the form | ✅ Yes |
| **SUBTITLE** | Smaller text below the title | No |
| **INSTRUCTIONS** | Help text for staff filling the form | No |
| **PAGE_NUMBER** | For multi-page forms (leave blank) | No |
| **PARENT_SECTION** | Nested section (leave blank) | No |

### A1_SCREEN_ENROLL — Sections (4 rows)

| SECTION_LABEL | SECTION_TITLE | SUBTITLE | INSTRUCTIONS | PAGE_NUMBER | PARENT_SECTION |
|---------------|---------------|----------|--------------|-------------|----------------|
| `screening` | `Screening Information` | `Part A: Subject identification and screening` | `Complete at time of initial screening` | | |
| `demographics` | `Infant Demographics` | `Date of birth, sex, and weight` | `Record infant demographic data as observed` | | |
| `eligibility` | `Eligibility Assessment` | `Inclusion and exclusion criteria` | `Assess all criteria. Both must be satisfied` | | |
| `enrollment` | `Enrollment and Randomization` | `Treatment arm assignment` | `Complete only if eligible and consented` | | |

### B1_RCT2_48H — Sections (4 rows)

| SECTION_LABEL | SECTION_TITLE | SUBTITLE | INSTRUCTIONS | PAGE_NUMBER | PARENT_SECTION |
|---------------|---------------|----------|--------------|-------------|----------------|
| `assessment` | `Assessment Information` | `Visit details` | `Complete 48 hours after enrollment` | | |
| `vitals` | `Vital Signs` | `Temperature and observations` | `Use calibrated digital thermometer` | | |
| `signs` | `Clinical Signs` | `Danger signs assessment` | `Assess each sign carefully` | | |
| `decision` | `Clinical Decision` | `Discharge or continue treatment` | `Based on clinical assessment` | | |

### B2_RCT2_TREATMENT — Sections (3 rows)

| SECTION_LABEL | SECTION_TITLE | SUBTITLE | INSTRUCTIONS | PAGE_NUMBER | PARENT_SECTION |
|---------------|---------------|----------|--------------|-------------|----------------|
| `visit_info` | `Visit Information` | `Follow-up visit details` | `Complete at each follow-up (Day 2, 4, 8)` | | |
| `treatment` | `Treatment Information` | `Medication compliance` | `Record treatment status and compliance` | | |
| `status` | `Clinical Status` | `Current condition` | `Assess current clinical condition` | | |

### C1_SAE — Sections (5 rows)

| SECTION_LABEL | SECTION_TITLE | SUBTITLE | INSTRUCTIONS | PAGE_NUMBER | PARENT_SECTION |
|---------------|---------------|----------|--------------|-------------|----------------|
| `sae_id` | `SAE Identification` | `Subject and report information` | `Complete when SAE occurs` | | |
| `sae_type` | `Type of Adverse Event` | `Classification` | `Check all types that apply` | | |
| `sae_dates` | `Dates and Causality` | `Onset, resolution, relationship` | `Record all dates accurately` | | |
| `sae_outcome` | `Outcome and Action` | `Action taken and outcome` | `Record action and final outcome` | | |
| `sae_narrative` | `Narrative Description` | `Detailed description` | `Provide clinical narrative` | | |

---

## Sheet 3: Groups — Define Item Groups

### Columns in the Groups Sheet

| Column | What to Put | Required? |
|--------|------------|-----------|
| **GROUP_LABEL** | Short code (no spaces) | ✅ Yes |
| **GROUP_LAYOUT** | Leave blank (default) | No |
| **GROUP_HEADER** | Display header for the group | No |
| **GROUP_REPEAT_NUMBER** | For repeating groups (leave blank) | No |
| **GROUP_REPEAT_MAX** | Max repeats (leave blank) | No |

### A1_SCREEN_ENROLL — Groups

| GROUP_LABEL | GROUP_LAYOUT | GROUP_HEADER | GROUP_REPEAT_NUMBER | GROUP_REPEAT_MAX |
|-------------|-------------|-------------|--------------------|-----------------| 
| `screening_grp` | | `Screening Data` | | |
| `demographics_grp` | | `Infant Demographics` | | |
| `eligibility_grp` | | `Eligibility Criteria` | | |
| `enrollment_grp` | | `Enrollment Data` | | |

### B1_RCT2_48H — Groups

| GROUP_LABEL | GROUP_LAYOUT | GROUP_HEADER | GROUP_REPEAT_NUMBER | GROUP_REPEAT_MAX |
|-------------|-------------|-------------|--------------------|-----------------| 
| `assess_grp` | | `Assessment` | | |
| `vitals_grp` | | `Vital Signs` | | |
| `signs_grp` | | `Clinical Signs` | | |
| `decision_grp` | | `Decision` | | |

### B2_RCT2_TREATMENT — Groups

| GROUP_LABEL | GROUP_LAYOUT | GROUP_HEADER | GROUP_REPEAT_NUMBER | GROUP_REPEAT_MAX |
|-------------|-------------|-------------|--------------------|-----------------| 
| `visit_grp` | | `Visit Details` | | |
| `treatment_grp` | | `Treatment` | | |
| `status_grp` | | `Clinical Status` | | |

### C1_SAE — Groups

| GROUP_LABEL | GROUP_LAYOUT | GROUP_HEADER | GROUP_REPEAT_NUMBER | GROUP_REPEAT_MAX |
|-------------|-------------|-------------|--------------------|-----------------| 
| `sae_id_grp` | | `Identification` | | |
| `sae_type_grp` | | `Event Type` | | |
| `sae_dates_grp` | | `Dates` | | |
| `sae_outcome_grp` | | `Outcome` | | |
| `sae_narrative_grp` | | `Narrative` | | |

---

## Sheet 4: Items — THE MAIN SHEET (All Your Data Fields)

### ALL 27 Columns (in the exact order they appear in the template)

| # | Column Name | What to Put | Required? |
|---|------------|------------|-----------|
| A | **ITEM_NAME** | Variable name (UPPERCASE, no spaces) | ✅ Yes |
| B | **DESCRIPTION_LABEL** | Internal description (same as LEFT_ITEM_TEXT is fine) | ✅ Yes |
| C | **LEFT_ITEM_TEXT** | Question text shown LEFT of the input field | ✅ Yes |
| D | **UNITS** | Unit of measurement (grams, °C, etc.) | No |
| E | **RIGHT_ITEM_TEXT** | Text shown RIGHT of the field | No |
| F | **SECTION_LABEL** | Must match a label from the Sections sheet | ✅ Yes |
| G | **GROUP_LABEL** | Must match a label from the Groups sheet | ✅ Yes |
| H | **HEADER** | Bold header text displayed ABOVE this item | No |
| I | **SUBHEADER** | Sub-header text below the header | No |
| J | **PARENT_ITEM** | Leave blank | No |
| K | **COLUMN_NUMBER** | Leave blank (defaults to 1 column layout) | No |
| L | **PAGE_NUMBER** | Leave blank (single page) | No |
| M | **QUESTION_NUMBER** | Question number label (A1.1, B1.5, etc.) | No |
| N | **RESPONSE_TYPE** | `text`, `textarea`, `radio`, `single-select`, etc. | ✅ Yes |
| O | **RESPONSE_LABEL** | Codelist name for radio/select; item name for text | ✅ Yes |
| P | **RESPONSE_OPTIONS_TEXT** | Comma-separated labels (e.g., `Yes,No`) | For radio/select |
| Q | **RESPONSE_VALUES_OR_CALCULATIONS** | Comma-separated values (e.g., `1,2`) | For radio/select |
| R | **RESPONSE_LAYOUT** | `Horizontal` for radio buttons (leave blank for text) | No |
| S | **DEFAULT_VALUE** | Leave blank | No |
| T | **DATA_TYPE** | `ST`, `INT`, `REAL`, `DATE` | ✅ Yes |
| U | **WIDTH_DECIMAL** | Leave blank | No |
| V | **VALIDATION** | e.g., `range(0, 59)` | No |
| W | **VALIDATION_ERROR_MESSAGE** | Error text if validation fails | No |
| X | **PHI** | `0` = No, `1` = Yes (Protected Health Info) | No |
| Y | **REQUIRED** | `1` = Yes, `0` = No | No |
| Z | **ITEM_DISPLAY_STATUS** | `HIDE` for conditionally shown items | No |
| AA | **SIMPLE_CONDITIONAL_DISPLAY** | e.g., `ENROLLED,1` (show when ENROLLED=1) | No |

### Quick Reference for RESPONSE_TYPE and DATA_TYPE

**RESPONSE_TYPE:**
| Value | Creates | Use When |
|-------|---------|----------|
| `text` | Single-line text box | Text, dates, numbers |
| `textarea` | Multi-line text box | Long descriptions |
| `radio` | Radio buttons (pick one) | Yes/No, Sex |
| `single-select` | Dropdown (pick one) | Lists with 3+ options |

**DATA_TYPE:**
| Value | Meaning | Use For |
|-------|---------|---------|
| `ST` | String | Text, IDs, free text |
| `INT` | Integer | Whole numbers, coded values (radio/select) |
| `REAL` | Decimal | Weight, temperature |
| `DATE` | Date | All dates |

**RESPONSE_LABEL Rules:**
- For `text` / `textarea` items → use item name in lowercase (e.g., `subjid`)
- For `radio` / `single-select` items → use a shared codelist name (e.g., `yn`)
- ⚠️ If two items share the SAME codelist name, they MUST have identical RESPONSE_OPTIONS_TEXT and RESPONSE_VALUES

---

## CRF 1: A1_SCREEN_ENROLL — Items Sheet (18 rows, ALL 27 columns)

> ⚠️ Empty cells = leave blank in Excel. Each row is one item.

**Row 1 — SUBJID:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SUBJID` |
| DESCRIPTION_LABEL | `Identification number of the young infant` |
| LEFT_ITEM_TEXT | `Identification number of the young infant` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `screening` |
| GROUP_LABEL | `screening_grp` |
| HEADER | `Subject Identification` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.1` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `subjid` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `ST` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 2 — SCRDTC:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SCRDTC` |
| DESCRIPTION_LABEL | `Date of screening` |
| LEFT_ITEM_TEXT | `Date of screening` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `screening` |
| GROUP_LABEL | `screening_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.2` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `scrdtc` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `DATE` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 3 — SCRTM:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SCRTM` |
| DESCRIPTION_LABEL | `Time of screening` |
| LEFT_ITEM_TEXT | `Time of screening (HH:MM)` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `screening` |
| GROUP_LABEL | `screening_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.3` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `scrtm` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `ST` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 4 — SCRCONS:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SCRCONS` |
| DESCRIPTION_LABEL | `Consent for screening obtained` |
| LEFT_ITEM_TEXT | `Consent for screening obtained from parent/guardian` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `screening` |
| GROUP_LABEL | `screening_grp` |
| HEADER | `Consent` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.4` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 5 — BRTHDTC:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `BRTHDTC` |
| DESCRIPTION_LABEL | `Date of birth of the infant` |
| LEFT_ITEM_TEXT | `Date of birth of the infant` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `demographics` |
| GROUP_LABEL | `demographics_grp` |
| HEADER | `Infant Demographics` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.5` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `brthdtc` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `DATE` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `1` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 6 — AGE:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `AGE` |
| DESCRIPTION_LABEL | `Age at screening in days` |
| LEFT_ITEM_TEXT | `Age at screening (days)` |
| UNITS | `days` |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `demographics` |
| GROUP_LABEL | `demographics_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.6` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `age` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | `range(0, 59)` |
| VALIDATION_ERROR_MESSAGE | `Age must be between 0 and 59 days` |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 7 — SEX:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SEX` |
| DESCRIPTION_LABEL | `Sex of the infant` |
| LEFT_ITEM_TEXT | `Sex of the infant` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `demographics` |
| GROUP_LABEL | `demographics_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.7` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `sex` |
| RESPONSE_OPTIONS_TEXT | `Male,Female,Unknown` |
| RESPONSE_VALUES_OR_CALCULATIONS | `M,F,U` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `ST` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 8 — WEIGHT:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `WEIGHT` |
| DESCRIPTION_LABEL | `Weight of the infant in grams` |
| LEFT_ITEM_TEXT | `Weight of the infant` |
| UNITS | `grams` |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `demographics` |
| GROUP_LABEL | `demographics_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.8` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `weight` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `REAL` |
| WIDTH_DECIMAL | |
| VALIDATION | `range(500, 9000)` |
| VALIDATION_ERROR_MESSAGE | `Weight must be between 500 and 9000 grams` |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 9 — INCLMET:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `INCLMET` |
| DESCRIPTION_LABEL | `All inclusion criteria met` |
| LEFT_ITEM_TEXT | `All inclusion criteria met` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | `Inclusion Criteria` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.9` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 10 — INCL1:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `INCL1` |
| DESCRIPTION_LABEL | `Inclusion: Age 0-59 days` |
| LEFT_ITEM_TEXT | `Age 0-59 days` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | |
| SUBHEADER | `Individual inclusion criteria` |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.9a` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 11 — INCL2:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `INCL2` |
| DESCRIPTION_LABEL | `Inclusion: Signs of PSBI` |
| LEFT_ITEM_TEXT | `Signs of possible serious bacterial infection` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.9b` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 12 — INCL3:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `INCL3` |
| DESCRIPTION_LABEL | `Inclusion: Consent willing` |
| LEFT_ITEM_TEXT | `Parent/guardian willing to provide informed consent` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.9c` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 13 — EXCLMET:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `EXCLMET` |
| DESCRIPTION_LABEL | `Any exclusion criteria present` |
| LEFT_ITEM_TEXT | `Any exclusion criteria present` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | `Exclusion Criteria` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.10` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 14 — EXCL1:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `EXCL1` |
| DESCRIPTION_LABEL | `Exclusion: Weight below 1500g` |
| LEFT_ITEM_TEXT | `Weight less than 1500 grams` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.10a` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 15 — EXCL2:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `EXCL2` |
| DESCRIPTION_LABEL | `Exclusion: Critical illness` |
| LEFT_ITEM_TEXT | `Signs of critical illness requiring intensive care` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `eligibility` |
| GROUP_LABEL | `eligibility_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.10b` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 16 — ENROLLED:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `ENROLLED` |
| DESCRIPTION_LABEL | `Subject enrolled in the study` |
| LEFT_ITEM_TEXT | `Subject enrolled in the study` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `enrollment` |
| GROUP_LABEL | `enrollment_grp` |
| HEADER | `Enrollment Decision` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.11` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 17 — ENRLDTC:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `ENRLDTC` |
| DESCRIPTION_LABEL | `Date of enrollment` |
| LEFT_ITEM_TEXT | `Date of enrollment` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `enrollment` |
| GROUP_LABEL | `enrollment_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.12` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `enrldtc` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `DATE` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | `HIDE` |
| SIMPLE_CONDITIONAL_DISPLAY | `ENROLLED,1` |

**Row 18 — TRTARM:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `TRTARM` |
| DESCRIPTION_LABEL | `Treatment arm assigned` |
| LEFT_ITEM_TEXT | `Treatment arm assigned` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `enrollment` |
| GROUP_LABEL | `enrollment_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `A1.13` |
| RESPONSE_TYPE | `single-select` |
| RESPONSE_LABEL | `trtarm` |
| RESPONSE_OPTIONS_TEXT | `Continued Inpatient Treatment,Discharged on Oral Amoxicillin` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | `HIDE` |
| SIMPLE_CONDITIONAL_DISPLAY | `ENROLLED,1` |

---

## CRF 2: B1_RCT2_48H — Items Sheet (16 rows, ALL 27 columns)

> Same format as above — one vertical table per item.

**Row 1 — SUBJID:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `SUBJID` |
| DESCRIPTION_LABEL | `Identification number` |
| LEFT_ITEM_TEXT | `Identification number` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `assessment` |
| GROUP_LABEL | `assess_grp` |
| HEADER | `Subject Identification` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.1` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `subjid` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `ST` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 2 — ASSESSDTC:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `ASSESSDTC` |
| DESCRIPTION_LABEL | `Date of assessment` |
| LEFT_ITEM_TEXT | `Date of assessment` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `assessment` |
| GROUP_LABEL | `assess_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.2` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `assessdtc` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `DATE` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 3 — ASSESSTM:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `ASSESSTM` |
| DESCRIPTION_LABEL | `Time of assessment` |
| LEFT_ITEM_TEXT | `Time of assessment (HH:MM)` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `assessment` |
| GROUP_LABEL | `assess_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.3` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `assesstm` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `ST` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 4 — ASSESSLOC:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `ASSESSLOC` |
| DESCRIPTION_LABEL | `Place of assessment` |
| LEFT_ITEM_TEXT | `Place of assessment` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `assessment` |
| GROUP_LABEL | `assess_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.4` |
| RESPONSE_TYPE | `single-select` |
| RESPONSE_LABEL | `assessloc` |
| RESPONSE_OPTIONS_TEXT | `Hospital,Health Centre,Health Post,Home,Other` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2,3,4,5` |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 5 — TEMP:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `TEMP` |
| DESCRIPTION_LABEL | `Axillary temperature` |
| LEFT_ITEM_TEXT | `Axillary temperature` |
| UNITS | `°C` |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `vitals` |
| GROUP_LABEL | `vitals_grp` |
| HEADER | `Vital Signs` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.5` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `temp` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `REAL` |
| WIDTH_DECIMAL | |
| VALIDATION | `range(34.0, 42.0)` |
| VALIDATION_ERROR_MESSAGE | `Temperature must be between 34.0 and 42.0 °C` |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 6 — RESPRATE:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `RESPRATE` |
| DESCRIPTION_LABEL | `Respiratory rate` |
| LEFT_ITEM_TEXT | `Respiratory rate` |
| UNITS | `breaths/min` |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `vitals` |
| GROUP_LABEL | `vitals_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.6` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `resprate` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | `range(10, 100)` |
| VALIDATION_ERROR_MESSAGE | `Respiratory rate must be between 10 and 100` |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 7 — HEARTRATE:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `HEARTRATE` |
| DESCRIPTION_LABEL | `Heart rate` |
| LEFT_ITEM_TEXT | `Heart rate` |
| UNITS | `beats/min` |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `vitals` |
| GROUP_LABEL | `vitals_grp` |
| HEADER | |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.7` |
| RESPONSE_TYPE | `text` |
| RESPONSE_LABEL | `heartrate` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | `range(60, 220)` |
| VALIDATION_ERROR_MESSAGE | `Heart rate must be between 60 and 220` |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 8 — FEEDDIFF:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `FEEDDIFF` |
| DESCRIPTION_LABEL | `Feeding difficulty` |
| LEFT_ITEM_TEXT | `Feeding difficulty` |
| UNITS | |
| RIGHT_ITEM_TEXT | |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| HEADER | `Clinical Signs` |
| SUBHEADER | |
| PARENT_ITEM | |
| COLUMN_NUMBER | |
| PAGE_NUMBER | |
| QUESTION_NUMBER | `B1.8` |
| RESPONSE_TYPE | `single-select` |
| RESPONSE_LABEL | `feedstatus` |
| RESPONSE_OPTIONS_TEXT | `No difficulty,Some difficulty,Not able to feed at all` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2,3` |
| RESPONSE_LAYOUT | |
| DEFAULT_VALUE | |
| DATA_TYPE | `INT` |
| WIDTH_DECIMAL | |
| VALIDATION | |
| VALIDATION_ERROR_MESSAGE | |
| PHI | `0` |
| REQUIRED | `1` |
| ITEM_DISPLAY_STATUS | |
| SIMPLE_CONDITIONAL_DISPLAY | |

**Row 9 — CHESTIND:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `CHESTIND` |
| DESCRIPTION_LABEL | `Severe chest indrawing` |
| LEFT_ITEM_TEXT | `Severe chest indrawing` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| QUESTION_NUMBER | `B1.9` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `1` |
| *(all other columns)* | *(leave blank)* |

**Row 10 — CONVULS:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `CONVULS` |
| DESCRIPTION_LABEL | `Convulsions observed` |
| LEFT_ITEM_TEXT | `Convulsions observed` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| QUESTION_NUMBER | `B1.10` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `0` |
| *(all other columns)* | *(leave blank)* |

**Row 11 — LETHARGY:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `LETHARGY` |
| DESCRIPTION_LABEL | `Lethargy or unconsciousness` |
| LEFT_ITEM_TEXT | `Lethargy or unconsciousness` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| QUESTION_NUMBER | `B1.11` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `0` |
| *(all other columns)* | *(leave blank)* |

**Row 12 — HYPOTHER:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `HYPOTHER` |
| DESCRIPTION_LABEL | `Hypothermia below 35.5 degrees` |
| LEFT_ITEM_TEXT | `Hypothermia (below 35.5 °C)` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| QUESTION_NUMBER | `B1.12` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `0` |
| *(all other columns)* | *(leave blank)* |

**Row 13 — HYPERTHER:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `HYPERTHER` |
| DESCRIPTION_LABEL | `Hyperthermia 38.0 degrees or above` |
| LEFT_ITEM_TEXT | `Hyperthermia (38.0 °C or above)` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| QUESTION_NUMBER | `B1.13` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `0` |
| *(all other columns)* | *(leave blank)* |

**Row 14 — CRITILL:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `CRITILL` |
| DESCRIPTION_LABEL | `Any critical illness signs present` |
| LEFT_ITEM_TEXT | `Any critical illness signs present` |
| SECTION_LABEL | `signs` |
| GROUP_LABEL | `signs_grp` |
| HEADER | `Overall Assessment` |
| QUESTION_NUMBER | `B1.14` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `1` |
| *(all other columns)* | *(leave blank)* |

**Row 15 — DSCHRG:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `DSCHRG` |
| DESCRIPTION_LABEL | `Infant can be discharged` |
| LEFT_ITEM_TEXT | `Decision: Infant can be discharged` |
| SECTION_LABEL | `decision` |
| GROUP_LABEL | `decision_grp` |
| HEADER | `Management Decision` |
| QUESTION_NUMBER | `B1.15` |
| RESPONSE_TYPE | `radio` |
| RESPONSE_LABEL | `yn` |
| RESPONSE_OPTIONS_TEXT | `Yes,No` |
| RESPONSE_VALUES_OR_CALCULATIONS | `1,2` |
| RESPONSE_LAYOUT | `Horizontal` |
| DATA_TYPE | `INT` |
| PHI | `0` |
| REQUIRED | `1` |
| *(all other columns)* | *(leave blank)* |

**Row 16 — DSCHREASON:**

| Column | Value |
|--------|-------|
| ITEM_NAME | `DSCHREASON` |
| DESCRIPTION_LABEL | `Reason for continued treatment` |
| LEFT_ITEM_TEXT | `If not discharged, reason for continued treatment` |
| SECTION_LABEL | `decision` |
| GROUP_LABEL | `decision_grp` |
| QUESTION_NUMBER | `B1.16` |
| RESPONSE_TYPE | `textarea` |
| RESPONSE_LABEL | `dschreason` |
| RESPONSE_OPTIONS_TEXT | |
| RESPONSE_VALUES_OR_CALCULATIONS | |
| DATA_TYPE | `ST` |
| PHI | `0` |
| REQUIRED | `0` |
| ITEM_DISPLAY_STATUS | `HIDE` |
| SIMPLE_CONDITIONAL_DISPLAY | `DSCHRG,2` |
| *(all other columns)* | *(leave blank)* |

---

## CRF 3: B2_RCT2_TREATMENT — Items Sheet (15 rows)

> For brevity, showing only filled columns. All unlisted columns = leave blank.

**Row 1 — SUBJID:** ITEM_NAME=`SUBJID`, DESCRIPTION_LABEL=`Identification number`, LEFT_ITEM_TEXT=`Identification number`, SECTION_LABEL=`visit_info`, GROUP_LABEL=`visit_grp`, HEADER=`Subject Identification`, QUESTION_NUMBER=`B2.1`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`subjid`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`1`

**Row 2 — DAYNUM:** ITEM_NAME=`DAYNUM`, DESCRIPTION_LABEL=`Visit day number`, LEFT_ITEM_TEXT=`Visit day number`, SECTION_LABEL=`visit_info`, GROUP_LABEL=`visit_grp`, QUESTION_NUMBER=`B2.2`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`visit`, RESPONSE_OPTIONS_TEXT=`Day 2,Day 4,Day 8`, RESPONSE_VALUES_OR_CALCULATIONS=`D2,D4,D8`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`1`

**Row 3 — VISITDTC:** ITEM_NAME=`VISITDTC`, DESCRIPTION_LABEL=`Date of visit`, LEFT_ITEM_TEXT=`Date of visit`, SECTION_LABEL=`visit_info`, GROUP_LABEL=`visit_grp`, QUESTION_NUMBER=`B2.3`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`visitdtc`, DATA_TYPE=`DATE`, PHI=`0`, REQUIRED=`1`

**Row 4 — ASSESSLOC:** ITEM_NAME=`ASSESSLOC`, DESCRIPTION_LABEL=`Place of completing this form`, LEFT_ITEM_TEXT=`Place of completing this form`, SECTION_LABEL=`visit_info`, GROUP_LABEL=`visit_grp`, QUESTION_NUMBER=`B2.4`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`assessloc`, RESPONSE_OPTIONS_TEXT=`Hospital,Health Centre,Health Post,Home,Other`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3,4,5`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 5 — RESPONDENT:** ITEM_NAME=`RESPONDENT`, DESCRIPTION_LABEL=`Adult primary respondent`, LEFT_ITEM_TEXT=`Adult primary respondent present`, SECTION_LABEL=`visit_info`, GROUP_LABEL=`visit_grp`, QUESTION_NUMBER=`B2.5`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`respondent`, RESPONSE_OPTIONS_TEXT=`Mother,Father,Grandmother,Grandfather,Other relative,Other`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3,4,5,6`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`0`

**Row 6 — AMOXGIVEN:** ITEM_NAME=`AMOXGIVEN`, DESCRIPTION_LABEL=`Oral amoxicillin given today`, LEFT_ITEM_TEXT=`Oral amoxicillin given today`, SECTION_LABEL=`treatment`, GROUP_LABEL=`treatment_grp`, HEADER=`Medication Compliance`, QUESTION_NUMBER=`B2.6`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 7 — REMTAB:** ITEM_NAME=`REMTAB`, DESCRIPTION_LABEL=`Remaining tablets or suspension`, LEFT_ITEM_TEXT=`Remaining tablets/suspension (count or mL)`, SECTION_LABEL=`treatment`, GROUP_LABEL=`treatment_grp`, QUESTION_NUMBER=`B2.7`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`remtab`, DATA_TYPE=`REAL`, PHI=`0`, REQUIRED=`0`, VALIDATION=`range(0, 100)`, VALIDATION_ERROR_MESSAGE=`Must be between 0 and 100`

**Row 8 — MISSEDDOSES:** ITEM_NAME=`MISSEDDOSES`, DESCRIPTION_LABEL=`Number of missed doses since last visit`, LEFT_ITEM_TEXT=`Number of missed doses since last visit`, SECTION_LABEL=`treatment`, GROUP_LABEL=`treatment_grp`, QUESTION_NUMBER=`B2.8`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`misseddoses`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`0`, VALIDATION=`range(0, 20)`, VALIDATION_ERROR_MESSAGE=`Must be between 0 and 20`

**Row 9 — OTHABX:** ITEM_NAME=`OTHABX`, DESCRIPTION_LABEL=`Other antibiotic given`, LEFT_ITEM_TEXT=`Other antibiotic given (name)`, SECTION_LABEL=`treatment`, GROUP_LABEL=`treatment_grp`, HEADER=`Additional Medications`, QUESTION_NUMBER=`B2.9`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`othabx`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`

**Row 10 — OTHABXREAS:** ITEM_NAME=`OTHABXREAS`, DESCRIPTION_LABEL=`Reason for other antibiotic`, LEFT_ITEM_TEXT=`Reason for other antibiotic`, SECTION_LABEL=`treatment`, GROUP_LABEL=`treatment_grp`, QUESTION_NUMBER=`B2.10`, RESPONSE_TYPE=`textarea`, RESPONSE_LABEL=`othabxreas`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`

**Row 11 — FEEDSTAT:** ITEM_NAME=`FEEDSTAT`, DESCRIPTION_LABEL=`Feeding status at this visit`, LEFT_ITEM_TEXT=`Feeding status at this visit`, SECTION_LABEL=`status`, GROUP_LABEL=`status_grp`, HEADER=`Clinical Assessment`, QUESTION_NUMBER=`B2.11`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`feedstatus`, RESPONSE_OPTIONS_TEXT=`No difficulty,Some difficulty,Not able to feed at all`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`0`

**Row 12 — TEMP:** ITEM_NAME=`TEMP`, DESCRIPTION_LABEL=`Axillary temperature`, LEFT_ITEM_TEXT=`Axillary temperature`, UNITS=`°C`, SECTION_LABEL=`status`, GROUP_LABEL=`status_grp`, QUESTION_NUMBER=`B2.12`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`temp`, DATA_TYPE=`REAL`, PHI=`0`, REQUIRED=`0`, VALIDATION=`range(34.0, 42.0)`, VALIDATION_ERROR_MESSAGE=`Temperature must be between 34.0 and 42.0 °C`

**Row 13 — IMPROVING:** ITEM_NAME=`IMPROVING`, DESCRIPTION_LABEL=`Clinical condition improving`, LEFT_ITEM_TEXT=`Clinical condition improving`, SECTION_LABEL=`status`, GROUP_LABEL=`status_grp`, QUESTION_NUMBER=`B2.13`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`0`

**Row 14 — HOSPREF:** ITEM_NAME=`HOSPREF`, DESCRIPTION_LABEL=`Referred or readmitted to hospital`, LEFT_ITEM_TEXT=`Referred/readmitted to hospital`, SECTION_LABEL=`status`, GROUP_LABEL=`status_grp`, QUESTION_NUMBER=`B2.14`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`0`

**Row 15 — HOSPREFREAS:** ITEM_NAME=`HOSPREFREAS`, DESCRIPTION_LABEL=`Reason for referral`, LEFT_ITEM_TEXT=`If referred, reason for referral`, SECTION_LABEL=`status`, GROUP_LABEL=`status_grp`, QUESTION_NUMBER=`B2.15`, RESPONSE_TYPE=`textarea`, RESPONSE_LABEL=`hosprefreas`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`, ITEM_DISPLAY_STATUS=`HIDE`, SIMPLE_CONDITIONAL_DISPLAY=`HOSPREF,1`

---

## CRF 4: C1_SAE — Items Sheet (21 rows)

> Same compact format. All unlisted columns = leave blank.

**Row 1 — SUBJID:** ITEM_NAME=`SUBJID`, DESCRIPTION_LABEL=`Identification number of the young infant`, LEFT_ITEM_TEXT=`Identification number of the young infant`, SECTION_LABEL=`sae_id`, GROUP_LABEL=`sae_id_grp`, HEADER=`Subject Identification`, QUESTION_NUMBER=`C1.1`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`subjid`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`1`

**Row 2 — SAERPTDTC:** ITEM_NAME=`SAERPTDTC`, DESCRIPTION_LABEL=`Date of filling this SAE form`, LEFT_ITEM_TEXT=`Date of filling this SAE form`, SECTION_LABEL=`sae_id`, GROUP_LABEL=`sae_id_grp`, QUESTION_NUMBER=`C1.2`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`saerptdtc`, DATA_TYPE=`DATE`, PHI=`0`, REQUIRED=`1`

**Row 3 — SAERPTNUM:** ITEM_NAME=`SAERPTNUM`, DESCRIPTION_LABEL=`SAE report number for this subject`, LEFT_ITEM_TEXT=`SAE report number (for this subject)`, SECTION_LABEL=`sae_id`, GROUP_LABEL=`sae_id_grp`, QUESTION_NUMBER=`C1.3`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`saerptnum`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`, VALIDATION=`range(1, 99)`, VALIDATION_ERROR_MESSAGE=`Must be between 1 and 99`

**Row 4 — ANAPHYL:** ITEM_NAME=`ANAPHYL`, DESCRIPTION_LABEL=`Anaphylactic reaction`, LEFT_ITEM_TEXT=`Anaphylactic reaction`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, HEADER=`Adverse Event Types`, QUESTION_NUMBER=`C1.4`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 5 — ALLERGIC:** ITEM_NAME=`ALLERGIC`, DESCRIPTION_LABEL=`Other allergic reaction or rash`, LEFT_ITEM_TEXT=`Other allergic reaction / rash`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.5`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 6 — INJSITE:** ITEM_NAME=`INJSITE`, DESCRIPTION_LABEL=`Injection site infection or abscess`, LEFT_ITEM_TEXT=`Injection site infection / abscess`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.6`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 7 — DIARRHEA:** ITEM_NAME=`DIARRHEA`, DESCRIPTION_LABEL=`Diarrhoea with severe dehydration`, LEFT_ITEM_TEXT=`Diarrhoea with severe dehydration`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.7`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 8 — AESLIFE:** ITEM_NAME=`AESLIFE`, DESCRIPTION_LABEL=`Life-threatening adverse event`, LEFT_ITEM_TEXT=`Life-threatening adverse event`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.8`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 9 — AESDEATH:** ITEM_NAME=`AESDEATH`, DESCRIPTION_LABEL=`Death`, LEFT_ITEM_TEXT=`Death`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.9`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 10 — AEOTHER:** ITEM_NAME=`AEOTHER`, DESCRIPTION_LABEL=`Other serious adverse event`, LEFT_ITEM_TEXT=`Other serious adverse event`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.10`, RESPONSE_TYPE=`radio`, RESPONSE_LABEL=`yn`, RESPONSE_OPTIONS_TEXT=`Yes,No`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2`, RESPONSE_LAYOUT=`Horizontal`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 11 — AEOTHERSP:** ITEM_NAME=`AEOTHERSP`, DESCRIPTION_LABEL=`If other specify`, LEFT_ITEM_TEXT=`If other, specify`, SECTION_LABEL=`sae_type`, GROUP_LABEL=`sae_type_grp`, QUESTION_NUMBER=`C1.10a`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`aeothersp`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`, ITEM_DISPLAY_STATUS=`HIDE`, SIMPLE_CONDITIONAL_DISPLAY=`AEOTHER,1`

**Row 12 — AESTDTC:** ITEM_NAME=`AESTDTC`, DESCRIPTION_LABEL=`Date of onset of the adverse event`, LEFT_ITEM_TEXT=`Date of onset of the adverse event`, SECTION_LABEL=`sae_dates`, GROUP_LABEL=`sae_dates_grp`, HEADER=`Event Timeline`, QUESTION_NUMBER=`C1.11`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`aestdtc`, DATA_TYPE=`DATE`, PHI=`0`, REQUIRED=`1`

**Row 13 — AEENDTC:** ITEM_NAME=`AEENDTC`, DESCRIPTION_LABEL=`Date of resolution`, LEFT_ITEM_TEXT=`Date of resolution (leave blank if ongoing)`, SECTION_LABEL=`sae_dates`, GROUP_LABEL=`sae_dates_grp`, QUESTION_NUMBER=`C1.12`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`aeendtc`, DATA_TYPE=`DATE`, PHI=`0`, REQUIRED=`0`

**Row 14 — AEREL:** ITEM_NAME=`AEREL`, DESCRIPTION_LABEL=`Relationship to study treatment`, LEFT_ITEM_TEXT=`Relationship to study treatment`, SECTION_LABEL=`sae_dates`, GROUP_LABEL=`sae_dates_grp`, HEADER=`Causality Assessment`, QUESTION_NUMBER=`C1.13`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`aerel`, RESPONSE_OPTIONS_TEXT=`Not related,Unlikely,Possible,Probable,Definite`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3,4,5`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 15 — AEACN:** ITEM_NAME=`AEACN`, DESCRIPTION_LABEL=`Action taken with study drug`, LEFT_ITEM_TEXT=`Action taken with study drug`, SECTION_LABEL=`sae_outcome`, GROUP_LABEL=`sae_outcome_grp`, HEADER=`Action and Outcome`, QUESTION_NUMBER=`C1.14`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`aeacn`, RESPONSE_OPTIONS_TEXT=`Drug withdrawn,Drug interrupted,Dose reduced,Dose not changed,Not applicable,Unknown`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3,4,5,6`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 16 — AEOUT:** ITEM_NAME=`AEOUT`, DESCRIPTION_LABEL=`Outcome of the adverse event`, LEFT_ITEM_TEXT=`Outcome of the adverse event`, SECTION_LABEL=`sae_outcome`, GROUP_LABEL=`sae_outcome_grp`, QUESTION_NUMBER=`C1.15`, RESPONSE_TYPE=`single-select`, RESPONSE_LABEL=`aeout`, RESPONSE_OPTIONS_TEXT=`Recovered,Recovering,Not recovered,Fatal,Unknown`, RESPONSE_VALUES_OR_CALCULATIONS=`1,2,3,4,5`, DATA_TYPE=`INT`, PHI=`0`, REQUIRED=`1`

**Row 17 — DTHDTC:** ITEM_NAME=`DTHDTC`, DESCRIPTION_LABEL=`Date of death if fatal`, LEFT_ITEM_TEXT=`If fatal — date of death`, SECTION_LABEL=`sae_outcome`, GROUP_LABEL=`sae_outcome_grp`, QUESTION_NUMBER=`C1.16`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`dthdtc`, DATA_TYPE=`DATE`, PHI=`1`, REQUIRED=`0`, ITEM_DISPLAY_STATUS=`HIDE`, SIMPLE_CONDITIONAL_DISPLAY=`AESDEATH,1`

**Row 18 — DTHCAUSE:** ITEM_NAME=`DTHCAUSE`, DESCRIPTION_LABEL=`Primary cause of death if fatal`, LEFT_ITEM_TEXT=`If fatal — primary cause of death`, SECTION_LABEL=`sae_outcome`, GROUP_LABEL=`sae_outcome_grp`, QUESTION_NUMBER=`C1.17`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`dthcause`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`, ITEM_DISPLAY_STATUS=`HIDE`, SIMPLE_CONDITIONAL_DISPLAY=`AESDEATH,1`

**Row 19 — SAEDESC:** ITEM_NAME=`SAEDESC`, DESCRIPTION_LABEL=`Detailed description of the SAE`, LEFT_ITEM_TEXT=`Detailed description of the SAE / death`, SECTION_LABEL=`sae_narrative`, GROUP_LABEL=`sae_narrative_grp`, HEADER=`Clinical Narrative`, QUESTION_NUMBER=`C1.18`, RESPONSE_TYPE=`textarea`, RESPONSE_LABEL=`saedesc`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`1`

**Row 20 — SAETRT:** ITEM_NAME=`SAETRT`, DESCRIPTION_LABEL=`Treatment given for the SAE`, LEFT_ITEM_TEXT=`Treatment given for the SAE`, SECTION_LABEL=`sae_narrative`, GROUP_LABEL=`sae_narrative_grp`, QUESTION_NUMBER=`C1.19`, RESPONSE_TYPE=`textarea`, RESPONSE_LABEL=`saetrt`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`0`

**Row 21 — RPTNAME:** ITEM_NAME=`RPTNAME`, DESCRIPTION_LABEL=`Name of person completing this report`, LEFT_ITEM_TEXT=`Name of person completing this report`, SECTION_LABEL=`sae_narrative`, GROUP_LABEL=`sae_narrative_grp`, HEADER=`Reporter Information`, QUESTION_NUMBER=`C1.20`, RESPONSE_TYPE=`text`, RESPONSE_LABEL=`rptname`, DATA_TYPE=`ST`, PHI=`0`, REQUIRED=`1`

---

## Upload Steps (After Filling All 4 Files)

1. Login to OpenClinica → **Tasks** → **Build Study**
2. Click **➕** next to "Create CRF"
3. Select **"Create a New CRF Version"** (not manual build)
4. Browse to `A1_SCREEN_ENROLL_v1.0.xls` → Click **Upload**
5. OpenClinica previews the CRF → Review it → Click **Submit**
6. ✅ CRF created! Repeat for the other 3 files.

## Upload Order

```
1. A1_SCREEN_ENROLL_v1.0.xls    → 18 items
2. B1_RCT2_48H_v1.0.xls         → 16 items
3. B2_RCT2_TREATMENT_v1.0.xls   → 15 items
4. C1_SAE_v1.0.xls               → 21 items
                                   ─────────
                          Total:   70 items
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `SECTION_LABEL not found` | Item references a section that doesn't exist in Sections sheet | Check spelling matches exactly |
| `GROUP_LABEL not found` | Item references a group that doesn't exist in Groups sheet | Check spelling matches exactly |
| `Duplicate RESPONSE_LABEL with different options` | Two items use same RESPONSE_LABEL but different options | All items with `yn` must use exactly `Yes,No` and `1,2` |
| `ITEM_NAME already exists` | Same item name used twice | Each ITEM_NAME must be unique within a CRF |
| `Invalid DATA_TYPE` | Wrong code | Use only: `ST`, `INT`, `REAL`, `DATE`, `PDATE`, `FILE` |
| `DESCRIPTION_LABEL is blank` | Missing required column | Must provide a description for every item |
| `RESPONSE_LABEL is blank` | Missing required column | Must provide for every item (item name lowercase for text, codelist name for radio/select) |
