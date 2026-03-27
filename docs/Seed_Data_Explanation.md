# HACT CTMS — Seed Data Explanation
## `python manage.py seed_data`

**Purpose:** Populates the database with realistic sample data for a Phase III Antimalarial clinical trial, enabling API testing and development without manual data entry.

---

## Usage

```bash
# Seed data (skips if data exists)
docker exec hact-django-api python manage.py seed_data

# Flush and re-seed (clears all existing data first)
docker exec hact-django-api python manage.py seed_data --flush
```

---

## Data Summary

| Category | Model | Count | Details |
|----------|-------|-------|---------|
| **Users** | User | 10 | 1 admin + 9 role-specific users |
| **Roles** | Role | 9 | All RBAC roles |
| **Role Assignments** | UserRole | 9 | One role per non-admin user |
| **Study** | Study | 1 | Phase III Antimalarial RCT |
| **Sites** | Site | 3 | 2 in Ethiopia + 1 in Kenya |
| **Site Staff** | SiteStaff | 5 | PI, coordinators, data managers |
| **Subjects** | Subject | 10 | Various enrollment statuses |
| **Visits** | Visit | 7 | Screening through Day 42 |
| **Subject Visits** | SubjectVisit | 24 | First 4 visits for enrolled subjects |
| **Forms** | FormDefinition | 4 | Demographics, Vitals, Medical Hx, AE |
| **Adverse Events** | AdverseEvent | 3 | 1 SAE + 2 non-serious |
| **Lab Results** | LabResult | 15 | 5 tests × 3 subjects |
| **Reference Ranges** | ReferenceRange | 6 | Male/Female normal ranges |
| **Contracts** | Contract | 3 | One per site |
| **Training Records** | TrainingRecord | 8 | 4 training types × 2 sites |
| **Milestones** | Milestone | 5 | Key study timeline events |

---

## Detailed Data

### 1. Users & Roles

**Admin User:**

| Field | Value |
|-------|-------|
| Username | `admin` |
| Email | `admin@hact.gov.et` |
| Password | `Admin@2026!` |
| Superuser | Yes |

**Role-Specific Users:**

| Username | Email | Role | Purpose |
|----------|-------|------|---------|
| `study_admin_user` | `study.admin@hact.gov.et` | `study_admin` | Study configuration |
| `data_manager_user` | `data.manager@hact.gov.et` | `data_manager` | Form/subject management |
| `site_coord_user` | `site.coord@hact.gov.et` | `site_coordinator` | Data entry at sites |
| `monitor_user` | `monitor@hact.gov.et` | `monitor` | Read-only data review |
| `safety_officer_user` | `safety@hact.gov.et` | `safety_officer` | Adverse event management |
| `lab_manager_user` | `lab.manager@hact.gov.et` | `lab_manager` | Lab data management |
| `ops_manager_user` | `ops.manager@hact.gov.et` | `ops_manager` | Operations management |
| `auditor_user` | `auditor@hact.gov.et` | `auditor` | Audit trail review |
| `pi_user` | `pi@hact.gov.et` | `principal_investigator` | Principal Investigator |

> All non-admin users have password: `User@2026!`

---

### 2. Study

| Field | Value |
|-------|-------|
| Protocol Number | `HACT-MAL-2026-001` |
| Title | Phase III Randomized Controlled Trial of Novel Antimalarial Combination Therapy |
| Phase | Phase III |
| Status | `active` |
| Sponsor | Ethiopian Public Health Institute (EPHI) |
| Start Date | 2026-01-15 |
| Expected End | 2027-06-30 |
| Target Enrollment | 500 |

---

### 3. Sites

| Site Code | Name | Country | City | Status |
|-----------|------|---------|------|--------|
| `ETH-AAU-001` | Addis Ababa University - Tikur Anbessa Hospital | Ethiopia | Addis Ababa | `active` |
| `ETH-JMC-002` | Jimma Medical Center | Ethiopia | Jimma | `active` |
| `KEN-KNH-003` | Kenyatta National Hospital | Kenya | Nairobi | `active` |

