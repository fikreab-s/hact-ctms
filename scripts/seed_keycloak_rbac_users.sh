#!/bin/bash
# =============================================================================
# Seed HACT RBAC users in Keycloak (realm roles + role-mapped users)
# =============================================================================
# Creates the 9 HACT realm roles and 12 role-mapped user accounts so that,
# on first login, Django's KeycloakOIDCBackend auto-syncs each user's role
# (realm_access.roles -> accounts.UserRole) and the React frontend scopes the
# UI per role via src/auth/roleConfig.js.
#
# Role names MUST match frontend/src/auth/roleConfig.js and backend
# core/permissions.py exactly:
#   admin, study_admin, data_manager, site_coordinator, monitor,
#   safety_officer, lab_manager, ops_manager, auditor
#
# IDEMPOTENT: safe to re-run. Existing users get their password re-set and the
# role re-asserted; existing roles are left as-is.
#
# ── How to run (on the deployment VM) ───────────────────────────────────────
#   1) Copy this script into the running Keycloak container and execute it:
#        docker cp scripts/seed_keycloak_rbac_users.sh hact-keycloak:/tmp/
#        docker exec -e KEYCLOAK_ADMIN=admin \
#                    -e KEYCLOAK_ADMIN_PASSWORD='<your-kc-admin-pass>' \
#                    hact-keycloak bash /tmp/seed_keycloak_rbac_users.sh
#
#   (KEYCLOAK_ADMIN / KEYCLOAK_ADMIN_PASSWORD default to the compose env values.)
# =============================================================================
set -euo pipefail

# When run *inside* the hact-keycloak container, the server is localhost:8080
# and the relative path is /auth (KC_HTTP_RELATIVE_PATH=/auth in compose).
KEYCLOAK_HOST="${KEYCLOAK_HOST:-localhost}"
KEYCLOAK_PORT="${KEYCLOAK_PORT:-8080}"
KEYCLOAK_BASE="${KEYCLOAK_BASE:-/auth}"
KC_ADMIN="${KEYCLOAK_ADMIN:-admin}"
KC_ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-change-me-keycloak-admin-password}"
KC_REALM="${KEYCLOAK_REALM:-hact}"

KCADM="/opt/keycloak/bin/kcadm.sh"
SERVER="http://${KEYCLOAK_HOST}:${KEYCLOAK_PORT}${KEYCLOAK_BASE}"

echo "=== HACT RBAC user seeding (realm: ${KC_REALM}) ==="

# ── 1. Wait for Keycloak & authenticate ──────────────────────────────────────
echo "[1/4] Waiting for Keycloak at ${SERVER} ..."
until curl -sf "${SERVER}/realms/master" > /dev/null 2>&1; do
    echo "  not ready — retrying in 3s..."
    sleep 3
done
echo "  ready."

echo "[2/4] Authenticating as '${KC_ADMIN}' ..."
$KCADM config credentials \
    --server "${SERVER}" \
    --realm master \
    --user "$KC_ADMIN" \
    --password "$KC_ADMIN_PASS"

# Ensure the realm exists (it normally does; create defensively).
$KCADM get "realms/${KC_REALM}" > /dev/null 2>&1 || \
    $KCADM create realms -s "realm=${KC_REALM}" -s enabled=true

# ── 2. Create the 9 HACT realm roles (idempotent) ────────────────────────────
create_role() {
    local NAME="$1"; local DESC="$2"
    if $KCADM get "roles/${NAME}" -r "$KC_REALM" > /dev/null 2>&1; then
        echo "  role '${NAME}' exists."
    else
        $KCADM create roles -r "$KC_REALM" -s "name=${NAME}" -s "description=${DESC}"
        echo "  created role '${NAME}'."
    fi
}

echo "[3/4] Ensuring realm roles ..."
create_role "admin"             "Full system administrator"
create_role "study_admin"       "Study-level administrator (studies, sites, visits, forms)"
create_role "data_manager"      "Subjects, forms, queries, data cleaning, exports"
create_role "site_coordinator"  "Site data entry (CRC) — enroll, fill CRFs, answer queries"
create_role "monitor"           "Read-only clinical data monitoring (CRA)"
create_role "safety_officer"    "Adverse events, SAEs, CIOMS forms"
create_role "lab_manager"       "Lab results, reference ranges, samples"
create_role "ops_manager"       "Contracts, training, milestones"
create_role "auditor"           "Read-only audit trail"

