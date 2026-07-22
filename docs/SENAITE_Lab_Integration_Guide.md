# SENAITE Laboratory Integration — End-to-End Guide (HACT CTMS)

> How the SENAITE LIMS fits into HACT CTMS: what it is, who uses it, when, how the
> data flows between systems, the exact configuration, and a concrete list of
> improvements to harden and extend the current implementation.

---

## 1. What SENAITE is and why HACT uses it

**SENAITE** is an open-source **LIMS** (Laboratory Information Management System),
built on Plone/Zope. In HACT CTMS it is the **system of record for laboratory
analysis**: sample registration, result entry by lab staff, and the formal
lab workflow (Receive → Submit → Verify → Publish) with its own audit trail.

HACT CTMS does **not** try to be a lab system. Instead it:

- keeps the **clinical context** (subjects, visits, studies, safety, eTMF), and
- **pulls published lab results** back from SENAITE, attaching them to the right
  subject and **auto-flagging** them High/Low/Normal against study reference ranges.

This separation means the lab runs its normal, regulated LIMS process, while the
study team sees clean, flagged results inside the CTMS without re-keying data.

---

## 2. Who uses it, and when

| Actor | System they touch | What they do |
|---|---|---|
| **Lab technician / analyst** | SENAITE UI | Register sample, receive it, enter results, submit |
| **Lab supervisor** | SENAITE UI | Verify and Publish results (releases them) |
| **CTMS Lab Manager** (`lab_manager` role) | CTMS `/lab` | Review synced results, manage reference ranges, CSV import, sample tracking |
| **Data Manager / Study Admin** (`data_manager`, `study_admin`, `admin`) | CTMS | Same lab access as Lab Manager (superset roles) |
| **Monitor / Auditor** | CTMS (read-only) | Review lab data / audit trail |
| **System (Celery beat)** | both | Every 15 min, pulls published results SENAITE → CTMS |

**When it is used in the study lifecycle:** after a subject visit where a biological
sample (e.g. blood) is collected. The sample is registered and analyzed in SENAITE;
once results are **Published**, they appear in CTMS on the **Laboratory** page and
are available to Safety/Monitoring workflows (e.g. an abnormally high CRP can support
an adverse-event assessment).

**CTMS access control:** all `/api/v1/lab/*` endpoints require the **`lab_manager`**
role (or `study_admin`/`admin`). See `backend/core/permissions.py → IsLabManager`.

---

## 3. Architecture — how SENAITE interacts with the other systems

```
                       ┌──────────────────────────────────────────────┐
                       │                 HACT CTMS                     │
                       │  Django API + React frontend + Celery         │
                       │                                               │
   Lab staff           │   /lab  (LabResult, ReferenceRange,           │
   (browser)           │          SampleCollection)                    │
      │                │        ▲                    ▲                 │
      │ SENAITE UI     │        │ pull (every 15m)   │ CSV import      │
      ▼                │        │ + on-demand        │ (manual)        │
┌───────────────┐  REST │   ┌────┴─────────────┐                       │
│   SENAITE     │◀──────┼───│ integrations/    │                       │
│   LIMS        │  JSON  │   │ senaite.py       │                       │
│ (Plone/Zope)  │───────┼──▶│ tasks.py         │                       │
│  ZODB          │       │   └──────────────────┘                       │
└───────────────┘       └──────────────────────────────────────────────┘
        ▲                         │  (subject_identifier == SENAITE ClientSampleID)
        │                         ▼
   published results     Keycloak (SSO)  ·  OpenClinica (EDC)  ·  Nextcloud (eTMF)
                          ERPNext (ops)   — sibling integrations, same pattern
```

Key interaction facts:

- **Transport:** SENAITE JSON API (`<host>/senaite/@@API/senaite/v1/...`) over HTTP
  Basic Auth. Reverse-proxied by NGINX under `/senaite/` (with a VirtualHostMonster
  rewrite so Plone emits correct HTTPS asset URLs).
- **The join key** between the two systems is the **subject identifier**:
  CTMS `Subject.subject_identifier` **==** SENAITE `AnalysisRequest.ClientSampleID`.
- **Client scoping:** results are pulled for the SENAITE Client titled
  **"HACT Clinical Trials"** (currently hard-coded — see improvements).
- **Relationship to other integrations:** SENAITE is one of four external systems
  (OpenClinica, Nextcloud, ERPNext, SENAITE) orchestrated by the `integrations` app.
  They share the same health-check + Celery pattern and the Integrations dashboard.

---

## 4. End-to-end workflows

### 4A. Primary flow — lab results from SENAITE into CTMS

