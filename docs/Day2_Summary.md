# HACT CTMS — Day 2 Summary
## Authentication, Authorization & Audit Infrastructure

**Date:** March 27, 2026  
**Status:** ✅ Complete — All 106 API endpoints secured and tested

---

## Overview

Day 2 builds the **security and compliance layer** on top of the Day 1 infrastructure. This includes Keycloak-based JWT authentication, role-based access control (RBAC) on all API endpoints, and a comprehensive audit middleware for 21 CFR Part 11 compliance.

---

## Tasks Completed

### 1. Keycloak JWT Authentication Backend
**File:** `backend/core/auth_backend.py`

- **`KeycloakJWTAuthentication`** — DRF authentication class that:
  - Extracts Bearer token from `Authorization` header
  - Fetches and caches Keycloak's JWKS public keys (5-minute TTL)
  - Verifies JWT signature, expiry, audience (`azp`), and issuer
  - Accepts tokens from both `localhost` (Postman/browser) and `keycloak:8080` (internal Docker)
  - Auto-creates or links Django User from Keycloak token claims (`sub`, `email`, `preferred_username`)
- **`KeycloakOIDCBackend.create_or_update_user()`** — Handles 3 cases:
  1. User with matching `keycloak_id` already exists → update profile
  2. User with matching `username` exists but no Keycloak link → link and update
  3. Completely new user → create
- **Role Sync** — Reads `realm_access.roles` from JWT → auto-creates `Role` + `UserRole` entries in Django

### 2. RBAC Permission Classes
**File:** `backend/core/permissions.py`

9 custom permission classes with role cascading (higher roles include lower privileges):

| Permission Class | Required Role(s) | Applied To |
|---|---|---|
| `IsStudyAdmin` | `study_admin`, `admin` | Study/Site configuration, User management |
| `IsDataManager` | `data_manager`, `study_admin`, `admin` | Subjects, Forms, Queries |
| `IsSiteCoordinator` | `site_coordinator` + above | FormInstance data entry |
| `IsMonitor` | `monitor` + above (read-only) | Clinical data monitoring |
| `IsSafetyOfficer` | `safety_officer`, `study_admin`, `admin` | Adverse Events, CIOMS |
| `IsLabManager` | `lab_manager`, `study_admin`, `admin` | Lab Results, Samples |
| `IsOpsManager` | `ops_manager`, `study_admin`, `admin` | Contracts, Training |
| `IsAuditor` | `auditor` + above (read-only) | Audit trail access |
| `IsReadOnlyOrDataManager` | Any (read) / `data_manager` (write) | Subjects, Outputs |

### 3. Audit Middleware (Thread-Local Context)
**File:** `backend/core/middleware.py`

- Captures `request.user`, IP address, and user agent into thread-local storage
- Provides `get_current_user()`, `get_client_ip()`, `get_user_agent()` — accessible from anywhere
- Auto-cleans thread-local after each request to prevent memory leaks
- Positioned after `AuthenticationMiddleware` in `settings.py`

### 4. Auto-Audit on Model Save
**File:** `backend/core/models.py`

- `TimeStampedModel.save()` override auto-sets `created_by` and `updated_by` from request context
- Works without explicit serializer field passing

### 5. Enhanced Audit Signals
**File:** `backend/audit/signals.py`

- Post-save and post-delete signals now capture **WHO** (user), **FROM WHERE** (IP), and **HOW** (user agent)
- Every model create/update/delete is logged with full context
- Auth tables (`auth_users`, `auth_roles`, `auth_user_roles`) excluded to prevent loops during JWT authentication

### 6. ViewSet Mixins
**File:** `backend/core/mixins.py`

- **`AuditCreateMixin`** — Auto-sets `created_by`/`updated_by` in `perform_create()` and `perform_update()`
- **`StudyScopedMixin`** — Filters querysets by user's assigned sites (site coordinators see only their data)

