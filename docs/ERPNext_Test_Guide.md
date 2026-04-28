# HACT CTMS — ERPNext Integration Test Guide

This guide walks you through testing the end-to-end integration between Django CTMS, React Frontend, and ERPNext.

> [!WARNING]
> **Memory**: Before starting, stop OpenClinica and Nextcloud if RAM is tight:
> `docker compose stop openclinica oc-postgres nextcloud`

## Step 1: Start ERPNext

```bash
docker compose --profile erpnext up -d
```

Verify all containers are running:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

You should see: `hact-erpnext`, `hact-erpnext-frontend`, `hact-erpnext-worker`, `hact-erpnext-scheduler`, `hact-mariadb`.

## Step 2: Access ERPNext UI

Open your browser and navigate to:

**http://localhost:8080**

Login with:
- **Email**: `Administrator`
- **Password**: `admin`

You should see the ERPNext Setup Wizard or Dashboard.

## Step 3: Complete ERPNext Setup Wizard

On first login, ERPNext shows a Setup Wizard. Fill in:
1. **Language**: English
2. **Country**: Ethiopia
3. **Company Name**: `HACT Clinical Trials`
4. **Domain**: `Services`

This creates the base Company, Chart of Accounts, and Customer Groups needed for site/contract management.

## Step 4: Generate API Keys for Django Integration

1. In ERPNext, go to **Settings → User** (or navigate to `/app/user/Administrator`).
2. Click on the **Administrator** user.
3. Scroll down to **API Access** section.
4. Click **Generate Keys**.
5. Copy the **API Key** and **API Secret**.
6. Update your `.env` file:
   ```
   ERPNEXT_API_KEY=<paste API Key here>
   ERPNEXT_API_SECRET=<paste API Secret here>
   ```
7. Restart Django: `docker restart hact-django-api hact-celery-worker`

## Step 5: Test Django → ERPNext API Connection

```bash
docker exec hact-django-api python manage.py test_erpnext
```

Expected output:
```
✅ ERPNext is REACHABLE
✅ Webhook executed successfully. Site is now active.
✅ ERPNext integration test COMPLETE.
```

## Step 6: Test Webhook (ERPNext → Django Site Activation)

The webhook simulates ERPNext marking a contract as "Signed", which automatically activates the site in Django.

Using curl:
```bash
curl -X POST http://localhost/api/v1/integrations/erpnext/webhook/contract-signed/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-token>" \
     -d '{"erpnext_site_id": "<site-erpnext-id>", "contract_status": "Signed"}'
```

Or test via the management command (Step 5) which tests this automatically.

## Step 7: Verify Integration Status

```bash
curl http://localhost/api/v1/integrations/status/
```

Expected response includes:
```json
{
  "erpnext": {"status": "healthy"},
  "nextcloud": {"status": "unavailable"},
  "openclinica": {"status": "unavailable"}
}
```

## Stopping ERPNext (without affecting other services)

To stop **only** ERPNext containers:
```bash
docker compose stop erpnext erpnext-frontend erpnext-worker erpnext-scheduler mariadb
```

## Troubleshooting

| Issue | Fix |
|---|---|
| ERPNext UI not loading | Check `docker logs hact-erpnext-frontend` |
| API connection failing | Ensure API keys are set in `.env` and Django is restarted |
| Celery sync errors | Check `docker logs hact-celery-worker --tail 50` |
| MariaDB collation error | Volumes may need to be recreated with correct charset |
