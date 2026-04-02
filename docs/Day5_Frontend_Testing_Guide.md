# HACT CTMS — Frontend Testing Guide (Day 5)

## Prerequisites

Before testing, ensure these services are running:

### 1. Backend Docker Stack
```bash
# In project root
docker compose up -d

# Verify all containers are healthy
docker compose ps
```

You should see these running:
- `hact-django-api` (port 8000)
- `hact-keycloak` (port 8080)
- `hact-postgres` (port 5432)
- `hact-redis` (port 6379)
- `hact-nginx` (port 80)

### 2. Frontend Dev Server
```bash
cd frontend
npm run dev
```
Running at **http://localhost:5173**

> [!IMPORTANT]
> The frontend proxies `/api/*` and `/auth/*` to `http://localhost:80` (NGINX).
> If Docker is not running, API calls will fail with network errors.

---

## Test 1: Login Page

**URL:** http://localhost:5173/login

**Expected:**
- ✅ Dark gradient background with dot pattern
- ✅ HACT CTMS shield logo
- ✅ "Sign in to your account" card with glassmorphism
- ✅ Username and Password fields with icons
- ✅ "Sign in" button in indigo/purple
- ✅ Footer: "Horn of Africa Clinical Trials — ICH-GCP Compliant"

**Test Login:**
1. Enter username: `hact-user` (or any Keycloak user)
2. Enter password: (the password you set in Keycloak)
3. Click "Sign in"
4. **Expected:** Redirect to Dashboard (`/`)
5. **On failure:** Red error banner with Keycloak error message

**Test Invalid Login:**
1. Type wrong password → click Sign in
2. **Expected:** Error message: "Login failed. Check your credentials."

---

## Test 2: Dashboard Page

**URL:** http://localhost:5173/ (after login)

**Expected Layout:**
- ✅ Dark sidebar on the left (w-64) with navigation groups
- ✅ Light top bar with search, notification bell, user avatar + name
- ✅ Content area to the right

**Expected Content:**
- ✅ "Welcome back, [Name]" heading
- ✅ 5 stat cards in a row (gradient backgrounds):
  - Active Studies (indigo)
  - Subjects (sky blue)
  - Open Queries (red if >0, green if 0)
  - Adverse Events (amber)
  - Enrollment Rate (green, as %)
- ✅ 2 charts:
  - Enrollment by Study (bar chart)
  - Subject Status Distribution (donut/pie chart)
- ✅ Recent Studies table (top 5)

> [!NOTE]
> If data is empty, you'll see "No study data available" text in chart areas.

---

## Test 3: Studies Page

**URL:** http://localhost:5173/studies

**Test List:**
- ✅ "Studies" heading with count
- ✅ "New Study" blue button (top right)
- ✅ Search box (search by protocol or name)
- ✅ Status dropdown filter (All/Planning/Active/Locked/Archived)
- ✅ Table columns: Protocol, Study Name, Phase, Sponsor, Status, Sites, Subjects, Enrolled
- ✅ Status badges with correct colors (planning=sky, active=green, locked=amber)
- ✅ Protocol number is a clickable link → opens study detail

**Test Create:**
1. Click "New Study"
2. Fill in: Protocol `HACT-2026-TEST`, Name `Test Study`, Phase `III`, Sponsor `HACT`
3. Click "Create Study"
4. **Expected:** Toast "Study created successfully!", modal closes, table refreshes

**Test Search/Filter:**
1. Type "HACT" in search → table filters
2. Select "Active" from dropdown → only active studies shown

**Test Pagination:**
- If >25 studies, "Page 1 of N" with Previous/Next buttons

---

## Test 4: Study Detail Page

**URL:** http://localhost:5173/studies/{id} (click a protocol link)

**Expected:**
- ✅ "← Back to Studies" link
- ✅ Protocol number as heading, study name as subtitle
- ✅ Status badge + "Move to [next status]" button
- ✅ 4 metric cards: Phase, Sites, Subjects, Enrolled
- ✅ Info row: Sponsor, Start Date, Open Queries
- ✅ Sites table (Code, Name, Country, PI, Status, Enrolled)
- ✅ Subjects table (Subject ID, Site, Status, Enrollment Date)

