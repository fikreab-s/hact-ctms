# HACT CTMS — SENAITE LIMS Integration Test Guide

This guide walks you through testing the end-to-end integration between Django CTMS and SENAITE LIMS.

> [!WARNING]
> **Memory**: Before starting, stop other heavy services if RAM is tight:
> `docker compose stop erpnext erpnext-frontend erpnext-worker erpnext-scheduler mariadb`

---

## Step 1: Start SENAITE

```bash
docker compose --profile senaite up -d
```

Verify the container is running and healthy:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=senaite"
```

Wait until `hact-senaite` status shows `healthy` (takes ~60-90s on first boot).

---

## Step 2: Create the SENAITE Site (First-Time Only)

1. Open your browser: **http://localhost:8081**
2. You will see the **"Install SENAITE LIMS"** page.
3. Fill in the following:
   - **Site ID**: `senaite`
   - **Title**: `SENAITE LIMS`
   - **Admin Username**: `admin`
   - **Admin Password**: `admin`
4. Click **"Create SENAITE Site"**
5. Wait for installation to complete (may take 1-2 minutes).

> [!NOTE]
> This step only needs to be done once. The data persists in the `senaite_data` Docker volume.

---

## Step 3: Access SENAITE UI

After site creation, navigate to:

**http://localhost:8081/senaite**

Login with:
- **Username**: `admin`
- **Password**: `admin`

You should see the SENAITE LIMS dashboard.

---

## Step 4: Initial SENAITE Configuration

Configure these items in SENAITE for the integration to work:

### 4a. Create a Client
1. Go to **Clients** (left sidebar or top menu)
2. Click **Add**
3. **Name**: `HACT Clinical Trials`
4. **Client ID**: `HACT`
5. Click **Save**

### 4b. Create Sample Types
1. Go to **LIMS Setup** → **Sample Types**
2. Add the following types (click **Add** for each):
   - **Title**: `Blood` | **Prefix**: `BLD`
   - **Title**: `Urine` | **Prefix**: `URN`
   - **Title**: `Tissue` | **Prefix**: `TSS`
3. Click **Save** for each

### 4c. Create Analysis Services (Lab Tests)
1. Go to **LIMS Setup** → **Analysis Services**
2. Add tests relevant to your trials:
   - **Title**: `Hemoglobin` | **Unit**: `g/dL` | **Category**: `Hematology`
   - **Title**: `WBC Count` | **Unit**: `10^3/uL` | **Category**: `Hematology`
   - **Title**: `Glucose` | **Unit**: `mg/dL` | **Category**: `Chemistry`
3. Click **Save** for each

### 4d. Create a Lab Contact
1. Go to **LIMS Setup** → **Lab Contacts**
2. Click **Add**
3. Fill in name and email
4. Click **Save**

---

## Step 5: Run the Automated Test

```bash
docker exec hact-django-api python manage.py test_senaite
```

Expected output:
```
Testing SENAITE connection...
✅ SENAITE is REACHABLE

Testing Results Published Webhook...
  Created test sample: TEST-SENAITE-001
✅ Webhook executed successfully. Sample is now completed.
  Test data cleaned up.

✅ SENAITE integration test COMPLETE.
```

---

## Step 6: Test the Full Data Flow

### 6a. Django → SENAITE (Sample Sync)

When a `SampleCollection` is created in Django, a Celery task automatically pushes it to SENAITE:

1. Create a sample via Django API or admin
2. The `sync_sample_to_senaite` Celery task fires
3. Check SENAITE UI → the sample appears under the `HACT Clinical Trials` client

### 6b. SENAITE → Django (Results Pull)

1. In SENAITE, create a sample and enter analysis results
2. Walk through the SENAITE workflow: **Receive** → **Submit** → **Verify** → **Publish**
3. Pull results into Django:
   ```bash
   docker exec hact-django-api python manage.py shell -c "
   from integrations.tasks import pull_results_from_senaite
   result = pull_results_from_senaite.apply()
   print(result.get())
   "
   ```
4. Imported results appear in Django LabResult table with auto H/L/N flags

### 6c. SENAITE → Django Webhook (Results Published)

When SENAITE publishes results, it can notify Django via webhook:

```bash
curl -X POST http://localhost/api/v1/integrations/senaite/webhook/results-published/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-token>" \
     -d '{"senaite_sample_id": "<sample-id>", "status": "published"}'
```

This automatically updates the `SampleCollection` status to `completed`.

---

## Step 7: Verify Integration Status

```bash
curl http://localhost/api/v1/integrations/status/
```

Expected response:
```json
{
  "senaite": {"status": "healthy"},
  "erpnext": {"status": "unavailable"},
  "nextcloud": {"status": "unavailable"},
  "openclinica": {"status": "unavailable"}
}
```

---

## Stopping SENAITE (without affecting other services)

```bash
docker compose stop senaite
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| SENAITE UI not loading | Wait 60-90s for Plone to start. Check `docker logs hact-senaite --tail 20` |
| "Install SENAITE LIMS" page | You need to create the site first (see Step 2) |
| API 401 error | Verify `SENAITE_API_USER` and `SENAITE_API_PASSWORD` in `.env` match SENAITE admin |
| Sample sync failing | Ensure SENAITE has a Client named `HACT Clinical Trials` |
| Results not pulling | Ensure results are in **Published** state (not just Submitted) |
| Container unhealthy | Check `docker logs hact-senaite --tail 50` |
| Port conflict on 8081 | Check if another service is using port 8081 |
