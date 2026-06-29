#!/bin/bash
# =============================================================================
# Seed default users in Keycloak (runs after Keycloak is ready)
# Called from docker-compose or CI/CD pipeline
# =============================================================================
set -e

KEYCLOAK_HOST="${KEYCLOAK_HOST:-keycloak}"
KEYCLOAK_PORT="${KEYCLOAK_PORT:-8080}"
KC_ADMIN="${KEYCLOAK_ADMIN:-admin}"
KC_ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-change-me-keycloak-admin-password}"
KC_REALM="${KEYCLOAK_REALM:-hact}"

KCADM="/opt/keycloak/bin/kcadm.sh"

echo "=== Seeding Keycloak users ==="

# Wait for Keycloak to be ready
echo "[1/3] Waiting for Keycloak..."
until curl -sf "http://${KEYCLOAK_HOST}:${KEYCLOAK_PORT}/auth/realms/master" > /dev/null 2>&1; do
    echo "  Keycloak not ready — retrying in 3s..."
    sleep 3
done
echo "  Keycloak is ready!"

# Authenticate as admin
echo "[2/3] Authenticating as admin..."
$KCADM config credentials \
    --server "http://${KEYCLOAK_HOST}:${KEYCLOAK_PORT}/auth" \
    --realm master \
    --user "$KC_ADMIN" \
    --password "$KC_ADMIN_PASS" 2>/dev/null

# Create realm if it doesn't exist
$KCADM get "realms/${KC_REALM}" > /dev/null 2>&1 || \
    $KCADM create realms -s "realm=${KC_REALM}" -s enabled=true 2>/dev/null && \
    echo "  Realm '${KC_REALM}' ready."

# Function to create a user idempotently
create_user() {
    local USERNAME="$1"
    local PASSWORD="$2"
    local EMAIL="$3"
    local FIRSTNAME="$4"
    local LASTNAME="$5"

    # Check if user exists
    EXISTING=$($KCADM get users -r "$KC_REALM" -q "username=${USERNAME}" 2>/dev/null)
    if echo "$EXISTING" | grep -q "\"username\" : \"${USERNAME}\""; then
        echo "  User '${USERNAME}' already exists — updating password."
        USER_ID=$($KCADM get users -r "$KC_REALM" -q "username=${USERNAME}" --fields id 2>/dev/null | grep -o '"id" : "[^"]*"' | head -1 | cut -d'"' -f4)
        $KCADM set-password -r "$KC_REALM" --userid "$USER_ID" --new-password "$PASSWORD" 2>/dev/null
    else
        echo "  Creating user '${USERNAME}'..."
        $KCADM create users -r "$KC_REALM" \
            -s "username=${USERNAME}" \
            -s "email=${EMAIL}" \
            -s "firstName=${FIRSTNAME}" \
            -s "lastName=${LASTNAME}" \
            -s "enabled=true" \
            -s "emailVerified=true" 2>/dev/null

        $KCADM set-password -r "$KC_REALM" \
            --username "$USERNAME" \
            --new-password "$PASSWORD" 2>/dev/null

        echo "  Created user '${USERNAME}' with password '${PASSWORD}'."
    fi
}

echo "[3/3] Creating default users..."

# Create default users
create_user "hact-user"  "hact-user"  "hact-user@hacts.org"  "HACT" "User"
create_user "hact-admin" "hact-admin" "hact-admin@hacts.org" "HACT" "Admin"

echo ""
echo "=== Keycloak user seeding complete ==="
echo "  Login credentials:"
echo "    hact-user  / hact-user"
echo "    hact-admin / hact-admin"
echo ""
