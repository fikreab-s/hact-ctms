# HACT CTMS — User Management & RBAC Guide

**Everything you need to know about users, roles, and access control.**

---

## How Authentication Works

The HACT system uses a **two-layer auth system**:

```
User (Postman/Browser)
    │
    ├── 1. Gets access_token from Keycloak
    │      POST http://localhost/auth/realms/hact/protocol/openid-connect/token
    │
    ├── 2. Sends token to Django API
    │      Authorization: Bearer <access_token>
    │
    └── 3. Django validates JWT → auto-creates/links Django User → checks roles
```

**Key insight:** Users are managed in **Keycloak** (where they log in), but their **roles and permissions** are enforced in **Django** (where the API runs). The two systems sync automatically.

---

## Step-by-Step: Register a New User

### Method 1: Via Keycloak Admin Console (Recommended)

**1. Open Keycloak Admin:**
```
http://localhost/auth/admin/
Username: admin
Password: admin  (or whatever you set in docker-compose)
```

**2. Select the `hact` realm** (top-left dropdown)

**3. Create the user:**
- Left menu → **Users** → **Add user**
- Fill in:
  - **Username:** `dr.newuser`
  - **Email:** `newuser@hact.gov.et`
  - **First Name:** `New`
  - **Last Name:** `User`
  - **Enabled:** ON
- Click **Save**

