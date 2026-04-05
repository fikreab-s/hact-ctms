# HACT CTMS — Test Credentials & RBAC Reference

> **Environment:** http://localhost:5173  
> **Last Updated:** 2026-04-05  
> **Auth Provider:** Keycloak (hact realm)

---

## User Credentials

| # | Username | Password | Role | Full Name |
|---|----------|----------|------|-----------|
| 1 | `hact-user` | `hact-user` | study_admin | HACT User |
| 2 | `dr.turemo` | `Test@2026!` | study_admin | Turemo Bedaso |
| 3 | `dm.sarah` | `Test@2026!` | data_manager | Sarah Bekele |
| 4 | `sc.nurse.addis` | `Test@2026!` | site_coordinator | Almaz Tadesse |
| 5 | `sc.nurse.hawassa` | `Test@2026!` | site_coordinator | Fatima Mohammed |
| 6 | `cra.monitor` | `Test@2026!` | monitor | Daniel Abebe |
| 7 | `safety.officer` | `Test@2026!` | safety_officer | Helen Girma |
| 8 | `lab.manager` | `Test@2026!` | lab_manager | Solomon Tekle |
| 9 | `ops.manager` | `Test@2026!` | ops_manager | Meron Haile |
| 10 | `auditor` | `Test@2026!` | auditor | Yonas Wolde |

---

## Role Permissions Matrix

### Sidebar Navigation

| Page | study_admin | data_manager | site_coordinator | monitor | safety_officer | lab_manager | ops_manager | auditor |
|------|:-----------:|:------------:|:----------------:|:-------:|:--------------:|:-----------:|:-----------:|:-------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Studies | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Subjects | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Queries | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Safety | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Lab | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Audit | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Action Buttons

| Action | study_admin | data_manager | site_coordinator | monitor | safety_officer | lab_manager | ops_manager | auditor |
|--------|:-----------:|:------------:|:----------------:|:-------:|:--------------:|:-----------:|:-----------:|:-------:|
| New Study | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Move to active/locked | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Create Subject | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Enroll Subject | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Answer Query | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Close Query | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Import Lab CSV | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Export Audit CSV | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Quick Test Checklist

### For each user, verify:

- [ ] Login at http://localhost:5173/login with username/password above
- [ ] Sidebar shows only the allowed pages (see matrix above)
- [ ] Role badge at bottom of sidebar shows correct role name
- [ ] Directly navigating to a restricted URL shows "Access Denied"
- [ ] Action buttons are hidden/shown according to the matrix above

### Recommended test flow:

1. **`lab.manager`** — Login → sidebar should show: Dashboard, Studies, Lab (only 3)
   - Go to Lab page → "Import CSV" button visible ✅
   - Type `/audit` in URL → "Access Denied" page ✅
   - Go to Studies → "New Study" button hidden ✅

2. **`auditor`** — Login → sidebar: Dashboard, Studies, Audit
   - Go to Audit page → "Export CSV" button visible ✅
   - Type `/safety` in URL → "Access Denied" ✅

3. **`dm.sarah`** — Login → sidebar: Dashboard, Studies, Subjects, Queries
   - Go to Queries → "Answer" hidden, "Close" visible ✅
   - Type `/lab` in URL → "Access Denied" ✅

4. **`cra.monitor`** — Login → sidebar: Dashboard, Studies, Subjects, Queries
   - All pages are **read-only** — no action buttons visible ✅

5. **`safety.officer`** — Login → sidebar: Dashboard, Studies, Safety
   - Type `/subjects` in URL → "Access Denied" ✅

---

## Admin Access

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Keycloak Admin | http://localhost/auth/admin | `admin` | `change-me-keycloak-admin-password` |
| Django Admin | http://localhost/admin | (superuser) | (set during setup) |
| Swagger API | http://localhost/api/v1/docs/ | — | Bearer token |
