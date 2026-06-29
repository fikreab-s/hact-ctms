# HACT CTMS — Full Project Audit & Context Restore

> Reconstructed from codebase on 2026-05-22. Replaces lost conversation history.

---

## 🏗️ Project Overview

**HACT Clinical Trial Management System (CTMS)**  
An open-source, composable platform for the **Horn of Africa Clinical Trials (HACT)** organization.  
Manages the full lifecycle of clinical research from protocol design through data export.

---

## 🧱 Architecture Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Frontend** | React 18 + Vite + React Router v7 | ✅ Built |
| **Backend** | Django 5.1 + DRF + Celery | ✅ Built |
| **Auth** | Keycloak OIDC (mozilla-django-oidc) | ✅ Built |
| **Database** | PostgreSQL 16 | ✅ Configured |
| **Task Queue** | Celery + Redis | ✅ Configured |
| **EDC** | OpenClinica CE | 🔌 Integration layer built |
| **eTMF Docs** | Nextcloud | 🔌 Integration layer built |
| **Lab LIMS** | SENAITE | 🔌 Integration layer built |
| **Operations** | ERPNext | 🔌 Integration layer built |
| **Infrastructure** | Docker Compose + Nginx | ✅ Configured |
| **PDF Generation** | ReportLab (CIOMS forms) | ✅ Built |
| **API Docs** | drf-spectacular (Swagger + ReDoc) | ✅ Configured |

---

## 📁 Backend Structure (`/backend`)

### Django Apps & Models

#### `accounts` app
- **User** — Custom AbstractUser with `keycloak_id` UUID for SSO
- **Role** — RBAC role definitions (data_manager, site_coordinator, monitor, PI, sponsor_admin, safety_officer, lab_manager, auditor)
- **UserRole** — User ↔ Role M2M mapping
- **SiteStaff** — User ↔ Site assignment with role_at_site
- **ExternalSystemIdentity** — Maps local users → OpenClinica/Nextcloud/SENAITE/ERPNext IDs

#### `clinical` app (core of the system)
- **Study** — Trial metadata (protocol_number, phase, sponsor, status, OpenClinica OID)
- **Site** — Participating sites (site_code, country, PI, ERPNext sync)
- **Subject** — Enrolled participants (subject_identifier, screening_number, enrollment_date, status)
- **Visit** — Visit schedule templates (visit_order, planned_day, window_before/after, OC Event OID)
- **SubjectVisit** — Actual subject visit records (scheduled_date, actual_date, status)
- **Form** — CRF definitions (name, version, OpenClinica CRF OID)
- **Item** — CRF fields (field_type: text/number/date/dropdown/radio/checkbox/textarea/file, options JSONB)
- **FormInstance** — Filled CRF instances (status: draft→submitted→signed→locked, 21 CFR Part 11 e-sig)
- **ItemResponse** — Actual data values (text storage, field-level audit)
- **Query** — Data discrepancy queries (open→answered→closed)

#### `safety` app
- **AdverseEvent** — AE records (severity, serious, causality, outcome, ICH-GCP E6 compliant)
- **CiomsForm** — CIOMS PDF form tracking (draft→submitted→approved, Nextcloud URL ref)
- **SafetyReview** — DSUR/DMC/Quarterly safety committee reviews

#### `lab` app
- Lab models, views, serializers — ✅ fully structured

#### `audit` app
- Audit trail models with signals — ✅ signal-driven logging

#### `outputs` app
- **ODM export** (`odm_export.py`) — CDISC ODM XML export
- **Quality checks** (`quality.py`) — Data quality metrics
- **Services** (`services.py`) — Export orchestration

#### `integrations` app
- **OpenClinica** (`openclinica.py`) — Full OC CE REST API client (14K bytes)
- **Nextcloud** (`nextcloud.py`) — WebDAV/REST client (11K bytes)
- **SENAITE** (`senaite.py`) — LIMS REST client (7.5K bytes)
- **ERPNext** (`erpnext.py`) — ERP REST client
- **Tasks** (`tasks.py`) — Celery async sync tasks (18K bytes — largest file)

#### `core` app
- **TimeStampedModel** — Base abstract model for all entities
- **auth_backend.py** — Keycloak OIDC authentication backend (12K)
- **permissions.py** — RBAC permission classes (5.5K)
- **mixins.py** — DRF view mixins
- **middleware.py** — Custom middleware

#### `ops` app
- Site operations, contracts, milestones models

### Backend API Routes (`/api/v1/`)
```
/api/v1/accounts/     → accounts.urls
/api/v1/clinical/     → clinical.urls
/api/v1/ops/          → ops.urls
/api/v1/safety/       → safety.urls
/api/v1/lab/          → lab.urls
/api/v1/outputs/      → outputs.urls
/api/v1/audit/        → audit.urls
/api/v1/integrations/ → integrations.urls
/api/health/          → health check
/api/schema/swagger/  → Swagger UI
/api/schema/redoc/    → ReDoc
```