# ── 3. Create users + assign a realm role (idempotent) ───────────────────────
# create_user <username> <password> <email> <first> <last> <realm_role>
create_user() {
    local USERNAME="$1"; local PASSWORD="$2"; local EMAIL="$3"
    local FIRSTNAME="$4"; local LASTNAME="$5"; local ROLE="$6"

    local EXISTING
    EXISTING=$($KCADM get users -r "$KC_REALM" -q "username=${USERNAME}" 2>/dev/null || echo "[]")
    if echo "$EXISTING" | grep -q "\"username\" : \"${USERNAME}\""; then
        echo "  user '${USERNAME}' exists — resetting password."
        local USER_ID
        # `|| true` guards against SIGPIPE/pipefail aborting the script when
        # `head -1` closes the pipe early (matters under `set -euo pipefail`).
        USER_ID=$($KCADM get users -r "$KC_REALM" -q "username=${USERNAME}" --fields id 2>/dev/null \
                  | grep -o '"id" : "[^"]*"' | head -1 | cut -d'"' -f4 || true)
        $KCADM set-password -r "$KC_REALM" --userid "$USER_ID" --new-password "$PASSWORD"
    else
        echo "  creating user '${USERNAME}' (${ROLE})..."
        $KCADM create users -r "$KC_REALM" \
            -s "username=${USERNAME}" \
            -s "email=${EMAIL}" \
            -s "firstName=${FIRSTNAME}" \
            -s "lastName=${LASTNAME}" \
            -s "enabled=true" \
            -s "emailVerified=true"
        # Password is permanent (no forced change) for UAT convenience.
        $KCADM set-password -r "$KC_REALM" --username "$USERNAME" --new-password "$PASSWORD"
    fi

    # Assign the realm role (add-roles is idempotent — safe to repeat).
    $KCADM add-roles -r "$KC_REALM" --uusername "$USERNAME" --rolename "$ROLE"
    echo "    -> role '${ROLE}' assigned."
}

echo "[4/4] Creating role-mapped users ..."
#            username          password             email                          first      last          role
create_user "study.admin"     "StudyAdmin@2026!"   "study.admin@hacts.org"        "Alemu"    "Tadesse"     "study_admin"
create_user "data.manager1"   "DataMgr1@2026!"     "data.manager1@hacts.org"      "Sara"     "Bekele"      "data_manager"
create_user "data.manager2"   "DataMgr2@2026!"     "data.manager2@hacts.org"      "Yohannes" "Girma"       "data_manager"
create_user "crc.addis"       "Crc1@2026!"         "crc.addis@hacts.org"          "Meron"    "Haile"       "site_coordinator"
create_user "crc.jimma"       "Crc2@2026!"         "crc.jimma@hacts.org"          "Dawit"    "Fikru"       "site_coordinator"
create_user "crc.nairobi"     "Crc3@2026!"         "crc.nairobi@hacts.org"        "Amina"    "Njoroge"     "site_coordinator"
create_user "cra.monitor"     "Monitor@2026!"      "cra.monitor@hacts.org"        "Helen"    "Assefa"      "monitor"
create_user "safety.officer"  "Safety@2026!"       "safety.officer@hacts.org"     "Getachew" "Mola"        "safety_officer"
create_user "lab.manager"     "LabMgr@2026!"       "lab.manager@hacts.org"        "Rahel"    "Tesfaye"     "lab_manager"
create_user "ops.manager"     "OpsMgr@2026!"       "ops.manager@hacts.org"        "Samuel"   "Kebede"      "ops_manager"
create_user "auditor1"        "Auditor@2026!"      "auditor1@hacts.org"           "Tigist"   "Alemayehu"   "auditor"
create_user "system.admin"    "SysAdmin@2026!"     "system.admin@hacts.org"       "System"   "Admin"       "admin"

echo ""
echo "=== Done. 9 roles ensured, 12 users created/updated. ==="
echo "Users log in at the HACT frontend; roles auto-sync to Django on first login."
