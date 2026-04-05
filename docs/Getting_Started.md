# HACT CTMS — Getting Started Guide

> Step-by-step instructions for running the project from scratch after cloning.

---

## Prerequisites

Make sure you have these installed:

| Tool | Version | Check |
|------|---------|-------|
| **Git** | 2.x+ | `git --version` |
| **Docker Desktop** | 4.x+ | `docker --version` |
| **Docker Compose** | v2+ | `docker compose version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |

> **RAM required:** At least 8 GB (Docker uses ~4.4 GB for all containers)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/fikreab-s/hact-ctms.git
cd hact-ctms
```

Switch to the frontend branch (if not merged to main yet):
```bash
git checkout feature/day5-react-frontend
```

---

## Step 2: Create the Environment File

```bash
cp .env.example .env
```

The default values in `.env.example` work for local development. No changes needed for basic setup.

---

## Step 3: Start the Backend (Docker)

Make sure Docker Desktop is running, then:

```bash
docker compose up -d
```

This starts **7 containers**:
| Container | Port | Purpose |
|-----------|------|---------|
| `hact-nginx` | 80 | Reverse proxy |
| `hact-django-api` | 8000 | REST API |
| `hact-celery-worker` | — | Async tasks |
| `hact-celery-beat` | — | Scheduled tasks |
| `hact-keycloak` | 8080 | Auth (OIDC/JWT) |
| `hact-postgres` | 5432 | Main database |
| `hact-redis` | 6379 | Cache + broker |

Wait ~60 seconds for all services to become healthy:
```bash
docker compose ps
```

All containers should show `Up (healthy)`.

---

## Step 4: Seed the Database

```bash
docker compose exec django-api python manage.py seed_data
```

This creates:
- 9 roles (study_admin, data_manager, etc.)
- 9 test users
- 1 sample study with sites, subjects, visits, forms, queries, AEs, and lab data

---

## Step 5: Set Up Keycloak

### 5a. Create the `hact` Realm

1. Open http://localhost/auth/admin
2. Login: `admin` / `change-me-keycloak-admin-password`
3. Hover over "master" (top-left) → Click **Create Realm**
4. Name: `hact` → Click **Create**

### 5b. Create the Confidential Client (for Django)

1. Go to **Clients** → **Create client**
2. Client ID: `hact-ctms`
3. Client authentication: **ON** (confidential)
4. Click **Next** → Enable: Standard flow, Direct access grants
5. Click **Save**
6. Go to **Credentials** tab → Copy the **Client Secret**
7. Paste it into `.env` as `OIDC_RP_CLIENT_SECRET=<paste-here>`

### 5c. Create the Public Client (for React Frontend)

1. Go to **Clients** → **Create client**
2. Client ID: `hact-ctms-frontend`
3. Client authentication: **OFF** (public)
4. Click **Next** → Enable: Standard flow, Direct access grants
5. Valid Redirect URIs: `http://localhost:5173/*`
6. Web Origins: `+`
7. Click **Save**

### 5d. Create the Realm Roles

Go to **Realm roles** → **Create role** — create each of these:

| Role Name |
|-----------|
| `admin` |
| `study_admin` |
| `data_manager` |
| `site_coordinator` |
| `monitor` |
| `safety_officer` |
| `lab_manager` |
| `ops_manager` |
| `auditor` |

### 5e. Create Test Users

Go to **Users** → **Add user** — create users with these details:

| Username | Password | Realm Role |
|----------|----------|-----------|
| `hact-user` | `hact-user` | `study_admin` |
| `dr.turemo` | `Test@2026!` | `study_admin` |
| `dm.sarah` | `Test@2026!` | `data_manager` |
| `sc.nurse.addis` | `Test@2026!` | `site_coordinator` |
| `sc.nurse.hawassa` | `Test@2026!` | `site_coordinator` |
| `cra.monitor` | `Test@2026!` | `monitor` |
| `safety.officer` | `Test@2026!` | `safety_officer` |
| `lab.manager` | `Test@2026!` | `lab_manager` |
| `ops.manager` | `Test@2026!` | `ops_manager` |
| `auditor` | `Test@2026!` | `auditor` |

For each user:
1. Fill in username → Click **Create**
2. Go to **Credentials** tab → **Set password** → uncheck "Temporary" → Save
3. Go to **Role mapping** tab → **Assign role** → Select the realm role → **Assign**

> **Shortcut:** If the `scripts/` folder exists, you can run:
> ```powershell
> powershell -ExecutionPolicy Bypass -File scripts/create_keycloak_users.ps1
> powershell -ExecutionPolicy Bypass -File scripts/fix_keycloak_roles.ps1
> ```

### 5f. Restart Django (to pick up Keycloak)

```bash
docker compose restart django-api
```

---

## Step 6: Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at **http://localhost:5173**

---

## Step 7: Verify

1. Open http://localhost:5173/login
2. Login with `hact-user` / `hact-user`
3. You should see the Dashboard with sidebar navigation

### Verify the API:
```bash
curl http://localhost/api/health/
# Should return: {"status": "healthy"}
```

### Verify Keycloak:
```bash
curl http://localhost/auth/realms/hact/.well-known/openid-configuration
# Should return JSON with token endpoints
```

---

## Quick Reference

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **API Docs (Swagger)** | http://localhost/api/v1/docs/ |
| **API Docs (ReDoc)** | http://localhost/api/v1/redoc/ |
| **Keycloak Admin** | http://localhost/auth/admin |
| **Django Admin** | http://localhost/admin |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Docker containers won't start | Make sure Docker Desktop is running. Check: `docker compose logs` |
| `502 Bad Gateway` on localhost | Wait 60s — Django is still starting. Check: `docker compose ps` |
| Login fails with "Invalid client" | Keycloak `hact-ctms-frontend` client not created (see Step 5c) |
| Login fails with "Invalid credentials" | User not created in Keycloak (see Step 5e) |
| Frontend shows blank page | Open browser DevTools (F12) → Console for errors |
| `npm install` fails | Make sure Node.js 18+ is installed: `node --version` |
| API returns 403 Forbidden | User role doesn't have access. See `docs/Test_Credentials.md` |

---

## Stopping the Project

```bash
# Stop all containers
docker compose down

# Stop and delete all data (fresh start)
docker compose down -v
```