**Test Status Transition:**
1. On a "planning" study → click "Move to active"
2. **Expected:** Toast "Study transitioned to active", badge changes
3. On an "active" study → click "Move to locked"
4. **Expected:** Confirmation dialog (warns about freezing data), then transitions

---

## Test 5: Subjects Page

**URL:** http://localhost:5173/subjects

**Expected:**
- ✅ Subject list with columns: Subject ID, Study, Site, Status, Consent Date, Enrollment Date, Actions
- ✅ Search box, status filter dropdown
- ✅ "Enroll" button visible only for `screened` subjects

**Test Enrollment:**
1. Find a subject with status `screened`
2. Click "Enroll"
3. Set Consent Signed Date (e.g., 2026-03-01)
4. Set Enrollment Date (e.g., 2026-03-01)
5. Click "Enroll Subject"
6. **Expected:** Toast "Subject [ID] enrolled!", status changes to `enrolled`

---

## Test 6: Queries Page

**URL:** http://localhost:5173/queries

**Expected:**
- ✅ Query list: ID, Subject, Form, Field, Query Text, Status, Raised By, Actions
- ✅ Status filter (All/Open/Answered/Closed)
- ✅ "Answer" button on `open` queries
- ✅ "Close" button on `open` and `answered` queries

**Test Answer:**
1. Click "Answer" on an open query
2. Type response text
3. Click "Submit Answer"
4. **Expected:** Status changes to `answered`

**Test Close:**
1. Click "Close" on an open or answered query
2. **Expected:** Toast "Query closed!", status changes

---

## Test 7: Safety Page

**URL:** http://localhost:5173/safety

**Expected:**
- ✅ Adverse events table: ID, Subject, AE Term, Severity, SAE, Causality, Outcome, Start Date, Days Open
- ✅ "Show SAEs only" checkbox toggle
- ✅ SAE entries show red "SAE" badge
- ✅ Severity badges: mild=green, moderate=amber, severe=red

**Test SAE Filter:**
1. Check "Show SAEs only"
2. **Expected:** Only SAEs (serious=true) visible

---

## Test 8: Lab Results Page

**URL:** http://localhost:5173/lab

**Expected:**
- ✅ Lab results table: Subject, Test, Result, Unit, Ref Range, Flag, Date, Visit
- ✅ "Import CSV" button (top right)
- ✅ Flag filter (All/Normal/High/Low)
- ✅ Flag badges: N=green, H=red, L=amber

**Test CSV Import:**
1. Click "Import CSV"
2. Select a valid lab CSV file
3. **Expected:** Toast "Imported N lab results!", table refreshes

---

## Test 9: Audit Trail Page

**URL:** http://localhost:5173/audit

**Expected:**
- ✅ Audit log table: Timestamp, User, Action, Table, Record ID, Changes
- ✅ "Export CSV" button (top right)
- ✅ Action filter (All/Create/Update/Delete)
- ✅ Action badges: CREATE=green, UPDATE=blue, DELETE=red

**Test Export:**
1. Click "Export CSV"
2. **Expected:** Browser downloads `audit_trail.csv`

---

## Test 10: Navigation & UX

- ✅ **Sidebar:** Click each nav item → correct page loads
- ✅ **Active state:** Current page is highlighted indigo in sidebar
- ✅ **Top bar:** User initials in avatar, role displayed below name
- ✅ **Logout:** Click logout icon (top right) → returns to login page
- ✅ **Protected routes:** Visit any page without login → redirected to `/login`

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Login fails with network error | Docker not running | `docker compose up -d` |
| "401 Unauthorized" after login | Token expired | Logout and login again |
| Tables show "No data" | No seed data | Run `docker compose exec django-api python manage.py seed_data` |
| API returns 403 | Wrong role | Login as `dr.turemo` (study_admin) or `hact-user` |
| Page blank / white screen | JS error | Open browser DevTools (F12) → Console tab |