1. **Sample collected** at a visit for a subject (e.g. `E2E-212727`).
2. **Register the sample in SENAITE** (lab user, SENAITE UI): create an
   *Add Sample* / AnalysisRequest under Client **HACT Clinical Trials**, set the
   **Client Sample ID = the CTMS subject identifier**, pick the sample type
   (e.g. Blood) and the analyses (CRP, Hemoglobin, WBC, Platelet…).
3. **Receive** the sample → **enter results** → **Submit**.
4. **Verify** → **Publish** (supervisor). Publishing is what makes results
   visible to CTMS (`review_state == "published"`).
5. **CTMS pulls** the results:
   - **instantly via webhook** — when SENAITE publishes, it POSTs to
     `POST /api/v1/integrations/senaite/webhook/results-published/` and CTMS
     kicks off an immediate pull (see §4D), *or*
   - automatically every **15 minutes** (Celery beat task
     `integrations.pull_results_from_senaite`, kept as a safety-net fallback), *or*
   - **on demand** via the **Sync from SENAITE** button on `/lab`
     (`POST /api/v1/integrations/senaite/pull-results/`).
6. For each published analysis, CTMS:
   - maps `ClientSampleID` → `Subject`,
   - creates a `LabResult` (test name, value, unit, date),
   - **auto-flags** H/L/N using the study `ReferenceRange` (matched by test name),
   - skips duplicates `(subject, test_name, result_value)`.
7. Result appears on **CTMS → Laboratory** (`/lab`) with the flag badge.

**How the pull actually reads SENAITE (important detail):** an AnalysisRequest's
`Analyses` field in the JSON API only returns *reference stubs* (`url/uid/api_url`),
**not** the values. So the pull queries the **`Analysis`** objects directly
(`review_state=published`, which expose `getResult`, `title`, `getUnit`,
`getRequestID`) and **joins them back** to the published sample to recover the
`ClientSampleID`. (This was a bug that made the pull import zero rows — now fixed.)

### 4B. Secondary flow — manual CSV import (no SENAITE needed)

For labs that email a spreadsheet, CTMS supports bulk import:

- **UI:** `/lab` → **Import CSV** button.
- **API:** `POST /api/v1/lab/results/import-csv/` (multipart: `file`, `study`).
- **Required columns:** `subject_identifier, test_name, result_value, unit, result_date`.
- Same auto-flagging against reference ranges; rows for unknown subjects are reported as errors.

### 4C. Push CTMS sample → SENAITE (now wired)

A coordinator can register a sample **inside CTMS** instead of re-keying it in
SENAITE:

- **UI:** `/lab` → **Register Sample** (choose subject, sample type, collection
  date). Registered samples appear on the **Samples** tab with a live status and
  their SENAITE ID once linked.
- **API:** `POST /api/v1/lab/samples/`.
- **What happens:** a `post_save` signal (`lab/signals.py`) dispatches
  `integrations.sync_sample_to_senaite`, which calls `create_sample()` to create
  the AnalysisRequest under the study's SENAITE Client and writes the returned
  `senaite_sample_id` back onto the `SampleCollection` (guarded so it never
  double-pushes). The lab then receives/analyses/publishes it in the SENAITE UI,
  and results flow back per §4A.

### 4D. Results-published webhook (low-latency alternative to polling)

Instead of waiting up to 15 minutes for the beat, SENAITE can notify CTMS the
moment a sample is published:

- **Endpoint:** `POST /api/v1/integrations/senaite/webhook/results-published/`
- **Auth:** shared secret in the `X-SENAITE-Token` header, compared against
  `SENAITE_WEBHOOK_SECRET` (an authenticated CTMS session is also accepted). If
  no secret is configured the endpoint fails closed (requires auth).
- **Body:** `{ "senaite_sample_id": "WS-0001", "status": "published" }` — the
  sample id is optional; a bare `{"status":"published"}` still triggers a pull.
- **Effect:** marks the linked `SampleCollection` completed *and* dispatches
  `pull_results_from_senaite` immediately (scoped to that sample's study when
  known). The 15-min beat remains as a fallback in case a webhook is missed.

**Wiring SENAITE to send it:** Plone/SENAITE has no built-in outbound webhooks.
A ready-to-deploy **host-side notifier** is shipped for this — see
`deploy/senaite-webhook-notifier/` (a small Python-stdlib script + systemd
timer/cron that polls SENAITE for newly-published samples every ~60s and calls
this webhook with the `X-SENAITE-Token` header). Alternatives if you prefer to
run inside SENAITE itself:
  1. a **Content Rule** (Site Setup → Content Rules) triggered on the publish
     transition that calls an external URL (via a small add-on/action), or
  2. a lightweight **event subscriber** add-on for the `AnalysisRequest`
     published event that POSTs to the endpoint.