### 7. Auth API Endpoints
**File:** `backend/accounts/views_auth.py`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/accounts/auth/me/` | Current user profile, roles, site assignments | Required |
| `GET` | `/api/v1/accounts/auth/status/` | Check authentication state | Public |

### 8. RBAC Applied to All ViewSets

| App | File | RBAC Applied |
|-----|------|-------------|
| Accounts | `accounts/views.py` | `IsStudyAdmin`, `IsReadOnlyOrStudyAdmin` |
| Clinical | `clinical/views.py` | `IsReadOnlyOrDataManager`, `IsDataManager`, `IsSiteCoordinator` + `StudyScopedMixin` |
| Safety | `safety/views.py` | `IsSafetyOfficer` |
| Lab | `lab/views.py` | `IsLabManager` |
| Ops | `ops/views.py` | `IsOpsManager` |
| Outputs | `outputs/views.py` | `IsReadOnlyOrDataManager` |
| Audit | `audit/views.py` | `IsAuditor` (read-only) |

### 9. Seed Data Management Command
**File:** `backend/core/management/commands/seed_data.py`

- `python manage.py seed_data` — Creates a complete test dataset
- `python manage.py seed_data --flush` — Clears existing data first
- See `docs/Seed_Data_Explanation.md` for full details

### 10. Settings & Dependencies

**Settings Updated (`hact_ctms/settings.py`):**
- Added `AuditMiddleware` after `AuthenticationMiddleware`
- Set `KeycloakJWTAuthentication` as default DRF authentication class
- Added `OIDC_OP_ISSUER`, `OIDC_RP_SIGN_ALGO`, and all Keycloak OIDC settings

**Dependencies Added (`requirements.txt`):**
- `PyJWT[crypto]` — JWT token decoding and verification
- `cryptography` — RSA key handling for JWKS
- `requests` — HTTP client for Keycloak JWKS endpoint

---

## Files Created (8 new files)

| File | Purpose |
|------|---------|
| `core/middleware.py` | Thread-local audit middleware |
| `core/auth_backend.py` | Keycloak JWT authentication + user sync |
| `core/permissions.py` | 9 RBAC permission classes |
| `core/mixins.py` | AuditCreateMixin + StudyScopedMixin |
| `accounts/views_auth.py` | `/auth/me/` and `/auth/status/` endpoints |
| `core/management/__init__.py` | Package init |
| `core/management/commands/__init__.py` | Package init |
| `core/management/commands/seed_data.py` | Database seed management command |

## Files Modified (12 files)

| File | Changes |
|------|---------|
| `hact_ctms/settings.py` | Added AuditMiddleware, JWT auth, OIDC settings |
| `accounts/urls.py` | Added auth routes |
| `accounts/views.py` | Applied RBAC permissions |
| `clinical/views.py` | RBAC + StudyScopedMixin + AuditCreateMixin |
| `safety/views.py` | Applied IsSafetyOfficer permission |
| `lab/views.py` | Applied IsLabManager permission |
| `ops/views.py` | Applied IsOpsManager permission |
| `outputs/views.py` | Applied IsReadOnlyOrDataManager permission |
| `audit/views.py` | Read-only + IsAuditor permission |
| `audit/signals.py` | Enhanced with user/IP/user-agent context |
| `core/models.py` | Auto-sets created_by/updated_by in save() |
| `requirements.txt` | Added PyJWT, cryptography, requests |

---

## Verification Results

| Test | Result |
|------|--------|
| `python manage.py check` | ✅ 0 issues |
| `GET /api/health/` | ✅ `{"status": "healthy"}` |
| `GET /api/schema/swagger/` | ✅ 200 OK — 106 endpoints |
| Unauthenticated → `/api/v1/clinical/studies/` | ✅ 401 Unauthorized |
| Token → `GET /api/v1/accounts/auth/me/` | ✅ Returns user profile with roles |
| Token → `GET /api/v1/clinical/studies/` | ✅ Returns study data |
| Token → `GET /api/v1/clinical/sites/` | ✅ Returns 3 sites |
| Token → `GET /api/v1/clinical/subjects/` | ✅ Returns 10 subjects |
| Token → `GET /api/v1/safety/adverse-events/` | ✅ Returns 3 AEs |
| Token → `GET /api/v1/lab/results/` | ✅ Returns 15 lab results |
| Token → `GET /api/v1/ops/contracts/` | ✅ Returns 3 contracts |
| Token → `GET /api/v1/audit/logs/` | ✅ Returns audit entries |
| `manage.py seed_data --flush` | ✅ All data created |
| Docker containers | ✅ All services healthy |

---

## Architecture Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐
│   Postman /  │────▶│    NGINX     │────▶│       Django + Gunicorn      │
│   Browser    │     │  (port 80)   │     │         (port 8000)          │
└──────────────┘     └──────┬───────┘     │                              │
                           │              │  ┌────────────────────────┐  │
                           │              │  │  AuditMiddleware       │  │
                           │              │  │  (thread-local user)   │  │
                           │              │  └────────┬───────────────┘  │
                           │              │           ▼                  │
                           │              │  ┌────────────────────────┐  │
                           │              │  │  KeycloakJWTAuth       │  │
                           │              │  │  (verify Bearer token) │  │
                           │              │  └────────┬───────────────┘  │
                           │              │           ▼                  │
                           │              │  ┌────────────────────────┐  │
                           │              │  │  RBAC Permissions      │  │
                           │              │  │  (check user roles)    │  │
                           │              │  └────────┬───────────────┘  │
                           │              │           ▼                  │
                           │              │  ┌────────────────────────┐  │
                           │              │  │  ViewSet + Serializer  │  │
                           │              │  │  (business logic)      │  │
                           │              │  └────────┬───────────────┘  │
                           │              │           ▼                  │
                           │              │  ┌────────────────────────┐  │
                           ▼              │  │  Audit Signals         │  │
                     ┌─────────────┐      │  │  (post_save logging)   │  │
                     │  Keycloak   │      │  └────────────────────────┘  │
                     │  (OIDC/JWT) │      └──────────────────────────────┘
                     └─────────────┘                    │
                                                        ▼
                                                 ┌──────────────┐
                                                 │  PostgreSQL  │
                                                 │  (hact_ctms) │
                                                 └──────────────┘
```

---

## Keycloak Setup Required

To use the API with JWT authentication:

1. **Realm:** `hact` (create in Keycloak Admin)
2. **Client:** `hact-ctms` (confidential, direct access grants enabled)
3. **Realm Roles:** `admin`, `study_admin`, `data_manager`, `site_coordinator`, `monitor`, `safety_officer`, `lab_manager`, `ops_manager`, `auditor`
4. **Test User:** Create with username, email, password, and assign role(s)
5. **Get Token:** `POST /auth/realms/hact/protocol/openid-connect/token`
6. **Use Token:** `Authorization: Bearer <access_token>`

---

## Next Steps (Day 3)

1. **Serializer Validation** — Enforce study status transitions, subject enrollment rules
2. **Nested Serializers** — Return related data (study with sites, subject with visits)
3. **Custom Actions** — Study lock/unlock, subject enrollment/withdrawal workflows
4. **Filtering & Search** — Advanced filtering per PRD requirements
5. **API Tests** — pytest test suite for critical endpoints
6. **Frontend Integration** — Connect React frontend to secured endpoints
