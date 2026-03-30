# HACT CTMS — External Systems Integration Strategy

**Date:** March 28, 2026  
**Status:** Approved — Stakeholder requirement  
**PRD Reference:** Sections 5, 8, 11, 13, 14, 16

---

## 1. Overview

The HACT CTMS is a **multi-system platform** comprising a Django backend (central orchestrator) and four external open-source systems required by stakeholders:

| System | License | Purpose | PRD Phase |
|--------|---------|---------|-----------|
| **OpenClinica CE 4.x** | LGPL 3.0 | Electronic Data Capture (eCRF, queries, DB lock, CDISC export) | Phase 0 / Phase 2 |
| **ERPNext 15+** | GPL 3.0 | Operations Management (site CRM, contracts, training) | Phase 0 / Phase 3 |
| **Nextcloud 28+** | AGPL 3.0 | Document Management (eTMF, regulatory docs, versioning) | Phase 0 / Phase 3 |
| **SENAITE 2.x** | GPL 2.0 | Laboratory Information Management (samples, results, workflows) | Phase 0 / Phase 3 |

> **These integrations are a hard requirement agreed upon during the requirements specification period with stakeholders.**

---

## 2. Architecture — Django as Central Orchestrator

The PRD (Section 13) defines Django as the **central API gateway**. All frontend requests route through Django, which dispatches to downstream systems. The external systems are **satellite services** that sync with Django — they do NOT replace Django.

