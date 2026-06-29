# Mobile EDC — End-to-End Testing Guide

> Complete testing guide for the HACT CTMS Mobile EDC feature.
> Covers: backend setup, API testing, frontend testing, offline testing, and all 6 industry-standard features.

---

## Table of Contents

1. [Prerequisites & Setup](#1-prerequisites--setup)
2. [Backend Setup & Migration](#2-backend-setup--migration)
3. [Backend API Testing (with curl/Swagger)](#3-backend-api-testing)
4. [Frontend Testing (Browser)](#4-frontend-testing)
5. [Testing the 6 Industry Gaps](#5-testing-the-6-industry-gaps)
6. [Offline Testing](#6-offline-testing)
7. [End-to-End Flow](#7-end-to-end-flow)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites & Setup

### What You Need Running

| Service | URL | Purpose |
|---------|-----|---------|
| **Django API** | `http://localhost:8000` | Backend REST API |
| **React Frontend** | `http://localhost:5173` | Frontend SPA |
| **PostgreSQL** | `localhost:5432` | Database |
| **Keycloak** | `http://localhost:8080` | SSO Authentication |

### Quick Start Commands

```bash
# Terminal 1: Start backend
cd backend
docker compose up -d  # or: python manage.py runserver

# Terminal 2: Start frontend
cd frontend
npm run dev
```

---

## 2. Backend Setup & Migration

### Step 1: Generate and Apply Migration

The new models (VisitForm, ItemResponseAudit) and new fields (display_condition, cross_field_validation, section, submission_uuid) need a database migration.

```bash
cd backend

# Generate migration
python manage.py makemigrations clinical --name="edc_skip_logic_audit_trail_visit_form"

# Apply migration
python manage.py migrate
```

> [!IMPORTANT]
> If you get migration errors, check that `models.py` has no syntax issues:
> ```bash
> python -c "from clinical.models import VisitForm, ItemResponseAudit; print('OK')"
> ```

### Step 2: Create Test Data via Django Admin

Open `http://localhost:8000/admin/` and create:

#### A. Study
| Field | Value |
|-------|-------|
| Protocol Number | `PSBI-2026-001` |
| Name | `PSBI Neonatal Sepsis Trial` |
| Phase | `Phase III` |
| Status | `active` |
| Start Date | `2026-06-01` |

#### B. Site
| Field | Value |
|-------|-------|
| Study | `PSBI-2026-001` |
| Site Code | `ETH-ADM-001` |
| Name | `Addis Ababa Medical Center` |
| Country | `Ethiopia` |
| Status | `active` |

#### C. Visits (create 4)

| Visit Name | Visit Order | Planned Day | Is Screening |
|-----------|-------------|-------------|-------------|
| Screening & Enrollment | 1 | 0 | ✅ Yes |
| 48-Hour Assessment | 2 | 2 | No |
| Day 4 Treatment | 3 | 4 | No |
| Day 8 Follow-up | 4 | 8 | No |

#### D. Forms (create 2 CRFs)

**Form 1: Screening CRF**

| Field | Value |
|-------|-------|
| Study | `PSBI-2026-001` |
| Name | `A1 Screening & Enrollment` |
| Version | `1.0` |
| Is Active | ✅ |

**Form 2: 48h Assessment CRF**

| Field | Value |
|-------|-------|
| Study | `PSBI-2026-001` |
| Name | `B1 48-Hour Assessment` |
| Version | `1.0` |
| Is Active | ✅ |

#### E. Items for Form 1 (Screening CRF) — with skip logic!

Create these Items in Django Admin under the "A1 Screening & Enrollment" form:

| # | field_name | field_label | field_type | required | section | order | options | display_condition | validation_rule | cross_field_validation |
|---|-----------|-------------|-----------|----------|---------|-------|---------|-------------------|-----------------|----------------------|
| 1 | `SCREEN_DATE` | Screening Date | `date` | ✅ | `Screening` | 1 | — | — | — | — |
| 2 | `BIRTH_DATE` | Date of Birth | `date` | ✅ | `Demographics` | 2 | — | — | — | — |
| 3 | `SEX` | Sex | `radio` | ✅ | `Demographics` | 3 | `[{"value":"1","label":"Male"},{"value":"2","label":"Female"}]` | — | — | — |
| 4 | `WEIGHT` | Weight (kg) | `number` | ✅ | `Vitals` | 4 | — | — | `range(0.5, 10.0)` | — |
| 5 | `TEMP` | Temperature (°C) | `number` | ✅ | `Vitals` | 5 | — | — | `range(34.0, 42.0)` | — |
| 6 | `FEEDING` | Feeding Difficulty | `radio` | ✅ | `Clinical Signs` | 6 | `[{"value":"0","label":"No difficulty"},{"value":"1","label":"Some difficulty"},{"value":"2","label":"Not able to feed"}]` | — | — | — |
| 7 | `CHEST_INDRAW` | Chest Indrawing | `radio` | ✅ | `Clinical Signs` | 7 | `[{"value":"0","label":"No"},{"value":"1","label":"Yes"}]` | — | — | — |
| 8 | `ELIGIBLE` | Eligible for Enrollment? | `radio` | ✅ | `Eligibility` | 8 | `[{"value":"1","label":"Yes"},{"value":"0","label":"No"}]` | — | — | — |
| 9 | `ENROLLED` | Enrolled? | `radio` | ✅ | `Enrollment` | 9 | `[{"value":"1","label":"Yes"},{"value":"0","label":"No"}]` | `{"field":"ELIGIBLE","operator":"eq","value":"1"}` | — | — |
| 10 | `ENROLL_DATE` | Date of Enrollment | `date` | ✅ | `Enrollment` | 10 | — | `{"field":"ENROLLED","operator":"eq","value":"1"}` | — | `{"gte":"SCREEN_DATE","message":"Enrollment date must be on or after screening date"}` |
| 11 | `CONSENT_PHOTO` | Photo of Signed Consent Form | `file` | No | `Enrollment` | 11 | — | `{"field":"ENROLLED","operator":"eq","value":"1"}` | — | — |

> [!TIP]
> **Items 9, 10, and 11 have skip logic!**
> - Item 9 (`ENROLLED`) only shows when `ELIGIBLE = "1"` (Yes)
> - Item 10 (`ENROLL_DATE`) only shows when `ENROLLED = "1"` (Yes)
> - Item 11 (`CONSENT_PHOTO`) only shows when `ENROLLED = "1"` (Yes)
> - Item 10 has **cross-field validation**: enrollment date must be ≥ screening date

#### F. Items for Form 2 (48h Assessment)

| # | field_name | field_label | field_type | required | section | order | options | validation_rule |
|---|-----------|-------------|-----------|----------|---------|-------|---------|-----------------|
| 1 | `ASSESS_DATE` | Assessment Date | `date` | ✅ | `Assessment` | 1 | — | — |
| 2 | `TEMP_48H` | Temperature (°C) | `number` | ✅ | `Vitals` | 2 | — | `range(34.0, 42.0)` |
| 3 | `FEEDING_48H` | Feeding Difficulty | `radio` | ✅ | `Clinical Signs` | 3 | `[{"value":"0","label":"Improved"},{"value":"1","label":"Same"},{"value":"2","label":"Worse"}]` | — |
| 4 | `NOTES` | Clinical Notes | `textarea` | No | `Notes` | 4 | — | — |

#### G. VisitForm Mappings (Form-to-Visit)

In Django Admin → **Visit-Form Mappings**, create:

| Visit | Form | Is Required |
|-------|------|-------------|
| Screening & Enrollment | A1 Screening & Enrollment | ✅ Yes |
| 48-Hour Assessment | B1 48-Hour Assessment | ✅ Yes |

> [!IMPORTANT]
> Without these mappings, ALL forms show at every visit. With mappings, only the correct forms appear.

---

## 3. Backend API Testing

### Get an Auth Token

```bash
# Option A: Get token from Keycloak
TOKEN=$(curl -s -X POST "http://localhost:8080/auth/realms/hact/protocol/openid-connect/token" \
  -d "grant_type=password" \
  -d "client_id=hact-ctms-frontend" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD" | jq -r '.access_token')

echo $TOKEN
```

### Test EDC Endpoints

```bash
BASE="http://localhost:8000/api/v1"

# 1. List subjects
curl -H "Authorization: Bearer $TOKEN" "$BASE/edc/subjects/"

# 2. Enroll a new subject
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$BASE/edc/enroll/" \
  -d '{
    "study_id": 1,
    "site_id": 1,
    "subject_identifier": "ETH-ADM-001-0001",
    "screening_number": "SCR-0001",
    "consent_signed_date": "2026-06-15",
    "enrollment_date": "2026-06-15"
  }'

# 3. Get form schema (with skip logic fields)
curl -H "Authorization: Bearer $TOKEN" "$BASE/edc/forms/1/schema/"
# → Should include: display_condition, cross_field_validation, section

# 4. Get forms for a visit (tests form-visit mapping)
curl -H "Authorization: Bearer $TOKEN" "$BASE/edc/subjects/1/visits/1/forms/"
# → Should show ONLY the Screening CRF (not the 48h Assessment)

# 5. Submit a CRF
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$BASE/edc/submit/" \
  -d '{
    "form_id": 1,
    "subject_id": 1,
    "subject_visit_id": 1,
    "status": "submitted",
    "e_signature_password": "YOUR_PASSWORD",
    "responses": [
      {"item_id": 1, "value": "2026-06-15"},
      {"item_id": 2, "value": "2026-06-10"},
      {"item_id": 3, "value": "1"},
      {"item_id": 4, "value": "3.2"},
      {"item_id": 5, "value": "37.1"},
      {"item_id": 6, "value": "0"},
      {"item_id": 7, "value": "0"},
      {"item_id": 8, "value": "1"},
      {"item_id": 9, "value": "1"},
      {"item_id": 10, "value": "2026-06-15"}
    ]
  }'

# 6. Edit the submitted CRF (with reason for change)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$BASE/edc/submit/" \
  -d '{
    "form_id": 1,
    "subject_id": 1,
    "subject_visit_id": 1,
    "status": "submitted",
    "reason_for_change": "Corrected temperature reading",
    "e_signature_password": "YOUR_PASSWORD",
    "responses": [
      {"item_id": 5, "value": "37.5"}
    ]
  }'

# 7. Verify e-signature
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$BASE/edc/verify-signature/" \
  -d '{"password": "YOUR_PASSWORD"}'
# → {"valid": true}

# 8. Check audit trail (in Django Admin)
# Go to: http://localhost:8000/admin/clinical/itemresponseaudit/
# → Should see the temperature change: "37.1" → "37.5" with reason
```

### Expected API Response Structure

**GET /edc/forms/1/schema/** (note the skip logic fields):
```json
{
  "id": 1,
  "name": "A1 Screening & Enrollment",
  "version": "1.0",
  "items": [
    {
      "id": 9,
      "field_name": "ENROLLED",
      "field_label": "Enrolled?",
      "field_type": "radio",
      "required": true,
      "section": "Enrollment",
      "display_condition": {"field": "ELIGIBLE", "operator": "eq", "value": "1"},
      "cross_field_validation": null,
      "options": [{"value": "1", "label": "Yes"}, {"value": "0", "label": "No"}]
    },
    {
      "id": 10,
      "field_name": "ENROLL_DATE",
      "display_condition": {"field": "ENROLLED", "operator": "eq", "value": "1"},
      "cross_field_validation": {"gte": "SCREEN_DATE", "message": "Enrollment date must be on or after screening date"}
    }
  ]
}
```

---

## 4. Frontend Testing

### Open Mobile EDC

1. Open Chrome → **http://localhost:5173/edc**
2. Chrome DevTools → **Toggle device toolbar** (Ctrl+Shift+M)
3. Select device: **iPhone 14** or **Samsung Galaxy S20**
4. Login with your Keycloak credentials

### What You Should See

| Screen | URL | Expected |
|--------|-----|----------|
| Subject List | `/edc` | Search bar, status tabs, floating + button |
| Enroll Subject | `/edc/enroll` | Study/site dropdowns, subject ID, dates |
| Visit Schedule | `/edc/subject/1` | Timeline with color-coded visits |
| Visit Forms | `/edc/subject/1/visit/1/forms` | Only mapped CRFs (not all) |
| CRF Form | `/edc/subject/1/visit/1/form/1` | Dynamic form with sections |
| Sync Status | `/edc/sync` | Pending queue + history |

### UI Checklist

- [ ] **No sidebar** — only the slim header bar with logo, sync, user, logout
- [ ] **Bottom status bar** — shows Online/Offline + pending sync count
- [ ] **Touch targets** — buttons are at least 48px tall (finger-friendly)
- [ ] **Search** — type a subject ID and results filter instantly
- [ ] **Status tabs** — All / Enrolled / Screened / Completed filter works
- [ ] **Floating + button** — visible on subject list, opens enrollment form
- [ ] **Visit timeline** — completed visits green, planned amber, with dot + line
- [ ] **Progress bar** — shows completion % in CRF form header
- [ ] **Section headers** — fields grouped by section (Demographics, Vitals, etc.)

---

## 5. Testing the 6 Industry Gaps

### Gap 1: Skip Logic / Conditional Display ⭐

This is the most visible feature. On the Screening CRF:

1. Open the Screening CRF form
2. Fill fields 1-7 normally
3. At field 8 **"Eligible for Enrollment?"**:
   - Select **"No"** → Fields 9, 10, 11 should be **HIDDEN**
   - Select **"Yes"** → Fields 9, 10, 11 should **APPEAR**
4. At field 9 **"Enrolled?"**:
   - Select **"No"** → Fields 10, 11 should be **HIDDEN**
   - Select **"Yes"** → Fields 10, 11 should **APPEAR**

> [!TIP]
> The progress bar should update dynamically — when fields are hidden, they don't count toward the total.

### Gap 2: Edit Existing CRFs

1. Submit a CRF successfully (Screening CRF)
2. Go back to the visit → tap the same form
3. The form should **pre-fill with existing values**
4. The header should show **"· Editing"** indicator
5. Change a value (e.g., change Temperature from 37.1 to 37.5)
6. The **"Reason for Change"** modal should appear
7. Enter a reason (e.g., "Corrected reading") → Continue
8. E-Signature modal appears → enter password → Sign & Submit
9. Check Django Admin → **Item Response Audit** table should show:
   - Old Value: `37.1`
   - New Value: `37.5`
   - Reason: `Corrected reading`
   - Changed By: your username
   - Changed At: timestamp

### Gap 3: E-Signature (21 CFR Part 11)

1. Fill out a CRF completely
2. Tap **"Submit CRF"** button
3. **E-Signature modal** should appear with:
   - Shield icon
   - "21 CFR Part 11 Compliance" subtitle
   - Legal text about certifying data accuracy
   - Password input field
   - "Cancel" and "Sign & Submit" buttons
4. Enter **wrong password** → error message "Incorrect password"
5. Enter **correct password** → CRF submits successfully
6. Check Django Admin → FormInstance should have:
   - `signed_by` = your user
   - `signed_at` = timestamp

### Gap 4: Audit Trail

After editing a submitted CRF:

1. Go to Django Admin → **Item Response Audit** (`/admin/clinical/itemresponseaudit/`)
2. Verify each changed field has an audit entry:
   - `item_response` → links to the field
   - `old_value` → what it was before
   - `new_value` → what it was changed to
   - `reason_for_change` → what the CRC entered
   - `changed_by` → who changed it
   - `changed_at` → when

3. Even initial submissions should have audit entries with:
   - `old_value` = "" (empty)
   - `new_value` = the entered value
   - `reason_for_change` = "Initial entry"

### Gap 5: Cross-Field Validation

1. Open the Screening CRF
2. Set `SCREEN_DATE` = **2026-06-15**
3. Set `ELIGIBLE` = Yes, `ENROLLED` = Yes
4. Set `ENROLL_DATE` = **2026-06-10** (BEFORE the screening date)
5. Tap **Submit CRF**
6. Should show validation error: **"Enrollment date must be on or after screening date"**
7. Fix `ENROLL_DATE` to **2026-06-15** → should validate successfully

### Gap 6: Form-to-Visit Mapping

1. Create VisitForm mappings in Django Admin (as described in setup)
2. Go to EDC → Subject → Visit Schedule
3. Tap **"Screening & Enrollment"** visit
   - Should show ONLY **"A1 Screening & Enrollment"** form
   - Should NOT show "B1 48-Hour Assessment"
4. Tap **"48-Hour Assessment"** visit
   - Should show ONLY **"B1 48-Hour Assessment"** form
   - Should NOT show "A1 Screening & Enrollment"

---

## 6. Offline Testing

### Step 1: Enable Offline Mode

1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Check **"Offline"** checkbox ✅
4. The bottom status bar should change: 🔴 **"Offline — data saved locally"**

### Step 2: Fill CRF While Offline

1. Navigate to a subject → visit → CRF form (if already cached)
2. Fill out all fields
3. Tap **"Submit CRF"**
4. Should show toast: **"Saved offline — will sync when online"** 📱
5. The bottom bar should show: **"1 pending sync"**

### Step 3: Go Back Online

1. Uncheck **"Offline"** in DevTools
2. The status bar should change to: 🟢 **"Online"**
3. The pending submission should **auto-sync** within seconds
4. The pending count should go to 0
5. Toast: **"CRF submitted successfully!"**

### Step 4: Check Sync Status Page

1. Navigate to sync status (via the sync button in the header)
2. Should show:
   - **Pending Queue**: 0 (all synced)
   - **Recent Submissions**: the form you just synced
   - **Last sync**: timestamp

### Step 5: Test Conflict Scenario

1. Go offline → submit CRF for Visit 2
2. Meanwhile, open another browser → submit CRF for the same visit
3. Go back online on the first browser
4. The sync should either succeed (if no conflict) or show a sync error

---

## 7. End-to-End Flow

Complete this flow as a CRC would in the field:

```
1. Open phone browser → https://localhost:5173/edc
2. Login with Keycloak credentials
3. See empty subject list
4. Tap (+) → Enroll a new subject:
   - Select study: PSBI-2026-001
   - Select site: ETH-ADM-001
   - Subject ID: ETH-ADM-001-0001
   - Consent date: today
   - Enrollment date: today
   → Tap "Enroll Subject"
5. Automatically navigate to the subject's visit schedule
6. See 4 visits: Screening (Due), 48h (Future), Day 4 (Future), Day 8 (Future)
7. Tap "Screening & Enrollment" → see only the Screening CRF
8. Tap the Screening CRF → fill all fields:
   - Screening date: today
   - DOB: 2026-06-10
   - Sex: Male
   - Weight: 3.2 kg
   - Temperature: 37.1°C
   - Feeding: No difficulty
   - Chest indrawing: No
   - Eligible: Yes → "Enrolled?" field appears (SKIP LOGIC!)
   - Enrolled: Yes → "Enrollment Date" + "Consent Photo" appear (SKIP LOGIC!)
   - Enrollment date: today
   - (optional) Take a consent photo
9. Tap "Submit CRF"
10. E-Signature modal appears → enter password → "Sign & Submit"
11. See success: "CRF Submitted ✅"
12. Tap "Back to Visits"
13. Screening visit should now show "Completed" ✅
14. Tap "48-Hour Assessment" visit → see only the 48h CRF
15. Fill and submit the 48h Assessment CRF
16. Done! ✅
```

### Verify in Django Admin

After the flow, check:

| Admin Page | What to Verify |
|------------|---------------|
| `/admin/clinical/subject/` | New subject `ETH-ADM-001-0001` with status `enrolled` |
| `/admin/clinical/subjectvisit/` | 4 visits created, Screening = `completed` |
| `/admin/clinical/forminstance/` | 2 form instances: Screening (submitted), 48h (submitted) |
| `/admin/clinical/itemresponse/` | All field values stored |
| `/admin/clinical/itemresponseaudit/` | Audit trail entries for every field |

---

## 8. Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `/edc` shows blank page | React route not matched | Check `App.jsx` has EdcLayout routes |
| "401 Unauthorized" on API | Token expired | Re-login via Keycloak |
| Form schema returns empty items | Items not created in admin | Create Items for the Form in Django Admin |
| Skip logic fields don't hide/show | `display_condition` not set on Item | Check JSON in Django Admin Item page |
| E-signature always fails | User doesn't have Django password | Set password: `python manage.py changepassword username` |
| Migration error | Model field conflict | Run `python manage.py makemigrations --merge` |
| Offline sync fails | UUID conflict | Clear IndexedDB: DevTools → Application → IndexedDB → Delete `hact_edc_offline` |
| All forms show at every visit | No VisitForm mappings | Create VisitForm entries in Django Admin |
| Cross-field validation doesn't work | `cross_field_validation` JSON syntax wrong | Must be: `{"gte": "FIELD_NAME", "message": "..."}` |

### How to Reset Test Data

```bash
# In Django shell
python manage.py shell
>>> from clinical.models import *
>>> FormInstance.objects.all().delete()
>>> ItemResponse.objects.all().delete()
>>> ItemResponseAudit.objects.all().delete()
>>> SubjectVisit.objects.all().delete()
>>> Subject.objects.all().delete()
>>> print("Clean slate!")
```

### How to Clear IndexedDB (Offline Cache)

1. Chrome DevTools → **Application** tab
2. Left panel → **IndexedDB** → `hact_edc_offline`
3. Right-click → **Delete database**
4. Refresh the page

---

> [!NOTE]
> **For production deployment**, remember to:
> - Run `python manage.py migrate` on the server
> - Set up VisitForm mappings for each study's visit-CRF relationships
> - Create proper Keycloak users with the `site_coordinator` role for CRCs
> - CRCs bookmark `https://your-domain/edc` on their phones