**4. Set their password:**
- Go to the **Credentials** tab
- **Set Password:** `SecurePass123!`
- **Temporary:** OFF (so they don't have to change on first login)
- Click **Save Password**

**5. Assign Keycloak realm roles (optional):**
- Go to **Role Mappings** tab
- Assign roles like `data_manager`, `site_coordinator`, etc.
- These roles will auto-sync to Django on first login

**6. Test the new user:**
```
POST http://localhost/auth/realms/hact/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded (form-data)

client_id:      hact-ctms
client_secret:  mk108Hu1yat2GOkpm9EpFEIHyKiMX5Kh
grant_type:     password
username:       dr.newuser
password:       SecurePass123!
```

**When this user first calls any Django API endpoint**, the `KeycloakJWTAuthentication` backend will:
1. Decode & verify the JWT token
2. Extract `sub` (Keycloak UUID), `preferred_username`, `email`
3. **Auto-create a Django User** record (or link to existing one)
4. **Auto-sync roles** from `realm_access.roles` in the JWT

### Method 2: Via Django API (Manual)

If you want to create a Django user directly (e.g., for testing):

```
POST /api/v1/accounts/users/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "username": "dr.newuser",
    "email": "newuser@hact.gov.et",
    "first_name": "New",
    "last_name": "User",
    "password": "SecurePass123!"
}
```

> **Note:** This creates a Django-only user. They won't be able to log in via Keycloak unless you also create them there. For production, always use Method 1.

---

## Step-by-Step: Assign Roles to a User

### Understanding the Role System

```
Role (table: auth_roles)           ← Definition of each role
  │
  └── UserRole (table: auth_user_roles)  ← Links users to roles (many-to-many)
        │
        └── Permission Classes (core/permissions.py) ← Checked on every API request
```

### Available Roles

| Role Name | Access Level | What They Can Do |
|-----------|-------------|-----------------|
| `admin` | Everything | Full system access, bypasses all role checks |
| `study_admin` | Study-wide | Create/edit studies, sites, visits, forms; manage all data |
| `data_manager` | Data management | Manage subjects, forms, queries, data cleaning, exports |
| `site_coordinator` | Site-level | Enter data, fill forms, respond to queries at assigned sites |
| `monitor` | Read-only clinical | View clinical data for monitoring (CRA role), cannot edit |
| `safety_officer` | Safety module | Manage AEs, SAEs, CIOMS forms, safety reviews |
| `lab_manager` | Lab module | Manage lab results, reference ranges, samples, CSV import |
| `ops_manager` | Operations | Manage contracts, training records, milestones |
| `auditor` | Read-only audit | View and export audit trail only |

### Permission Hierarchy

Roles inherit access from lower levels. The hierarchy is:

```
admin ──────────────────────────────────────── (access to everything)
  └── study_admin ──────────────────────────── (access to all modules)
        ├── data_manager ──────────────────── (clinical data + queries + exports)
        │     └── site_coordinator ────────── (data entry only)
        │           └── monitor ───────────── (read-only)
        ├── safety_officer ────────────────── (safety module only)
        ├── lab_manager ───────────────────── (lab module only)
        ├── ops_manager ───────────────────── (operations only)
        └── auditor ───────────────────────── (audit trail read-only)
```

### Assign a Role via API

**Step 1: Find the user's ID**
```
GET /api/v1/accounts/users/
Authorization: Bearer <admin-token>
```

**Step 2: Find the role ID**
```
GET /api/v1/accounts/roles/
Authorization: Bearer <admin-token>
```

Response:
```json
[
    {"id": 1, "name": "admin", "description": "Full system administrator"},
    {"id": 2, "name": "study_admin", "description": "Study-level administrator"},
    {"id": 3, "name": "data_manager", "description": "Forms, queries, subjects..."},
    {"id": 4, "name": "site_coordinator", "description": "Data entry at assigned sites"},
    {"id": 5, "name": "monitor", "description": "Read-only clinical data monitoring"},
    {"id": 6, "name": "safety_officer", "description": "AE/SAE and safety reporting"},
    {"id": 7, "name": "lab_manager", "description": "Lab data and sample tracking"},
    {"id": 8, "name": "ops_manager", "description": "Contracts, training, milestones"},
    {"id": 9, "name": "auditor", "description": "Read-only audit trail access"}
]
```

**Step 3: Create the UserRole assignment**
```
POST /api/v1/accounts/user-roles/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "user": 10,
    "role": 3
}
```

This assigns `data_manager` (role ID 3) to user ID 10.

**Step 4: Assign multiple roles** (a user can have many roles)
```
POST /api/v1/accounts/user-roles/
{"user": 10, "role": 6}
```

Now user 10 has both `data_manager` and `safety_officer` roles.

---

## Step-by-Step: Assign a User to a Site

Site Coordinators need to be linked to specific sites:

```
POST /api/v1/accounts/site-staff/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "site": 1,
    "user": 4,
    "role_at_site": "Study Nurse",
    "start_date": "2026-04-01"
}
```

---

## How RBAC Is Enforced (What Happens Behind the Scenes)

When a user calls any API endpoint, this is what happens:

```
1. User sends: GET /api/v1/clinical/studies/
   Header: Authorization: Bearer eyJhbGciOi...

2. KeycloakJWTAuthentication runs:
   ├── Decodes the JWT token
   ├── Verifies signature against Keycloak JWKS public keys
   ├── Extracts claims (sub, email, username, realm_access.roles)
   ├── Auto-creates/updates Django User
   └── Returns (user, decoded_token)

3. Permission class runs (e.g., IsStudyAdmin):
   ├── Queries UserRole table for this user
   ├── Caches roles: {"study_admin", "data_manager"}
   └── Returns True/False

4. If True → ViewSet processes the request
   If False → Returns 403 Forbidden
```

### What Each Endpoint Requires

| Module | ViewSet | Permission | Who Can Access |
|--------|---------|-----------|---------------|
| Studies | `StudyViewSet` | `IsReadOnlyOrStudyAdmin` | All read; study_admin+ write |
| Sites | `SiteViewSet` | `IsReadOnlyOrStudyAdmin` | All read; study_admin+ write |
| Subjects | `SubjectViewSet` | `IsSiteCoordinator` | site_coordinator, data_manager, study_admin, admin |
| Visits | `VisitViewSet` | `IsReadOnlyOrStudyAdmin` | All read; study_admin+ write |
| Forms | `FormViewSet` | `IsReadOnlyOrStudyAdmin` | All read; study_admin+ write |
| Form Instances | `FormInstanceViewSet` | `IsSiteCoordinator` | site_coordinator+ |
| Item Responses | `ItemResponseViewSet` | `IsSiteCoordinator` | site_coordinator+ |
| Queries | `QueryViewSet` | `IsDataManager` | data_manager, study_admin, admin |
| Adverse Events | `AdverseEventViewSet` | `IsSafetyOfficer` | safety_officer, study_admin, admin |
| CIOMS Forms | `CiomsFormViewSet` | `IsSafetyOfficer` | safety_officer, study_admin, admin |
| Lab Results | `LabResultViewSet` | `IsLabManager` | lab_manager, study_admin, admin |
| Contracts | `ContractViewSet` | `IsOpsManager` | ops_manager, study_admin, admin |
| Audit Logs | `AuditLogViewSet` | `IsAuditor` | auditor, study_admin, admin (read-only) |
| Snapshots | `DatasetSnapshotViewSet` | `IsDataManager` | data_manager, study_admin, admin |
| Quality Reports | `DataQualityReportViewSet` | `IsDataManager` | data_manager, study_admin, admin |

---

## Existing Seed Users

| Username | Role | Password | What They Can Do |
|----------|------|----------|-----------------|
| `dr.turemo` | study_admin | Test@2026! | Everything (study-level admin) |
| `dm.sarah` | data_manager | Test@2026! | Subjects, forms, queries, exports |
| `sc.nurse.addis` | site_coordinator | Test@2026! | Data entry at ETH-001 |
| `sc.nurse.hawassa` | site_coordinator | Test@2026! | Data entry at ETH-002 |
| `cra.monitor` | monitor | Test@2026! | Read-only clinical data |
| `safety.officer` | safety_officer | Test@2026! | AE/SAE, CIOMS forms |
| `lab.manager` | lab_manager | Test@2026! | Lab results, samples |
| `ops.manager` | ops_manager | Test@2026! | Contracts, training |
| `auditor` | auditor | Test@2026! | Audit trail (read-only) |

> **Note:** These are Django-only users from seed data. To use them via Keycloak, create matching users in Keycloak with the same usernames.

---

## Auto-Sync: Keycloak Roles → Django

When a user logs in via Keycloak, the JWT token contains:

```json
{
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "preferred_username": "dr.newuser",
    "email": "newuser@hact.gov.et",
    "realm_access": {
        "roles": ["data_manager", "safety_officer", "default-roles-hact"]
    }
}
```

The `KeycloakOIDCBackend.create_or_update_user()` method:
1. Creates/updates the Django User from `sub`, `email`, `preferred_username`
2. Reads `realm_access.roles` from the token
3. Filters out Keycloak internal roles (`offline_access`, `uma_authorization`, `default-roles-hact`)
4. Auto-creates `Role` and `UserRole` records in Django

**This means:** If you assign `data_manager` in Keycloak → the user automatically gets `data_manager` in Django on their next API call.

---

## Quick Reference: Common Tasks

### Register new user + assign role:
```
1. Create in Keycloak Admin → Users → Add User → Set Password
2. Assign realm role in Keycloak → Role Mappings
3. User logs in → Django auto-creates user + syncs roles
```

### Change a user's role:
```
Method A: Change in Keycloak → auto-syncs on next login
Method B: POST /api/v1/accounts/user-roles/ → immediate effect
```

### Remove a role:
```
DELETE /api/v1/accounts/user-roles/{id}/
Authorization: Bearer <admin-token>
```

### Check what roles a user has:
```
GET /api/v1/accounts/user-roles/?user={user_id}
Authorization: Bearer <admin-token>
```

### Deactivate a user:
```
PATCH /api/v1/accounts/users/{id}/
{"is_active": false}
```