Until one of these is running, the on-demand **Sync** button and the 15-min beat
fallback keep results flowing.

---

## 5. Configuration & deployment

**Container** (`docker-compose.yml`, profile `senaite`):

- image `senaite/senaite:2.x`, container `hact-senaite`, storage = ZODB volume `hact-senaite-data`.
- local port `127.0.0.1:8081 → 8080`; public access via NGINX `/senaite/`.

**NGINX** (`nginx/nginx.conf`) — the `/senaite/` block must advertise the external
scheme/port to Plone, otherwise the UI breaks with mixed-content over HTTPS:

```nginx
rewrite ^/senaite/(.*) /VirtualHostBase/https/$host:443/senaite/VirtualHostRoot/_vh_senaite/$1 break;
```

**Environment variables** (CTMS container `.env`):

| Var | Purpose | Note |
|---|---|---|
| `SENAITE_URL` | Base URL to SENAITE | e.g. `http://hact-senaite:8080`. Code auto-appends the Plone site id if the URL has no path. |
| `SENAITE_SITE_ID` | Plone site id | defaults to `senaite` → API base becomes `.../senaite/@@API/senaite/v1` |
| `SENAITE_API_USER` | API user | must be a real SENAITE member with lab View/Verify perms |
| `SENAITE_API_PASSWORD` | API password | **must exactly match** that user's SENAITE password |
| `SENAITE_WEBHOOK_SECRET` | Shared secret for the inbound results-published webhook | sent by SENAITE as the `X-SENAITE-Token` header; if unset the webhook fails closed |

> ⚠️ **Auth gotcha:** with HTTP Basic auth, a **wrong password does not 401** — Plone
> silently treats the request as **Anonymous** (still HTTP 200), and Anonymous sees
> **no** lab data, so every search returns 0. The health check can still read
> "healthy" (a false positive). Always confirm with the diagnostic endpoint below.
> Docker only reads `.env` on **container recreate**:
> `docker compose up -d --force-recreate django-api celery-worker celery-beat`.

**Scheduled tasks** (`backend/hact_ctms/settings.py → CELERY_BEAT_SCHEDULE`):

- `pull-senaite-results-every-15-min` → `integrations.pull_results_from_senaite` (900 s)
- `check-senaite-health-every-10-min` → `integrations.check_senaite_health` (600 s)

---

## 6. CTMS data model (lab schema)

| Model | Table | Purpose | Key fields |
|---|---|---|---|
| `LabResult` | `lab_results` | One imported/entered test result | `subject`, `test_name`, `result_value`, `unit`, `reference_range_low/high`, `flag` (H/L/N), `result_date`, `imported_by`, `senaite_sample_id`, `senaite_analysis_uid` |
| `ReferenceRange` | `lab_reference_ranges` | Per-study normal range for flagging | `study`, `test_name`, `gender`, `age_lower/upper`, `range_low`, `range_high` |
| `SampleCollection` | `lab_sample_collections` | Sample lifecycle tracking | `subject`, `senaite_sample_id`, `collection_date`, `sample_type`, `status` |

---

## 7. Reference ranges & auto-flagging

- Create ranges per study (`POST /api/v1/lab/reference-ranges/`, or the UI).
- **The `test_name` must match SENAITE's analysis title** (e.g.
  `C-Reactive Protein (CRP)`), because matching is done case-insensitively on the name.
- Flag logic: `value < range_low → L`, `value > range_high → H`, else `N`.
- Example that validated the flow: CRP range `0–5 mg/L`; a published result of
  `12.5` → flagged **H (High)** in CTMS.

---

## 8. Current status & recommended improvements ("make it more")

### What works today ✅
- SENAITE UI lab workflow (setup → sample → results → Receive/Submit/Verify/Publish).
- **CTMS → SENAITE sample push** on `SampleCollection` creation (Register Sample UI).
- **Results-published webhook** for instant pulls, with the 15-min beat as fallback.
- Scheduled + on-demand + webhook pull of **published** results, correct subject
  mapping, idempotent import (Analysis UID), real result dates, and H/L/N flagging.
- **Per-study SENAITE Client** (`Study.senaite_client_title`).
- Manual CSV import path.
- Health monitoring and an Integrations status dashboard.

