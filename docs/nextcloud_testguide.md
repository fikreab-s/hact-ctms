# Nextcloud eTMF Integration — Test Guide

## Prerequisites

> [!IMPORTANT]
> Nextcloud requires ~512 MB RAM. Before starting, **stop OpenClinica** to free 1.5 GB:
> ```powershell
> docker compose --profile openclinica stop openclinica oc-postgres
> ```

## 1. Start Nextcloud

```powershell
docker compose --profile nextcloud up -d nextcloud
```

Wait ~2 minutes for first boot (Nextcloud installs itself on first start).

### Verify Container Health

```powershell
docker ps --filter "name=nextcloud" --format "table {{.Names}}\t{{.Status}}"
```

**Expected:**
```
NAMES              STATUS
hact-nextcloud     Up X minutes (healthy)
```

> [!NOTE]
> First boot takes longer — health check has `start_period: 60s` and retries 10 times.

---

## 2. Test Web UI Access

### Direct Access
Open browser: **http://localhost:8089**

**Expected:** Nextcloud login page

### Login Credentials
| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `hact-nc-2026` |

### Via NGINX Proxy
Open browser: **http://localhost/nextcloud/**

---

## 3. Run Integration Test

```powershell
docker exec hact-django-api python manage.py test_nextcloud
```

**Expected Output:**
```
Testing Nextcloud eTMF connection...
  URL:  http://nextcloud:80
  User: admin

✅ Nextcloud is REACHABLE
  Version: 28.x.x
  Edition: ...

Creating eTMF structure for test study HACT-TEST...
  ✅ eTMF folder structure created

Uploading test document...
  ✅ File uploaded: http://nextcloud:80/remote.php/dav/files/admin/eTMF/HACT-TEST/01_Regulatory/integration_test.txt

Downloading and verifying test document...
  ✅ Download verified (content matches)

Listing eTMF studies...
  📁 HACT-TEST

Listing eTMF documents for HACT-TEST/01_Regulatory...
  📄 integration_test.txt

Cleaning up test data...
  ✅ Test folder removed

✅ Nextcloud eTMF integration test COMPLETE.
```

---

## 4. Test Celery Tasks

### Health Check Task
```powershell
docker exec hact-django-api python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','hact_ctms.settings')
import django; django.setup()
from integrations.tasks import check_nextcloud_health
result = check_nextcloud_health.delay()
import time; time.sleep(5)
print('Result:', result.get(timeout=10))
"
```

**Expected:**
```
Result: {'status': 'healthy', 'version': '28.x.x', 'etmf_studies': 0}
```

### Create eTMF Structure Task
```powershell
docker exec hact-django-api python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','hact_ctms.settings')
import django; django.setup()
from integrations.tasks import create_etmf_for_study
result = create_etmf_for_study.delay('HACT-001')
import time; time.sleep(10)
print('Result:', result.get(timeout=15))
"
```

**Expected:**
```
Result: {'status': 'success', 'protocol': 'HACT-001'}
```

### Verify in Nextcloud UI
After running the above, go to **http://localhost:8089** → Files → **eTMF** → **HACT-001**

You should see 10 TMF Reference Model folders:
```
📁 01_Regulatory
📁 02_Protocol
📁 03_Safety
📁 04_DataManagement
📁 05_Monitoring
📁 06_SiteDocuments
📁 07_Contracts
📁 08_Training
📁 09_Exports
📁 10_Correspondence
```

---

## 5. Test Document Upload Task

```powershell
docker exec hact-django-api python -c "
import os, base64
os.environ.setdefault('DJANGO_SETTINGS_MODULE','hact_ctms.settings')
import django; django.setup()
from integrations.tasks import upload_document_to_etmf
content = base64.b64encode(b'Test safety document for HACT-001').decode()
result = upload_document_to_etmf.delay('HACT-001', '03_Safety', 'test_safety_doc.txt', content, 'text/plain')
import time; time.sleep(10)
print('Result:', result.get(timeout=15))
"
```

**Expected:**
```
Result: {'status': 'success', 'url': 'http://nextcloud:80/remote.php/dav/files/admin/eTMF/HACT-001/03_Safety/test_safety_doc.txt'}
```

### Verify in Nextcloud UI
Go to **http://localhost:8089** → Files → eTMF → HACT-001 → 03_Safety → `test_safety_doc.txt`

---

## 6. Verify Profile Isolation

Stop Nextcloud:
```powershell
docker compose --profile nextcloud stop nextcloud
```

Start core only:
```powershell
docker compose up -d
```

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected:** `hact-nextcloud` should NOT appear in the list.

---

## 7. Configuration Reference

### Environment Variables (.env)

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXTCLOUD_URL` | `http://nextcloud:80` | Internal Docker URL |
| `NEXTCLOUD_ADMIN_USER` | `admin` | Admin username |
| `NEXTCLOUD_ADMIN_PASSWORD` | `hact-nc-2026` | Admin password |

### Docker Compose Profile

| Command | What Starts |
|---------|-------------|
| `docker compose up -d` | Core only (no NC) |
| `docker compose --profile nextcloud up -d` | Core + Nextcloud |
| `docker compose --profile nextcloud --profile openclinica up -d` | Core + NC + OC |

### Ports

| Service | Direct Port | NGINX Route |
|---------|------------|-------------|
| Nextcloud | http://localhost:8089 | http://localhost/nextcloud/ |

---

## 8. eTMF Folder Structure (TMF Reference Model)

Each study gets this folder structure automatically:

| Folder | Purpose |
|--------|---------|
| `01_Regulatory` | IRB/EC submissions, regulatory approvals |
| `02_Protocol` | Protocol versions, amendments |
| `03_Safety` | CIOMS forms, safety reviews, SAE reports |
| `04_DataManagement` | CRF snapshots, DB lock records |
| `05_Monitoring` | Monitoring visit reports |
| `06_SiteDocuments` | Site-specific regulatory documents |
| `07_Contracts` | Contracts, budgets, invoices |
| `08_Training` | GCP certificates, training logs |
| `09_Exports` | CDISC/SDTM exports, data snapshots |
| `10_Correspondence` | Meeting minutes, email records |

---

## Troubleshooting

### Nextcloud shows "unhealthy"
```powershell
docker logs hact-nextcloud --tail 20
```
Usually means still installing. Wait 2-3 minutes.

### OutOfMemoryException
Stop other profile services to free RAM:
```powershell
docker compose --profile openclinica stop openclinica oc-postgres
```

### WebDAV authentication fails
Verify `.env` credentials match:
```powershell
docker exec hact-django-api printenv NEXTCLOUD_ADMIN_PASSWORD
```
Should output: `hact-nc-2026`
