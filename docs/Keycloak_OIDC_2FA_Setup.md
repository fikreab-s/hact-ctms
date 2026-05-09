# Keycloak Configuration for OIDC PKCE + 2FA

## Overview
The frontend has been migrated from **password grant** to **Authorization Code + PKCE**.
Keycloak must be configured to match this flow.

---

## Step 1: Configure the Frontend Client

Open Keycloak Admin Console: **http://localhost/auth** → Login as `admin`

Navigate to: **Realm: hact** → **Clients** → **hact-ctms-frontend**

### Settings Tab

| Field | Value | Why |
|---|---|---|
| **Client Protocol** | `openid-connect` | ✅ Already set |
| **Access Type** | `public` | No client_secret for SPA |
| **Standard Flow Enabled** | `ON` | Authorization Code flow |
| **Direct Access Grants Enabled** | `OFF` | ⚠️ Disable password grant |
| **Implicit Flow Enabled** | `OFF` | Not needed with PKCE |
| **Valid Redirect URIs** | `http://localhost/auth/callback` | Where Keycloak redirects after login |
| **Valid Post Logout Redirect URIs** | `http://localhost/login` | Where to go after logout |
| **Web Origins** | `http://localhost` or `+` | CORS for token endpoint |

### Advanced Settings (expand)

| Field | Value |
|---|---|
| **Proof Key for Code Exchange Code Challenge Method** | `S256` |
| **Access Token Lifespan** | `5 minutes` (default, refreshed automatically) |

**Click Save.**

---

## Step 2: Enable Two-Factor Authentication (OTP)

Navigate to: **Realm: hact** → **Authentication**

### Option A: Required for ALL Users

1. Click **Flows** tab → Select **Browser** flow
2. Find **OTP Form** row → Change requirement from `OPTIONAL` to `REQUIRED`
3. Click **Save**

Now every user must configure an OTP authenticator (Google Authenticator, FreeOTP, etc.) on first login.

### Option B: Required for Specific Roles Only

1. Go to **Authentication** → **Flows** → Duplicate the **Browser** flow → Name it `Browser + OTP`
2. In the duplicated flow, set **OTP Form** to `REQUIRED`
3. Go to **Bindings** tab → Set **Browser Flow** to `Browser + OTP`
4. Or assign per-user: Go to **Users** → Select user → **Required User Actions** → Add `Configure OTP`

### Option C: Per-User Opt-In (Recommended for Demo)

1. Navigate to: **Users** → Select a user (e.g., admin)
2. Click **Required User Actions** dropdown
3. Add **Configure OTP**
4. Click **Save**

Next time the user logs in, Keycloak will prompt them to set up an authenticator app.

---

## Step 3: Verify the Setup

### Test Login Flow
1. Open http://localhost → Click **"Sign in with Keycloak SSO"**
2. You should be redirected to Keycloak's login page
3. Enter username/password
4. If 2FA is enabled, enter OTP code from authenticator app
5. You should be redirected back to the HACT dashboard

### Test Token Refresh
1. Login successfully
2. Wait 4+ minutes (access token expires at 5 min)
3. Navigate to a different page — it should work without re-login
4. Check browser console for: `[Auth] Token refreshed successfully`

### Test Session Timeout
1. Login and leave the browser idle for 30+ minutes
2. You should be automatically logged out
3. Check browser console for: `[Auth] Session timed out due to inactivity`

### Test Logout
1. Click the logout button in the top bar
2. You should be redirected to Keycloak's logout page then back to /login
3. Your Keycloak SSO session should be terminated

---

## Keycloak Admin Console Commands (Alternative to UI)

If you prefer to configure via Keycloak REST API:

```bash
# Get admin token
KC_TOKEN=$(curl -s -X POST "http://localhost/auth/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" | jq -r '.access_token')

# Update hact-ctms-frontend client
curl -s -X PUT "http://localhost/auth/admin/realms/hact/clients/<CLIENT_UUID>" \
  -H "Authorization: Bearer $KC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "hact-ctms-frontend",
    "publicClient": true,
    "standardFlowEnabled": true,
    "directAccessGrantsEnabled": false,
    "redirectUris": ["http://localhost/auth/callback"],
    "webOrigins": ["+"],
    "attributes": {
      "pkce.code.challenge.method": "S256",
      "post.logout.redirect.uris": "http://localhost/login"
    }
  }'
```

---

## Architecture Summary

```
┌─────────────┐     1. Click Login      ┌──────────────┐
│   React     │ ──────────────────────▶  │   Keycloak   │
│   Frontend  │                          │   Login Page │
│             │     4. /auth/callback    │  + 2FA/OTP   │
│             │ ◀──────────────────────  │              │
│             │     ?code=xxx&state=yyy  └──────────────┘
│             │
│  5. Exchange code+verifier for tokens
│  6. GET /api/v1/accounts/auth/me/
│  7. Schedule token refresh (every 4 min)
│  8. Start session timeout (30 min idle)
└─────────────┘
```
