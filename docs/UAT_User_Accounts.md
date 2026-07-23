# HACT CTMS — UAT User Accounts (Role-Based)

These 12 accounts cover all **9 HACT RBAC roles**. They live in **Keycloak**
(realm `hact`); on first login each user's role auto-syncs to Django and the
React frontend scopes the UI accordingly (see `frontend/src/auth/roleConfig.js`).

> Created by `scripts/seed_keycloak_rbac_users.sh` (idempotent — safe to re-run).

---

## How to create these users (run on the deployment VM)

```bash
# From the repo root on the VM
docker cp scripts/seed_keycloak_rbac_users.sh hact-keycloak:/tmp/
docker exec \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD='<your-keycloak-admin-password>' \
  hact-keycloak bash /tmp/seed_keycloak_rbac_users.sh
```

The script (1) ensures the 9 realm roles exist, (2) creates the 12 users with
permanent passwords, and (3) assigns each user's realm role. Re-running it just
resets passwords and re-asserts roles.

---

## Credentials

| # | Username | Password | Role | Full Name | Email |
|---|----------|----------|------|-----------|-------|
| 1 | `study.admin` | `StudyAdmin@2026!` | `study_admin` | Alemu Tadesse | study.admin@hacts.org |
| 2 | `data.manager1` | `DataMgr1@2026!` | `data_manager` | Sara Bekele | data.manager1@hacts.org |
| 3 | `data.manager2` | `DataMgr2@2026!` | `data_manager` | Yohannes Girma | data.manager2@hacts.org |
| 4 | `crc.addis` | `Crc1@2026!` | `site_coordinator` (CRC) | Meron Haile | crc.addis@hacts.org |
| 5 | `crc.jimma` | `Crc2@2026!` | `site_coordinator` (CRC) | Dawit Fikru | crc.jimma@hacts.org |
| 6 | `crc.nairobi` | `Crc3@2026!` | `site_coordinator` (CRC) | Amina Njoroge | crc.nairobi@hacts.org |
| 7 | `cra.monitor` | `Monitor@2026!` | `monitor` (CRA) | Helen Assefa | cra.monitor@hacts.org |
| 8 | `safety.officer` | `Safety@2026!` | `safety_officer` | Getachew Mola | safety.officer@hacts.org |
| 9 | `lab.manager` | `LabMgr@2026!` | `lab_manager` | Rahel Tesfaye | lab.manager@hacts.org |
| 10 | `ops.manager` | `OpsMgr@2026!` | `ops_manager` | Samuel Kebede | ops.manager@hacts.org |
| 11 | `auditor1` | `Auditor@2026!` | `auditor` | Tigist Alemayehu | auditor1@hacts.org |
| 12 | `system.admin` | `SysAdmin@2026!` | `admin` | System Admin | system.admin@hacts.org |

> Passwords are permanent (no forced change) for UAT convenience. For a stricter
> setup, enable **Configure OTP** / **Update Password** as a Required User Action
> per user in Keycloak (see `docs/Keycloak_OIDC_2FA_Setup.md`).

---

## What each role sees (sidebar / accessible pages)

Derived from `SIDEBAR_ACCESS` in `frontend/src/auth/roleConfig.js`.

| Role | Dashboard | Studies | Subjects | Queries | Safety | Lab | Monitoring | Audit | Integrations |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `admin` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `study_admin` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `data_manager` | ✅ | ✅ | ✅ | ✅ | – | – | ✅ | – | – |
| `site_coordinator` (CRC) | ✅ | ✅ | ✅ | ✅ | – | – | – | – | – |
| `monitor` (CRA) | ✅ | ✅ | ✅ | ✅ | – | – | ✅ | – | – |
| `safety_officer` | ✅ | ✅ | – | – | ✅ | – | ✅ | – | – |
| `lab_manager` | ✅ | ✅ | – | – | – | ✅ | – | – | – |
| `ops_manager` | ✅ | – | – | – | – | – | – | – | – |
| `auditor` | ✅ | ✅ | – | – | – | – | – | ✅ | – |

All roles can also access the **Mobile EDC** (`/edc`) surface.

> Example — the **CRC** accounts (`crc.addis`, `crc.jimma`, `crc.nairobi`) only
> see **Dashboard, Studies, Subjects, Queries** and can enroll subjects / fill
> CRFs / answer queries; they cannot see Safety, Lab, Monitoring, Audit, or
> Integrations.

---

## Key action permissions by role

From `ACTION_PERMISSIONS` in `roleConfig.js`:

- **Create/edit study, create site, transition study** → `admin`, `study_admin`
- **Create subject** → `admin`, `study_admin`, `data_manager`
- **Enroll / withdraw subject, answer query, submit CRF** → + `site_coordinator`
- **Create query, close query, exports, quality report** → `admin`, `study_admin`, `data_manager`
- **Create AE, generate CIOMS** → `admin`, `study_admin`, `safety_officer`
- **Import lab CSV, register sample, sync lab results** → `admin`, `study_admin`, `lab_manager`
- **Manage milestones** → `admin`, `study_admin`, `ops_manager`
- **Export audit** → `admin`, `study_admin`, `auditor`

---

## Notes on the auth flow

1. User logs in at the HACT frontend → redirected to Keycloak (realm `hact`).
2. Keycloak issues a JWT containing `realm_access.roles`.
3. Django `KeycloakOIDCBackend.create_or_update_user()` auto-creates/links the
   Django user and syncs roles into the `accounts.UserRole` table.
4. `GET /api/v1/accounts/auth/me/` returns the user + roles; the frontend uses
   them to render the correct sidebar, routes, and action buttons.

Changing a role later: update the user's **Role Mapping** in Keycloak → it
re-syncs on their next login (or POST to `/api/v1/accounts/user-roles/` for an
immediate change). See `docs/User_Management_RBAC_Guide.md`.