---

### 4. Site Staff Assignments

| User | Site | Role at Site | Start Date |
|------|------|-------------|------------|
| `pi_user` | ETH-AAU-001 | Principal Investigator | 2026-01-10 |
| `site_coord_user` | ETH-AAU-001 | Study Coordinator | 2026-01-12 |
| `data_manager_user` | ETH-AAU-001 | Data Manager | 2026-01-12 |
| `site_coord_user` | ETH-JMC-002 | Study Coordinator | 2026-01-20 |
| `data_manager_user` | KEN-KNH-003 | Data Manager | 2026-02-01 |

---

### 5. Subjects (Patients)

| Subject ID | Initials | Gender | DOB | Status | Site |
|------------|----------|--------|-----|--------|------|
| `HACT-001` | A.B. | M | 1985-03-15 | `enrolled` | ETH-AAU-001 |
| `HACT-002` | C.D. | F | 1990-07-22 | `enrolled` | ETH-AAU-001 |
| `HACT-003` | E.F. | M | 1978-11-08 | `enrolled` | ETH-AAU-001 |
| `HACT-004` | G.H. | F | 1995-01-30 | `enrolled` | ETH-JMC-002 |
| `HACT-005` | I.J. | M | 1988-06-14 | `enrolled` | ETH-JMC-002 |
| `HACT-006` | K.L. | F | 1992-09-25 | `enrolled` | ETH-JMC-002 |
| `HACT-007` | M.N. | M | 1983-12-03 | `enrolled` | KEN-KNH-003 |
| `HACT-008` | O.P. | F | 1997-04-18 | `screening` | KEN-KNH-003 |
| `HACT-009` | Q.R. | M | 1975-08-07 | `screening` | KEN-KNH-003 |
| `HACT-010` | S.T. | F | 1991-02-28 | `discontinued` | ETH-AAU-001 |

---

### 6. Visits (Study Schedule)

| Visit Number | Name | Window (Days) | Target Day |
|-------------|------|---------------|------------|
| 1 | Screening Visit | -14 to 0 | Day -14 |
| 2 | Baseline / Day 0 | 0 to 1 | Day 0 |
| 3 | Day 3 Follow-up | 2 to 4 | Day 3 |
| 4 | Day 7 Follow-up | 6 to 8 | Day 7 |
| 5 | Day 14 Follow-up | 13 to 15 | Day 14 |
| 6 | Day 28 Follow-up | 27 to 29 | Day 28 |
| 7 | Day 42 / End of Study | 41 to 43 | Day 42 |

---

### 7. Subject Visits

24 subject visit records — the first 4 visits for each of the 6 enrolled subjects at ETH-AAU-001 and ETH-JMC-002:

- Visits 1-3: Status = `completed`
- Visit 4: Status = `scheduled`
- Visit dates are offset from subject enrollment date (2026-02-01)

---

### 8. Form Definitions

| Form Code | Name | Version | Status |
|-----------|------|---------|--------|
| `DEMO-01` | Demographics Form | 1.0 | `active` |
| `VS-01` | Vital Signs Form | 1.0 | `active` |
| `MH-01` | Medical History Form | 1.0 | `active` |
| `AE-01` | Adverse Event Form | 1.0 | `active` |

---

### 9. Adverse Events

| Subject | Description | Severity | Serious? | Status | Start Date |
|---------|-------------|----------|----------|--------|------------|
| HACT-001 | Severe headache and nausea following dose administration | severe | Yes (SAE) | `ongoing` | 2026-02-10 |
| HACT-002 | Mild skin rash on forearms | mild | No | `resolved` | 2026-02-15 |
| HACT-003 | Moderate joint pain in lower extremities | moderate | No | `ongoing` | 2026-02-20 |

---

### 10. Lab Results

