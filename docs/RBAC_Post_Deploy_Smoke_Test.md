# HACT CTMS — Post-Deploy RBAC Smoke Test

Run this right after the RBAC-hardening deploy to confirm (a) legitimate roles
can still do their jobs and (b) tightened endpoints correctly **block** the
wrong roles. Uses the 12 UAT accounts from `docs/UAT_User_Accounts.md`.

> Legend: ✅ = should succeed · ⛔ = should be blocked (403 Forbidden / hidden in UI)

---

## 0. Prep
- [ ] Deploy finished; `https://ctms.hacts.org/api/health/` → `200`.
- [ ] Ran the Keycloak seeding script on the VM (12 users exist).
- [ ] Hard-refresh the browser (Ctrl+Shift+R) to drop the old JS bundle.

Each login below: log out fully (ends the Keycloak SSO session), then log in as
the listed user.

---

## 1. `site_coordinator` (CRC) — `crc.addis` / `Crc1@2026!`
The most important regression check (these are the endpoints we tightened).
- [ ] ✅ Sidebar shows **only**: Dashboard, Studies, Subjects, Queries.
- [ ] ⛔ No Safety / Lab / Monitoring / Audit / Integrations links.
- [ ] ✅ **Mobile EDC** (`/edc`): can open a subject, **enroll** a subject, and **submit/edit a CRF** (this exercises the now-`IsSiteCoordinator` endpoints `POST /edc/enroll/` and `POST /edc/submit/`).
- [ ] ✅ Can answer a query.

## 2. `data_manager` — `data.manager1` / `DataMgr1@2026!`
- [ ] ✅ Sidebar: Dashboard, Studies, Subjects, Queries, Monitoring.
- [ ] ✅ Create subject, create/close query, run an export.
- [ ] ✅ Monitoring dashboard loads (now `IsMonitoringViewer`).
- [ ] ⛔ No Safety / Lab / Audit / Integrations.

## 3. `monitor` (CRA) — `cra.monitor` / `Monitor@2026!`
- [ ] ✅ Sidebar: Dashboard, Studies, Subjects, Queries, Monitoring.
- [ ] ✅ Monitoring RBM dashboard + SAE timeline load.
- [ ] ⛔ Cannot create/edit subjects (read-only) — write actions hidden/blocked.

## 4. `safety_officer` — `safety.officer` / `Safety@2026!`
- [ ] ✅ Sidebar: Dashboard, Studies, Safety, Monitoring.
- [ ] ✅ Create AE/SAE, generate CIOMS, **mark SAE reported**.
- [ ] ✅ Monitoring + SAE timeline load (included in `IsMonitoringViewer`).
- [ ] ⛔ No Lab / Audit / Integrations / Subjects nav.

## 5. `lab_manager` — `lab.manager` / `LabMgr@2026!`
- [ ] ✅ Sidebar: Dashboard, Studies, Lab.
- [ ] ✅ On `/lab`: **"Sync from SENAITE"** works (exercises the now-`IsLabManager` `POST /integrations/senaite/pull-results/`), register sample, import CSV.
- [ ] ⛔ No Safety / Monitoring / Audit / Integrations.

## 6. `auditor` — `auditor1` / `Auditor@2026!`
**Key security check — auditor must be strictly read-only.**
- [ ] ✅ Sidebar: Dashboard, Studies, Audit. Can view + export audit trail.
- [ ] ⛔ Via Mobile EDC, **cannot enroll a subject or submit a CRF** → `403` (previously this was allowed — the bug we fixed).
- [ ] ⛔ No Safety / Lab / Monitoring / Subjects / Integrations.

## 7. `ops_manager` — `ops.manager` / `OpsMgr@2026!`
- [ ] ✅ Sidebar: Dashboard only (+ Mobile EDC surface).
- [ ] ⛔ Cannot access Studies write, Safety, Lab, Monitoring, Audit, Integrations.

## 8. `study_admin` — `study.admin` / `StudyAdmin@2026!`
- [ ] ✅ Full sidebar incl. Integrations.
- [ ] ✅ Create/edit study, create site, **OpenClinica import-metadata** (now `IsStudyAdmin`), **eTMF document upload** (now `IsStudyAdmin`).
- [ ] ✅ Can do everything the module roles can.

## 9. `admin` — `system.admin` / `SysAdmin@2026!`
- [ ] ✅ Superuser/admin: everything, plus Django admin at `/admin/` (incl. UAT Feedback review).

---

## Quick API spot-checks (optional, via curl)
Get a token for a role, then hit a tightened endpoint. Expect `403` for the
wrong role, `2xx` for the right one.

```bash
# Get an access token (replace user/pass)
TOKEN=$(curl -s -X POST \
  "https://ctms.hacts.org/auth/realms/hact/protocol/openid-connect/token" \
  -d "client_id=hact-ctms-frontend" -d "grant_type=password" \
  -d "username=auditor1" -d "password=Auditor@2026!" | jq -r .access_token)

# Auditor enrolling via EDC → expect 403
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  "https://ctms.hacts.org/api/v1/edc/enroll/" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'
# Expected: 403
```

> Note: password grant works only if the `hact-ctms-frontend` client has Direct
> Access Grants enabled; otherwise test through the UI. See
> `docs/Keycloak_OIDC_2FA_Setup.md`.

---

## If something legitimate is blocked
- Confirm the user's realm role is assigned in Keycloak (Users → Role Mappings).
- Remember roles sync to Django on **login** — log out/in after a role change.
- Cross-check the expected role set in `frontend/src/auth/roleConfig.js` and
  `backend/core/permissions.py`.