```
┌──────────────────────────────────────────────────────────────┐
│                        React Frontend                         │
│                    (Single Page Application)                   │
└────────────────────────────┬─────────────────────────────────┘
                             │  All requests via REST API
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    Django Orchestrator                         │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Custom Modules (What We Build)                       │    │
│  │  ├── accounts/   (Users, Roles, RBAC)                │    │
│  │  ├── clinical/   (Study, Site, Subject, Visit, Form) │    │
│  │  ├── safety/     (AE, SAE, CIOMS, Safety Reviews)    │    │
│  │  ├── lab/        (Results, Samples, Ref Ranges)      │    │
│  │  ├── ops/        (Contracts, Training, Milestones)   │    │
│  │  ├── outputs/    (Exports, Data Quality Reports)     │    │
│  │  └── audit/      (Audit Trail)                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Integration Modules (Added Later — NO code removed)  │    │
│  │  ├── integrations/openclinica.py                      │    │
│  │  ├── integrations/erpnext.py                          │    │
│  │  ├── integrations/nextcloud.py                        │    │
│  │  └── integrations/senaite.py                          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Celery Tasks (Async Sync Operations)                 │    │
│  │  ├── Sync study → OpenClinica (real-time)             │    │
│  │  ├── Sync site data → ERPNext (hourly)                │    │
│  │  ├── Upload docs → Nextcloud (on demand)              │    │
│  │  └── Pull lab results ← SENAITE (on demand)           │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────┬────────────┬────────────┬────────────┬──────────┘
             │            │            │            │
             ▼            ▼            ▼            ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
      │OpenClinica│ │ ERPNext  │ │Nextcloud │ │ SENAITE  │
      │  (EDC)   │ │  (Ops)   │ │ (eTMF)   │ │ (LIMS)   │
      └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## 3. Key Principle — Nothing Gets Removed

When external systems are integrated, **zero existing code is removed**. The Django backend is the master system; external systems are added ON TOP.

### What Stays (Current Django Backend)

All models, serializers, views, permissions, middleware, and audit infrastructure remain exactly as they are:

| App | Models (All Stay) |
|-----|-------------------|
| `clinical` | Study, Site, Subject, Visit, SubjectVisit, Form, Item, FormInstance, ItemResponse, Query |
| `safety` | AdverseEvent, CiomsForm, SafetyReview |
| `lab` | LabResult, ReferenceRange, SampleCollection |
| `ops` | Contract, TrainingRecord, Milestone, SiteStaff |
| `accounts` | User, Role, UserRole, ExternalSystemLink |
| `audit` | AuditLog |
| `outputs` | ExportLog, DataQualityReport |

### What Gets Added (Integration Layer)

| Addition | Type | Description |
|----------|------|-------------|
| `backend/integrations/__init__.py` | New package | Integration module package |
| `backend/integrations/openclinica.py` | New file | OpenClinica REST API client + sync logic |
| `backend/integrations/erpnext.py` | New file | ERPNext Frappe API client + sync logic |
| `backend/integrations/nextcloud.py` | New file | Nextcloud WebDAV/OCS API client |
| `backend/integrations/senaite.py` | New file | SENAITE JSON API client + result import |
| `docker-compose.yml` | Modified | New service containers added |
| `nginx/nginx.conf` | Modified | New proxy routes for external UIs |
| `.env` | Modified | New connection credentials |

### What Does NOT Change

| Component | Impact |
|-----------|--------|
| Existing Django models | ❌ No changes (OID fields already exist) |
| Existing API endpoints | ❌ No changes (same URLs, same responses) |
| Existing serializers | ❌ No changes |
| Existing permissions (RBAC) | ❌ No changes |
| Existing audit middleware | ❌ No changes |
| Existing seed data | ❌ No changes |
| Postman collections | ❌ No changes |

---

## 4. Pre-Built OID Mapping Fields

The Django models were designed from Day 1 with integration fields ready:

| Model | Field | Links To |
|-------|-------|----------|
| `Study` | `openclinica_study_oid` | OpenClinica Study (`S_HACT001`) |
| `Visit` | `openclinica_event_definition_oid` | OpenClinica Event Definition |
| `Form` | `openclinica_crf_oid` | OpenClinica CRF |
| `Site` | `erpnext_site_id` | ERPNext Site record (`SITE-00001`) |
| `SampleCollection` | `senaite_sample_id` | SENAITE Sample (`SAMP-2026-0001`) |
| `CiomsForm` | `file_url` | Nextcloud document path |
| `SafetyReview` | `file_url` | Nextcloud document path |
| `ExternalSystemLink` | `external_id` | Any external system user mapping |

These fields are currently blank and will be populated when integrations are activated.

---

## 5. How Each Integration Works

### 5.1 OpenClinica CE Integration

**Data Flow:**
```
1. Study Admin creates a Study in Django
2. Django → OpenClinica API: Creates matching study in OC
3. OC returns study_oid → Django stores in openclinica_study_oid
4. Site Coordinator enters data → Django FormInstance
5. Celery task syncs FormInstance data → OpenClinica for regulatory compliance
6. OpenClinica provides CDISC/SDTM export capability
```

**Sync Strategy:** Synchronous for study/subject creation, asynchronous (Celery) for form data sync.

**API Used:** OpenClinica REST API v2 (`/api/v2/studies`, `/api/v2/participants`, `/api/v2/events`)

---

### 5.2 ERPNext Integration

**Data Flow:**
```
1. Study Admin creates Site in Django
2. Celery task syncs Site data → ERPNext Customer/Project
3. Ops Manager manages contracts/budgets in ERPNext
4. Celery hourly task pulls contract status → Django Contract model
5. Training records managed in both systems, synced via API
```

**Sync Strategy:** Asynchronous (Celery hourly sync)

**API Used:** ERPNext Frappe REST API (`/api/resource/Customer`, `/api/resource/Project`)

---

### 5.3 Nextcloud Integration

**Data Flow:**
```
1. Regulatory Manager uploads document via Django API
2. Django → Nextcloud WebDAV: Stores file with versioning
3. Nextcloud returns file path → Django stores in file_url field
4. Users access documents via Nextcloud UI or download via Django API
5. eTMF folder structure auto-created per study
```

**Sync Strategy:** On-demand (upload/download via API)

**API Used:** Nextcloud WebDAV + OCS API

---

### 5.4 SENAITE Integration

**Data Flow:**
```
1. Lab Tech creates samples in SENAITE
2. Lab processes samples, enters results in SENAITE
3. Django Celery task pulls results via SENAITE JSON API
4. Results stored in Django LabResult model
5. Auto-flag out-of-range values based on ReferenceRange
6. Flagged results trigger queries for Data Manager review
```

**Sync Strategy:** On-demand import + scheduled Celery pull

**API Used:** SENAITE JSON API (`/@@API/senaite/v1/`)

---

## 6. Deployment Timeline

### Phase A — Django Core (Days 1-6) — CURRENT

| Day | Focus | External Systems |
|-----|-------|-----------------|
| Day 1 ✅ | Infrastructure + 27 Models | PostgreSQL, Redis, Keycloak |
| Day 2 ✅ | Auth, RBAC, Audit, Seed Data | — |
| Day 3 🔨 | Business Logic & Workflows | — |
| Day 4 | E-signatures, DB Lock, Export | — |
| Day 5-6 | React Frontend (basic) | — |

### Phase B — External System Deployment (Days 7-14)

| Day | Focus | Container Added | RAM Added |
|-----|-------|----------------|-----------|
| Day 7 | Deploy OpenClinica CE + OC PostgreSQL | `openclinica`, `oc-postgres` | +1.5 GB |
| Day 8 | Build OpenClinica sync service | — | — |
| Day 9 | Deploy Nextcloud | `nextcloud` | +512 MB |
| Day 10 | Build Nextcloud integration (eTMF) | — | — |
| Day 11 | Deploy ERPNext + MariaDB | `erpnext`, `mariadb` | +1.5 GB |
| Day 12 | Build ERPNext integration (Ops) | — | — |
| Day 13 | Deploy SENAITE | `senaite` | +1 GB |
| Day 14 | Build SENAITE integration (Lab) | — | — |

### Phase C — Polish & Launch (Days 15-20)

| Day | Focus |
|-----|-------|
| Day 15-16 | End-to-end testing, full trial simulation |
| Day 17-18 | Security audit, performance testing |
| Day 19 | Documentation, training materials |
| Day 20 | Production deployment, go-live |

---

## 7. Resource Requirements

| Deployment Stage | Total Containers | RAM Required | Your Machine |
|-----------------|-----------------|-------------|-------------|
| Current (Phase A) | 7 | ~4.4 GB | ✅ 10 GB OK |
| + OpenClinica (Day 7) | 9 | ~5.9 GB | ✅ 10 GB OK |
| + Nextcloud (Day 9) | 10 | ~6.4 GB | ✅ 10 GB OK |
| + ERPNext (Day 11) | 12 | ~7.9 GB | ⚠️ 10 GB tight |
| + SENAITE (Day 13) | 13 | ~8.9 GB | ⚠️ 10 GB very tight |
| Production (all) | 13+ | 16-48 GB | ❌ Need server |

> **Recommendation:** Deploy on a cloud VM (16 GB minimum) or upgrade local RAM before Day 11.

---

## 8. Synchronization Strategy Summary

| Flow Type | Use Case | Implementation |
|-----------|----------|---------------|
| **Synchronous** | Study + Subject creation in OpenClinica | Django → OC API (real-time, in request) |
| **Asynchronous** | Site data → ERPNext, Lab results ← SENAITE | Celery tasks (hourly or on-demand) |
| **Event-Driven** | SAE deadline alerts, document upload | Django signals → Celery → External system |
| **Manual** | Bulk lab import, regulatory doc upload | User-triggered via API endpoint |

---

## 9. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Django is master, externals are satellites | PRD Section 13: "Django serves as the central API gateway" |
| OID fields added from Day 1 | No schema changes needed when integrating |
| Build Django logic first, integrate later | Ensures core works independently; externals enhance |
| One system at a time integration | Reduces risk, allows testing per system |
| Celery for async sync | Prevents Django API slowdown from external calls |

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| OpenClinica API limitations (PRD Risk R1) | Django has full native EDC as fallback |
| Integration complexity across 6+ systems (PRD Risk R9) | Centralized in Django orchestrator |
| Server resource contention (PRD Risk R3) | Incremental deployment, resource monitoring |
| External system downtime | Django works standalone; sync retries via Celery |

---

**Document prepared by:** HACT CTMS Development Team  
**Approved by:** Stakeholders (requirements specification period)  
**Next Action:** Proceed with Day 3 (Business Logic) → Day 7 starts external deployments