5 test types × 3 subjects (HACT-001, HACT-002, HACT-003):

| Test Name | Normal Range | Subject Results |
|-----------|-------------|-----------------|
| Hemoglobin (g/dL) | 12.0 – 17.5 (M) / 11.5 – 15.5 (F) | 14.2 (N), 12.8 (N), 15.1 (N) |
| White Blood Cell (×10³/µL) | 4.0 – 11.0 | 6.5 (N), 8.2 (N), 4.8 (N) |
| Platelet Count (×10³/µL) | 150 – 400 | 245 (N), 312 (N), 178 (N) |
| ALT (U/L) | 7 – 56 | 32 (N), 45 (N), 28 (N) |
| Creatinine (mg/dL) | 0.6 – 1.2 (M) / 0.5 – 1.1 (F) | 0.9 (N), 0.7 (N), 1.1 (N) |

**Flag Values:** `N` = Normal, `H` = High, `L` = Low

---

### 11. Reference Ranges

| Test | Gender | Lower Limit | Upper Limit | Unit |
|------|--------|-------------|-------------|------|
| Hemoglobin | Male | 12.0 | 17.5 | g/dL |
| Hemoglobin | Female | 11.5 | 15.5 | g/dL |
| White Blood Cell | All | 4.0 | 11.0 | ×10³/µL |
| Platelet Count | All | 150.0 | 400.0 | ×10³/µL |
| ALT | All | 7.0 | 56.0 | U/L |
| Creatinine | Male | 0.6 | 1.2 | mg/dL |

---

### 12. Contracts

| Site | Type | Value (USD) | Start | End | Status |
|------|------|-------------|-------|-----|--------|
| ETH-AAU-001 | Site Agreement | $150,000 | 2026-01-01 | 2027-06-30 | `active` |
| ETH-JMC-002 | Site Agreement | $120,000 | 2026-01-15 | 2027-06-30 | `active` |
| KEN-KNH-003 | Site Agreement | $135,000 | 2026-02-01 | 2027-06-30 | `active` |

---

### 13. Training Records

| Training Type | Sites | Date | Duration | Trainer |
|--------------|-------|------|----------|---------|
| GCP Training | AAU, JMC | 2026-01-05 | 8 hours | Dr. Sarah Chen |
| Protocol Training | AAU, JMC | 2026-01-08 | 4 hours | Dr. Sarah Chen |
| EDC System Training | AAU, JMC | 2026-01-10 | 6 hours | Technical Team |
| Safety Reporting | AAU, JMC | 2026-01-12 | 3 hours | Safety Officer |

---

### 14. Milestones

| Name | Target Date | Status |
|------|-------------|--------|
| Site Initiation Visit — AAU | 2026-01-15 | `completed` |
| Site Initiation Visit — JMC | 2026-01-25 | `completed` |
| First Patient Enrolled | 2026-02-01 | `completed` |
| 50% Enrollment Target | 2026-06-30 | `pending` |
| Database Lock | 2027-03-31 | `pending` |

---

## Entity Relationship Overview

```
Study (1)
  ├── Sites (3)
  │     ├── SiteStaff (5)
  │     ├── Subjects (10)
  │     │     ├── SubjectVisits (24)
  │     │     ├── AdverseEvents (3)
  │     │     └── LabResults (15)
  │     ├── Contracts (3)
  │     └── TrainingRecords (8)
  ├── Visits (7) — schedule template
  ├── FormDefinitions (4)
  └── Milestones (5)

Users (10) ──── Roles (9) ──── UserRoles (9)
ReferenceRanges (6) — standalone lab reference data
```

---

## Notes

- The seed data represents a realistic Phase III antimalarial trial in East Africa
- All dates are in 2026 to match the development timeline
- Subject IDs follow the format `HACT-XXX` for the study protocol
- The admin user can access Django Admin at `http://localhost/admin/`
- Re-running `seed_data` without `--flush` is safe — it skips if data exists