### Is the SENAITE UI "sufficient"? — division of labour
Yes for the **lab-side** work: receiving, entering results, and Verify/Publish are
regulated lab actions and belong in SENAITE — do **not** rebuild them in CTMS.
What *did* belong in CTMS was **sample registration** (the coordinator's action)
and **result review** — both now covered by the `/lab` Register Sample + Samples
tab and the results grid, so no double data-entry is needed to start a sample.

### Remaining gaps and hardening opportunities 🔧

1. **Link results to the visit.** `LabResult.subject_visit` is left null on pull.
   Map SENAITE sample metadata (e.g. Client Order / date) to the correct
   `SubjectVisit` so results roll up per visit.

2. **Use full reference-range stratification.** The pull now prefers the
   `gender='all'` range (deterministic), but `gender`/`age` columns are otherwise
   unused because CTMS `Subject` carries no sex/DOB. Add those demographics to
   match age/sex-specific ranges precisely.

3. **Publishing needs SMTP.** In SENAITE, "Publish" is an email-distribution step.
   Without a MailHost the email send fails (the sample still transitions to
   published in our environment, but this is fragile). Configure an SMTP relay
   and the Plone/SENAITE "From" address for a clean, auditable publish + report PDF.

4. **Security / least privilege.** Use a **dedicated SENAITE LabManager service
   account** (not the shared `admin`) with a strong password stored only in `.env`
   / a secret manager. Rotate credentials; never commit them.

5. **Coding standards for results.** Add LOINC/analysis-code mapping and unit
   normalization so results are interoperable and comparisons are unit-safe.

6. **Observability.** Surface last-successful-pull time, imported/skipped counts,
   and auth identity on the Integrations dashboard (the pull endpoint already
   returns these) so operators can spot silent failures early.

7. **Native SENAITE outbound webhook.** We provide the inbound endpoint (§4D)
   *and* a host-side notifier bridge (`deploy/senaite-webhook-notifier/`) that
   calls it within ~60s of publishing — no SENAITE code changes needed. A true
   in-process event subscriber (fires on the publish event itself) remains a
   possible future refinement.

> **Now shipped (previously gaps):** CTMS→SENAITE sample push, inbound
> results-published webhook + immediate pull, per-study Client, Analysis-UID
> idempotency, and real result-date parsing.

---

## 9. Troubleshooting (issues we actually hit)

| Symptom | Root cause | Fix |
|---|---|---|
| SENAITE UI unstyled / JS dead over HTTPS | NGINX VHM advertised `http/80` | VHM rewrite → `https/$host:443`; force-recreate nginx on deploy |
| Pull imports 0, but SENAITE has published results | AR `Analyses` field returns only reference stubs | Query `Analysis` objects and join by `getRequestID` |
| Search returns 200 but 0 items | `SENAITE_URL` missing Plone site path → hit Zope root catalog | Append site id → `.../senaite/@@API/senaite/v1` (`SENAITE_SITE_ID`) |
| `current_user: Anonymous`, 0 results, health "healthy" | Wrong `SENAITE_API_PASSWORD` (Basic auth silently downgrades to Anonymous) | Set password to the real member password; recreate containers |
| Publish "Failed to send Email(s)" | No SMTP/MailHost + missing "From" address | Configure SMTP + Plone "From" (sample may still transition to published) |

**Diagnostic endpoint** (auth as a Lab Manager):

```
POST /api/v1/integrations/senaite/pull-results/    body: {"study_id": <id>}
```

Returns the configured SENAITE URL/user, the authenticated identity
(`current_user`), raw AR/Analysis search counts, a preview of fetched results,
and the import outcome — the fastest way to tell auth vs. URL vs. mapping issues apart.

---

## 10. Quick reference

**CTMS lab endpoints**

- `GET/POST /api/v1/lab/results/` — list/create lab results (role: `lab_manager`)
- `POST /api/v1/lab/results/import-csv/` — CSV bulk import
- `GET/POST /api/v1/lab/reference-ranges/` — reference ranges
- `GET/POST /api/v1/lab/samples/` — sample tracking (POST auto-pushes to SENAITE)
- `POST /api/v1/integrations/senaite/pull-results/` — trigger pull + diagnostics
- `POST /api/v1/integrations/senaite/webhook/results-published/` — SENAITE event
  hook (auth: `X-SENAITE-Token` = `SENAITE_WEBHOOK_SECRET`); marks sample complete
  + triggers an immediate pull
- `GET  /api/v1/integrations/status/` — health of all external systems

**SENAITE (direct)**

- UI: `https://<host>/senaite/`
- JSON API base: `https://<host>/senaite/@@API/senaite/v1/`
- Common searches: `search?portal_type=AnalysisRequest&review_state=published&complete=yes`,
  `search?portal_type=Analysis&review_state=published&complete=yes`

**Deploy note:** environment/credential changes require
`docker compose up -d --force-recreate django-api celery-worker celery-beat`.