### Key Backend Dependencies
- Django 5.1.5, DRF 3.15.2, django-filter 24.3
- psycopg2-binary (PostgreSQL)
- mozilla-django-oidc 4.0.1 + PyJWT (Keycloak)
- Celery 5.4.0 + Redis 5.2.1 + django-celery-beat
- drf-spectacular 0.28.0 (OpenAPI)
- reportlab 4.2.5 (CIOMS PDF)
- django-health-check 3.18.3

---

## 📁 Frontend Structure (`/frontend/src`)

### Technology
- React 18.3 + Vite 6 + React Router DOM v7
- State: **Zustand** (`store/authStore.js`)
- Server state: **TanStack React Query** v5
- HTTP: **Axios** (`api/client.js`, `api/endpoints.js`)
- Charts: **Recharts** v2
- Icons: **react-icons** v5
- Notifications: **react-hot-toast**
- Date utils: **date-fns**

### Pages (10 total)
| Page | File | Purpose |
|------|------|---------|
| Dashboard | `DashboardPage.jsx` (13K) | Main overview with stats/charts |
| Studies | `StudiesPage.jsx` (10K) | Study listing & management |
| Study Detail | `StudyDetailPage.jsx` (21K) | Full study detail — sites, subjects, visits |
| Subjects | `SubjectsPage.jsx` (13K) | Subject listing across studies |
| Subject Detail | `SubjectDetailPage.jsx` (14K) | Subject detail — visits, forms, AEs |
| Queries | `QueriesPage.jsx` (7.4K) | Data query management |
| Safety | `SafetyPage.jsx` (15K) | AE reporting & safety monitoring |
| Lab | `LabPage.jsx` (5.6K) | Lab sample tracking |
| Audit | `AuditPage.jsx` (6.7K) | Audit trail viewer |
| Integrations | `IntegrationStatusPage.jsx` (5.6K) | External system status |

### Components (7 total)
- `Sidebar.jsx` — Navigation sidebar
- `TopBar.jsx` — Top navigation bar
- `StatCard.jsx` — Dashboard stat card
- `StatusBadge.jsx` — Status indicator badge
- `LoadingSpinner.jsx` — Loading state
- `EmptyState.jsx` — Empty state UI
- `AccessDenied.jsx` — Permission denied screen

### Auth Module
- `LoginPage.jsx` — Keycloak SSO login UI
- `CallbackPage.jsx` — OIDC callback handler
- `ProtectedRoute.jsx` — Route guard
- `oidc.js` — OIDC flow logic (5.2K)
- `roleConfig.js` — Role-based UI permissions config (6.8K)
- `usePermission.js` — Permission hook

### Routing (App.jsx)
```
/              → DashboardPage
/login         → LoginPage  
/auth/callback → CallbackPage
/studies       → StudiesPage
/studies/:id   → StudyDetailPage
/subjects      → SubjectsPage
/subjects/:id  → SubjectDetailPage
/queries       → QueriesPage
/safety        → SafetyPage
/lab           → LabPage
/audit         → AuditPage
/integrations  → IntegrationStatusPage
```

---

## 🐳 Infrastructure

- **docker-compose.yml** (20K) — Full multi-service Docker Compose
- **nginx/** — Nginx reverse proxy config
- **openclinica/** — OpenClinica CE configuration
- **scripts/** — Utility scripts

---

## 📊 Development Phase Status

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 0 | Infrastructure & Docker | ✅ Complete |
| Phase 1 | Core platform (auth, study/site management) | ✅ Complete |
| Phase 2 | Clinical workflows (eCRF, visits, queries) | ✅ Complete |
| Phase 3 | Safety, lab, regulatory modules | ✅ Complete |
| Phase 4 | Testing, UAT, documentation, launch | 🔄 In Progress |

---

## ⚙️ Compliance Standards
- ICH-GCP E6(R2)
- 21 CFR Part 11 (electronic signatures — FormInstance signing)
- CDISC ODM/SDTM export
- GDPR / Data Protection
- CIOMS safety reporting forms

---

## 🔑 Key Notes for Continued Development
1. Auth is Keycloak OIDC — backend validates JWT tokens via `core/auth_backend.py`
2. All models extend `core.models.TimeStampedModel` for `created_at`/`updated_at`
3. Celery workers handle all async integration sync tasks (`integrations/tasks.py`)
4. CIOMS PDF generation uses ReportLab (`safety/cioms_pdf.py`)
5. ODM XML export for CDISC compliance is in `outputs/odm_export.py`
6. Frontend uses Zustand for auth state, React Query for server data
7. Role config in `frontend/src/auth/roleConfig.js` controls UI permissions

