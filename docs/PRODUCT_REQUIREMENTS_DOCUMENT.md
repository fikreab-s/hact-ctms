# HACT Clinical Trial Management System (CTMS)
# Product Requirements Document

**Organization:** Horn of Africa Clinical Trials (HACT) — [hacts.org](https://hacts.org)
**Document Version:** 1.0
**Date:** March 21, 2026
**Status:** Draft — Pending Stakeholder Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Goals](#3-product-vision--goals)
4. [Scope & Boundaries](#4-scope--boundaries)
5. [HACT Core Services](#5-hact-core-services)
6. [Clinical Trial Lifecycle](#6-clinical-trial-lifecycle)
7. [User Roles & Personas](#7-user-roles--personas)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [System Architecture](#10-system-architecture)
11. [Open-Source Technology Stack](#11-open-source-technology-stack)
12. [Database Design](#12-database-design)
13. [Integration Architecture](#13-integration-architecture)
14. [Infrastructure & Deployment](#14-infrastructure--deployment)
15. [Security & Compliance](#15-security--compliance)
16. [Development Phases & Roadmap](#16-development-phases--roadmap)
17. [Risk Assessment](#17-risk-assessment)
18. [Success Metrics](#18-success-metrics)
19. [Appendices](#19-appendices)

---

## 1. Executive Summary

HACT (Horn of Africa Clinical Trials) requires a comprehensive, open-source Clinical Trial Management System (CTMS) to manage the full lifecycle of clinical research — from protocol design through data collection, safety monitoring, regulatory compliance, and final dataset export for statistical analysis.

This PRD defines the requirements, architecture, and development roadmap for building the HACT CTMS using a composable open-source stack. The system combines **OpenClinica Community Edition** (for electronic data capture and clinical data management) with **custom Django/React modules** (for study operations, safety dashboards, regulatory document management, and lab integration), orchestrated through a unified platform that leverages **Keycloak** (identity management), **ERPNext** (operational management), **SENAITE** (laboratory information), and **Nextcloud** (document management).

### Key Objectives
- **100% Open Source**: No proprietary licensing costs; full control over code and data
- **Regulatory Compliance**: ICH-GCP, 21 CFR Part 11, CDISC/SDTM standards support
- **Unified Platform**: Single-login experience across all clinical operations
- **Data Integrity**: Complete audit trail, database lock/snapshot, data validation
- **Scalability**: Support multiple concurrent studies, thousands of subjects, multiple sites

---

## 2. Problem Statement

HACT currently lacks an integrated digital system for managing clinical trials. Without a CTMS, the organization faces:

- **Fragmented Data**: Clinical data scattered across spreadsheets, paper CRFs, and disconnected tools
- **Compliance Risk**: No systematic audit trail, making regulatory inspections challenging
- **Inefficient Workflows**: Manual processes for adverse event reporting, query management, and data cleaning
- **No Data Standards**: Difficulty producing CDISC-compliant datasets for regulatory submissions
- **Limited Visibility**: No real-time dashboards for enrollment progress, safety signals, or study milestones

### Current State
| Area | Current Approach | Problem |
|------|-----------------|---------|
| Data Collection | Paper CRFs / Excel | No validation, no audit trail |
| Safety Reporting | Manual email/fax | Missed deadlines, incomplete reports |
| Lab Data | Separate systems | No linkage to subject records |
| Regulatory Docs | File folders | Version confusion, no deadline alerts |
| Access Control | Ad-hoc | No role-based permissions |

---

## 3. Product Vision & Goals

### Vision
> A unified, open-source clinical trial platform that enables HACT to run ICH-GCP compliant trials with full data integrity, from first-patient-in to final study report — empowering clinical research in the Horn of Africa.

### Strategic Goals

| # | Goal | Measure of Success |
|---|------|-------------------|
| G1 | Digitize the complete 12-step clinical trial workflow | All 12 steps supported end-to-end in the system |
| G2 | Ensure regulatory compliance from day one | Pass a mock audit with zero critical findings |
| G3 | Reduce data management cycle time | 50% reduction in time from data entry to database lock |
| G4 | Enable real-time study oversight | Dashboards showing enrollment, queries, safety events within 24h |
| G5 | Support CDISC data standards | Successfully generate SDTM-compliant datasets |
| G6 | Achieve zero-cost licensing | 100% open-source stack with self-hosting |

---

## 4. Scope & Boundaries

### In Scope (MVP)
- Study creation, configuration, and protocol metadata management
- Multi-site and site staff management
- Subject registration, enrollment tracking, and consent management
- Electronic Case Report Form (eCRF) design, data entry, and edit checks
- Visit scheduling and tracking per protocol
- Query management (automated + manual) with resolution workflow
- Adverse Event (AE) and Serious Adverse Event (SAE) capture and reporting
- CIOMS form generation for expedited safety reports
- Lab data import, validation, and reference range management
- Database lock, snapshot, and CDISC SDTM data export
- Complete audit trail across all data changes
- Role-based access control (RBAC) with SSO via Keycloak
- Regulatory document management (eTMF) with version control
- Real-time dashboards and operational reports

### Out of Scope (Future Phases)
- Randomization and trial supply management (IRT/RTSM)
- Direct statistical analysis engine (R/SAS integration is export-based)
- Patient-facing portal / ePRO (electronic patient-reported outcomes)
- FHIR/HL7 interoperability with hospital EHR systems
- Mobile offline data capture for remote sites
- AI/ML-powered safety signal detection
- Multi-language interface localization

---

## 5. HACT Core Services

The CTMS must support five core service domains that define HACT's clinical research operations:

### 5.1 Trial Planning
| Capability | Description | System Component |
|-----------|-------------|-----------------|
| Protocol Management | Define study objectives, endpoints, inclusion/exclusion criteria, treatment arms, visit schedules | Custom Django module |
| CRF Design | Create electronic forms to capture data per protocol | OpenClinica CRF Builder |
| Site Selection & Initiation | Identify sites, manage contracts, train staff | ERPNext + Custom Django |
| Randomization Planning | Plan drug allocation and inventory | Future phase |

### 5.2 Data Management
| Capability | Description | System Component |
|-----------|-------------|-----------------|
| Electronic Data Capture | eCRF data entry with real-time validation | OpenClinica |
| Query Management | Automated edit checks, manual queries, resolution workflow | OpenClinica |
| Medical Coding | MedDRA / WHO Drug dictionary mapping | OpenClinica |
| Data Review & Cleaning | Dashboards for missing data, discrepancies, query status | Custom React dashboards |
| Database Lock | Controlled lock process with immutable snapshot | OpenClinica + Custom |

### 5.3 Pharmacovigilance
| Capability | Description | System Component |
|-----------|-------------|-----------------|
| AE/SAE Capture | Structured entry of adverse events with seriousness criteria | OpenClinica (basic) + Custom safety module |
| CIOMS Form Generation | Auto-generate CIOMS I forms from SAE data | Custom Django module |
| Expedited Reporting | Track and enforce regulatory submission deadlines | Custom safety dashboard |
| Safety Signal Review | Aggregate safety data review, DSUR preparation | Custom reporting module |

### 5.4 Regulatory Affairs
| Capability | Description | System Component |
|-----------|-------------|-----------------|
| Document Repository | Store regulatory submissions with version control | Nextcloud |
| Submission Tracking | Track IRB/EC and health authority submissions | Custom Django module |
| Approval Management | Record approval dates, conditions, renewal deadlines | Custom with alerts |
| Inspection Readiness | Maintain eTMF with audit-ready regulatory file | Nextcloud + Custom metadata |

### 5.5 Laboratory / Biomarker Services
| Capability | Description | System Component |
|-----------|-------------|-----------------|
| Sample Tracking | Record collection, processing, shipping of biological samples | SENAITE LIMS |
| Lab Data Import | Import results from central/local labs via file or API | Custom import engine |
| Reference Range Management | Lab-specific ranges for result interpretation | Custom Django module |
| Result Validation | Flag out-of-range values, auto-generate queries | Custom validation rules |

---

## 6. Clinical Trial Lifecycle

The CTMS must support the complete 12-step clinical trial lifecycle:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HACT CLINICAL TRIAL LIFECYCLE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐    │
│  │ 1. Study  │──▶│ 2. eCRF  │──▶│ 3. Site  │──▶│ 4. Regulatory│    │
│  │ Planning  │   │  Design  │   │  Setup   │   │   Approval   │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘    │
│       │                                              │              │
│       ▼                                              ▼              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐    │
│  │ 5. Subj. │──▶│ 6. Visit │──▶│ 7. Data  │──▶│ 8. Validation│    │
│  │ Enroll.  │   │ Schedule │   │ Collect. │   │   & Queries  │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘    │
│       │                                              │              │
│       ▼                                              ▼              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐    │
│  │ 9. Med   │──▶│10. Safety│──▶│11. DB    │──▶│ 12. Archive  │    │
│  │  Coding  │   │ Monitor  │   │  Lock    │   │  & Report    │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────────┘    │
│                                                                     │
│  ━━━━CTMS Directly Supports━━━━  ━━Export to R/SAS━━  ━━Manual━━   │
│  Steps 1-9 (Full Support)        Steps 10-11 (Partial) Step 12     │
└─────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step System Support

| Step | Process | Primary Actors | System Support |
|------|---------|---------------|----------------|
| 1. Protocol Definition | Create study protocol, objectives, eligibility, visit schedule | Study Lead, Clinical Scientist | Custom Django module for protocol metadata |
| 2. eCRF Design | Design electronic Case Report Forms | Data Manager, Study Lead | OpenClinica CRF Builder + Custom metadata storage |
| 3. Site Selection & Setup | Identify sites, initiate, train staff | Clinical Ops, Site Coordinator | ERPNext CRM + Custom Django site module |
| 4. Regulatory Submission | Submit to IRB/EC and health authorities, track approvals | Regulatory Affairs | Custom document management + Nextcloud |
| 5. Subject Enrollment | Screen, consent, enroll participants | Site Coordinator, Investigator | OpenClinica subject management + Custom consent tracking |
| 6. Visit Scheduling | Schedule and perform visits per protocol | Site Coordinator, Investigator | OpenClinica visit tracking |
| 7. Data Collection | Enter clinical data into eCRFs, import lab results | Site Coordinator, Lab Tech | OpenClinica data entry + Custom lab import |
| 8. Data Validation | Run edit checks, generate and resolve queries | Data Manager, Site Coordinator | OpenClinica query module |
| 9. Medical Coding | Map terms to MedDRA/WHO Drug | Medical Coder | OpenClinica coding tools |
| 10. Safety Monitoring | Review AEs, generate CIOMS forms, track deadlines | Safety Officer | OpenClinica AE forms + Custom safety dashboard |
| 11. Database Lock & Export | Clean data, lock database, export for analysis | Data Manager | OpenClinica lock + CDISC export |
| 12. Archive | Long-term retention per regulatory requirements | System Admin | Nextcloud archival + Custom metadata |

---

## 7. User Roles & Personas

### Role Matrix

| Role | Description | System Access |
|------|-------------|--------------|
| **System Administrator** | Infrastructure, user accounts, system settings | Full admin access: Keycloak, Django Admin, OpenClinica Admin, all systems |
| **Study Lead / PI** | Oversees study; scientific integrity | View all data (OpenClinica); approve milestones (Custom) |
| **Data Manager** | Data quality, cleaning, validation, lock | OpenClinica data management; create queries; run exports; initiate lock |
| **Clinical Research Associate (CRA)** | Monitors sites, source data verification | Read-only site data (OpenClinica); monitoring notes (Custom) |
| **Site Coordinator** | Recruits subjects, primary data entry | Add/edit own site data (OpenClinica); respond to queries |
| **Investigator** | Responsible for site conduct, data sign-off | View all site data; approve eCRFs (OpenClinica) |
| **Lab Technician** | Enters or uploads lab results | Limited lab data entry (OpenClinica/SENAITE) |
| **Safety Officer** | Reviews AEs, generates safety reports | Safety data (OpenClinica); custom safety dashboard; CIOMS generation |
| **Regulatory Affairs Manager** | Manages submissions and approvals | Custom document repository; submission tracking; deadline alerts |
| **Statistician** | Requires locked data for analysis | Read-only OpenClinica exports; custom data request portal |
| **Auditor / Inspector** | Reviews system and data for compliance | Read-only access to all data and audit trails |

### SSO Role Mapping (Keycloak → All Systems)

| Keycloak Role | OpenClinica | Nextcloud Group | ERPNext Role | SENAITE Role |
|--------------|-------------|-----------------|-------------|-------------|
| `site_coordinator` | Coordinator | Sites | Site User | Lab Technician |
| `data_manager` | DataManager | Data Mgmt | Data Manager | LIMS Admin |
| `safety_officer` | SafetyOfficer | Safety | — | — |
| `regulatory_manager` | — | Regulatory | — | — |
| `system_admin` | Admin | Admin | Admin | Admin |

---

## 8. Functional Requirements

### 8.1 Study Management (Custom Django + ERPNext)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-SM-01 | Study Creation | P0 | Create new studies with protocol number, phase, sponsor, dates, status |
| FR-SM-02 | Visit Schedule Definition | P0 | Define visit windows with day offsets and allowed CRFs per visit |
| FR-SM-03 | CRF Configuration Metadata | P0 | Store CRF design metadata linking to OpenClinica form definitions |
| FR-SM-04 | Study Milestone Tracking | P1 | Track key dates: FPI, LPO, DBL with planned vs actual |
| FR-SM-05 | Study Status Management | P0 | Support statuses: planned → active → locked → archived |

### 8.2 Site Management (Custom Django + ERPNext)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-SI-01 | Site Registration | P0 | Register sites with code, address, country, PI, activation date |
| FR-SI-02 | Site Contact Management | P0 | Maintain contact list with roles (coordinator, investigator, pharmacist) |
| FR-SI-03 | Contract Management | P1 | Track site contracts with start/end dates, budget, and linked documents |
| FR-SI-04 | Training Record Management | P1 | Log staff training (GCP, protocol) with certificates and dates |
| FR-SI-05 | Site Status Dashboard | P0 | Real-time view of site activation status and enrollment performance |

### 8.3 Participant Management (OpenClinica + Custom)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-PM-01 | Subject Registration | P0 | Register subjects with study/site assignment, generate USUBJID |
| FR-PM-02 | Enrollment Tracking | P0 | Track enrollment status: screened → enrolled → completed → withdrawn |
| FR-PM-03 | Consent Management | P1 | Record consent date, version, re-consents with audit trail |
| FR-PM-04 | Subject Timeline View | P1 | Visual timeline showing visits, events, and data completion per subject |

### 8.4 Data Collection & Management (OpenClinica)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-DC-01 | eCRF Data Entry | P0 | User-friendly electronic forms with field-level validation |
| FR-DC-02 | Edit Checks | P0 | Automated cross-field and cross-form validation rules |
| FR-DC-03 | Query Generation | P0 | System-generated and manual queries for data discrepancies |
| FR-DC-04 | Query Resolution Workflow | P0 | Query lifecycle: open → answered → closed, with notifications |
| FR-DC-05 | Medical Coding | P1 | MedDRA and WHO Drug dictionary integration |
| FR-DC-06 | Data Review Dashboard | P0 | Views for missing data, pending queries, form completion rates |

### 8.5 Safety Reporting (OpenClinica + Custom)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-SR-01 | AE/SAE Capture | P0 | Structured entry with term, dates, severity, causality, outcome |
| FR-SR-02 | Seriousness Assessment | P0 | Auto-check serious criteria (death, life-threatening, hospitalization) |
| FR-SR-03 | CIOMS Form Generation | P0 | Auto-generate CIOMS I PDF from SAE data |
| FR-SR-04 | Expedited Reporting Tracker | P0 | Track regulatory submission deadlines with alerts |
| FR-SR-05 | Safety Dashboard | P1 | Aggregate view: AE frequency, SAE timeline, signal detection |
| FR-SR-06 | DSUR Data Preparation | P2 | Compile data for Development Safety Update Reports |

### 8.6 Laboratory Integration (SENAITE + Custom)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-LI-01 | Sample Registration | P1 | Record sample collection linked to subject and visit |
| FR-LI-02 | Lab Result Import | P0 | Import results from files (CSV) or SENAITE API |
| FR-LI-03 | Reference Range Management | P1 | Define study-specific normal ranges by test, gender, age |
| FR-LI-04 | Out-of-Range Flagging | P0 | Auto-flag abnormal results (H/L/N) |
| FR-LI-05 | Lab Data Dashboard | P1 | Completeness tracking, turnaround times, flagged results |

### 8.7 Regulatory Document Management (Nextcloud + Custom)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-RD-01 | Document Upload & Storage | P0 | Upload regulatory documents with metadata and version control |
| FR-RD-02 | Submission Tracking | P0 | Track submissions to IRB/EC and health authorities |
| FR-RD-03 | Approval Record Management | P0 | Record approval dates, conditions, and expiry dates |
| FR-RD-04 | Deadline Alerts | P1 | Automated notifications for upcoming renewals and deadlines |
| FR-RD-05 | eTMF Organization | P2 | Organize docs per TMF Reference Model structure |

### 8.8 Database Lock & Export (OpenClinica + Custom)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-DL-01 | Pre-Lock Checklist | P0 | Verify all queries resolved, forms complete before lock |
| FR-DL-02 | Database Lock | P0 | Freeze data — prevent further edits with audit entry |
| FR-DL-03 | Snapshot Creation | P0 | Create immutable point-in-time data snapshot |
| FR-DL-04 | SDTM Export | P1 | Export locked data in CDISC SDTM format |
| FR-DL-05 | Export Logging | P0 | Record all exports with parameters, user, timestamp |

### 8.9 Audit & Compliance (All Systems)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-AU-01 | Clinical Data Audit Trail | P0 | Every change to clinical data logged with who/when/old/new values |
| FR-AU-02 | Operational Audit Trail | P0 | All user actions in custom modules logged |
| FR-AU-03 | Unified Audit Viewer | P1 | Aggregate audit logs from all systems in one view |
| FR-AU-04 | Audit Trail Export | P1 | Export audit logs for regulatory inspections |

### 8.10 Reporting & Dashboards (Custom React)

| ID | Requirement | Priority | Description |
|----|------------|----------|-------------|
| FR-RP-01 | Enrollment Dashboard | P0 | Real-time enrollment progress by study, site, timeline |
| FR-RP-02 | Data Quality Dashboard | P0 | Query counts, missing data, form completion rates |
| FR-RP-03 | Safety Overview | P1 | AE summary tables, SAE timeline, CIOMS submission status |
| FR-RP-04 | Site Performance | P1 | Enrollment rate, query response time, data entry timeliness |
| FR-RP-05 | Custom Report Builder | P2 | Ad-hoc report generation with filters and export |

---

## 9. Non-Functional Requirements

| ID | Requirement | Specification | Implementation Strategy |
|----|------------|---------------|------------------------|
| NFR-01 | **Security** | TLS 1.3 for all traffic; AES-256 encryption at rest; MFA via Keycloak | Nginx reverse proxy with TLS; PostgreSQL encryption; Keycloak 2FA |
| NFR-02 | **Audit Trail Integrity** | Immutable, timestamped, non-repudiable logs | OpenClinica audit trails; append-only audit tables in custom DB |
| NFR-03 | **Regulatory Compliance** | ICH-GCP E6(R2), 21 CFR Part 11 (electronic signatures), GDPR/DPA | Electronic signature workflow; validation documentation; SOPs |
| NFR-04 | **Data Integrity** | Referential integrity, validation constraints, regular backups | PostgreSQL foreign keys; Django model validators; nightly pg_dump |
| NFR-05 | **Scalability** | Support 10+ concurrent studies, 10,000+ subjects | Horizontal scaling; async task queues (Celery); database indexing |
| NFR-06 | **Availability** | 99.5% uptime; safety functions 24/7 | Docker with restart policies; health monitoring; failover strategy |
| NFR-07 | **Interoperability** | CDISC ODM, SDTM, CSV, JSON, E2B(R3) for safety | OpenClinica CDISC export; custom E2B generator; REST APIs |
| NFR-08 | **Usability** | < 1 hour training for site coordinators; mobile-responsive | Modern React UI with contextual help; responsive CSS |
| NFR-09 | **Performance** | < 2s page load; < 500ms API response; bulk import < 5min/1000 records | Database indexing; Redis caching; paginated queries |
| NFR-10 | **Maintainability** | Modular architecture; CI/CD; > 80% test coverage | Django apps; React components; GitHub Actions; pytest/jest |

---

## 10. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                                  │
│                    (React SPA — Custom Frontend)                        │
└─────────────────────┬────────────────────────┬──────────────────────────┘
                      │                        │
                      │  HTTPS (TLS 1.3)       │  HTTPS (TLS 1.3)
                      ▼                        ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────────┐
│        NGINX REVERSE PROXY      │ │          KEYCLOAK (IAM)             │
│    (SSL Termination, Routing)   │ │   SSO / OAuth2 / OIDC / 2FA        │
└────┬───────┬───────┬───────┬────┘ └─────────────────────────────────────┘
     │       │       │       │
     ▼       ▼       ▼       ▼
┌────────┐┌────────┐┌────────┐┌──────────┐
│ Django ││OpenCli-││ERPNext ││Nextcloud │
│ API    ││nica CE ││        ││          │
│Backend ││  (EDC) ││(Ops)   ││(eTMF/    │
│        ││        ││        ││ Docs)    │
└───┬────┘└───┬────┘└───┬────┘└────┬─────┘
    │         │         │          │         ┌──────────┐
    │         │         │          │         │ SENAITE  │
    │         │         │          │         │  (LIMS)  │
    │         │         │          │         └────┬─────┘
    ▼         ▼         ▼          ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL Cluster                     │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Custom   │ │ OpenClinica  │ │ Keycloak │ │SENAITE │ │
│  │ HACT DB  │ │    DB        │ │   DB     │ │  DB    │ │
│  └──────────┘ └──────────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
                    ┌──────────────────┐
                    │  Study Creation   │
                    │  (Custom Django)  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │   Site    │   │  eCRF    │   │Regulatory│
       │  Setup   │   │  Design  │   │ Approval │
       │(ERPNext) │   │(OpenClin)│   │(Nextcloud)│
       └────┬─────┘   └────┬─────┘   └──────────┘
            │              │
            ▼              ▼
       ┌──────────┐   ┌──────────┐
       │ Subject  │──▶│  Visit   │
       │ Enroll   │   │  Data    │
       │(OpenClin)│   │(OpenClin)│
       └────┬─────┘   └────┬─────┘
            │              │
            ├──────────────┤
            ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌──────────┐
       │   AE /   │   │Lab Result│   │  Queries │
       │   SAE    │   │ Import   │   │& Cleaning│
       │(OpenClin │   │(SENAITE →│   │(OpenClin)│
       │+ Custom) │   │ Custom)  │   │          │
       └────┬─────┘   └──────────┘   └────┬─────┘
            │                              │
            ▼                              ▼
       ┌──────────┐                  ┌──────────┐
       │  CIOMS   │                  │   DB     │
       │  Report  │                  │   Lock   │
       │ (Custom) │                  │(OpenClin)│
       └──────────┘                  └────┬─────┘
                                          │
                                          ▼
                                    ┌──────────┐
                                    │  SDTM    │
                                    │  Export  │
                                    │  → R/SAS │
                                    └──────────┘
```

---

## 11. Open-Source Technology Stack

### Core Stack Decision Matrix

| Component | Selected Tool | License | Purpose | Alternatives Considered |
|-----------|--------------|---------|---------|------------------------|
| **EDC / Clinical Data** | OpenClinica CE 4.x | LGPL 3.0 | eCRF design, data entry, queries, audit trail, DB lock | REDCap (limited API), LibreClinica (small community) |
| **Custom Backend** | Django 5.x + DRF | BSD | API gateway, orchestration, safety/regulatory/lab modules | Node.js (less mature for enterprise), FastAPI (less ecosystem) |
| **Custom Frontend** | React 18+ with Vite | MIT | Unified SPA for dashboards, safety, regulatory, admin | Vue.js, Angular |
| **Identity & Access** | Keycloak 24+ | Apache 2.0 | SSO, OAuth2/OIDC, 2FA, federated identity | Custom Django auth (less features), Authentik |
| **Operations Mgmt** | ERPNext 15+ | GPL 3.0 | Site management, contracts, milestones, CRM | Custom build (higher effort), Odoo (licensing concerns) |
| **Document Mgmt** | Nextcloud 28+ | AGPL 3.0 | eTMF, regulatory docs, version control, sharing | Alfresco (complex), custom S3 (no UI) |
| **Lab Information** | SENAITE 2.x | GPL 2.0 | Sample tracking, lab workflows, result management | Custom build (very complex), OpenLIMS |
| **Database** | PostgreSQL 16+ | PostgreSQL License | Primary data store for all components | MySQL (less features), CockroachDB (over-engineered) |
| **Cache / Queue** | Redis 7+ / Celery 5+ | BSD / BSD | Caching, async task queue, session store | RabbitMQ (heavier), Memcached (no persistence) |
| **Reverse Proxy** | Nginx | BSD-2 | SSL termination, load balancing, routing | Traefik (auto-config), HAProxy |
| **Containerization** | Docker + Docker Compose | Apache 2.0 | Consistent deployment, isolation, reproducibility | Podman, Kubernetes (future scale) |
| **CI/CD** | GitHub Actions | Free tier | Automated testing, building, deployment | GitLab CI, Jenkins |

### Why OpenClinica CE Was Chosen

> **Recommendation from CTMS Comparison & Recommendation Matrix (March 17, 2026)**

| Criterion | OpenClinica CE | REDCap | LibreClinica |
|-----------|---------------|--------|-------------|
| REST API for Integration | ★★★★★ Excellent | ★★☆☆☆ Limited | ★★★☆☆ Moderate |
| CDISC/SDTM Support | ★★★★★ Native | ★★☆☆☆ Manual | ★★★☆☆ Inherited |
| Community & Longevity | ★★★★☆ Large, active | ★★★★★ Massive (academic) | ★★☆☆☆ Small |
| Self-Hosted Docker Deployment | ★★★★★ Yes | ★★★☆☆ Complex | ★★★☆☆ Limited |
| Feature Completeness for Trials | ★★★★★ Full EDC/CDM | ★★★☆☆ Survey-focused | ★★★★☆ EDC |
| Fit for HACT Architecture | ★★★★★ Perfect | ★★☆☆☆ Poor | ★★★☆☆ Risky |

---

## 12. Database Design

### Schema Organization

The HACT custom PostgreSQL database is organized into 7 logical schemas. Clinical data resides in OpenClinica's database; this custom DB stores operational, integration, and enhanced data.

```
PostgreSQL (hact_ctms_db)
├── auth        → Users, roles, permissions, external identity mappings
├── clinical    → Study metadata, visit schedules, CRF definitions (links to OpenClinica)
├── ops         → Sites, contacts, contracts, training records, milestones
├── safety      → SAE tracking, CIOMS forms, safety reviews (enhances OpenClinica)
├── lab         → Sample collections, lab results cache, reference ranges
├── outputs     → Export logs, data quality reports, SDTM mapping metadata
└── audit       → Operational audit trail (clinical audit in OpenClinica)
```

### Key Entity Relationships

```
auth.users ─────────────────────┐
    ├── auth.user_roles         │
    │      └── auth.roles       │
    └── auth.external_system_   │
           identities           │
                                │
clinical.studies ───────────────┤
    ├── clinical.visit_schedules│
    ├── clinical.crf_definitions│
    ├── ops.milestones ─────────┤
    ├── safety.serious_adverse_ │
    │      events               │
    │      └── safety.cioms_    │
    │            forms          │
    ├── safety.safety_reviews   │
    ├── lab.reference_ranges    │
    ├── outputs.export_logs     │
    └── outputs.data_quality_   │
           reports              │
                                │
ops.sites ──────────────────────┤
    ├── ops.site_contacts       │
    ├── ops.contracts           │
    ├── ops.training_records    │
    └── ops.milestones          │
                                │
lab.sample_collections ─────────┘
    └── lab.lab_results
```

### Key Tables Summary

| Schema | Table | Primary Purpose | Key Foreign Links |
|--------|-------|----------------|-------------------|
| `auth` | `users` | Local mapping of Keycloak users | — |
| `auth` | `roles` | Cached Keycloak roles | — |
| `auth` | `user_roles` | Many-to-many user↔role | `users`, `roles` |
| `auth` | `external_system_identities` | Maps users to IDs in OpenClinica, SENAITE, etc. | `users` |
| `clinical` | `studies` | Study metadata + OpenClinica OID link | — |
| `clinical` | `visit_schedules` | Visit windows per study | `studies` |
| `clinical` | `crf_definitions` | CRF metadata + OpenClinica OID link | `studies` |
| `ops` | `sites` | Site profiles + ERPNext ID link | — |
| `ops` | `site_contacts` | Site staff directory | `sites` |
| `ops` | `contracts` | Site contracts with document links | `sites` |
| `ops` | `training_records` | Staff GCP/protocol training logs | `sites` |
| `ops` | `milestones` | Study/site milestone tracking | `studies`, `sites` |
| `safety` | `serious_adverse_events` | SAE cache from OpenClinica for enhanced tracking | `studies` |
| `safety` | `cioms_forms` | Generated CIOMS I forms with submission tracking | `serious_adverse_events` |
| `safety` | `safety_reviews` | DSUR and safety committee records | `studies` |
| `lab` | `sample_collections` | Sample tracking linked to SENAITE | — |
| `lab` | `lab_results` | Cached results from SENAITE | `sample_collections` |
| `lab` | `reference_ranges` | Study-specific normal value ranges | `studies` |
| `outputs` | `export_logs` | Record of all data exports | `studies`, `users` |
| `outputs` | `data_quality_reports` | Generated DQ report metadata | `studies` |
| `audit` | `audit_logs` | Comprehensive operational audit trail | `users` |

---

## 13. Integration Architecture

### Django as Central Orchestrator

The Django backend serves as the **central API gateway** — all React frontend requests route through Django, which then dispatches to the appropriate downstream system.

```
┌──────────────┐
│    React     │
│   Frontend   │
└──────┬───────┘
       │ All requests via REST API
       ▼
┌──────────────────────────────────────────────────┐
│              Django Orchestrator                  │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ REST API     │  │ Integration Modules       │  │
│  │ (DRF Views)  │  │                          │  │
│  │              │  │ ├─ integrations.openclinica│ │
│  │              │  │ ├─ integrations.senaite   │  │
│  │              │  │ ├─ integrations.erpnext   │  │
│  │              │  │ ├─ integrations.nextcloud │  │
│  │              │  │ └─ integrations.keycloak  │  │
│  └──────────────┘  └──────────────────────────┘  │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Celery Tasks │  │ Custom Modules            │  │
│  │ (Async Ops)  │  │ ├─ safety (CIOMS, alerts)│  │
│  │              │  │ ├─ regulatory (eTMF)     │  │
│  │              │  │ ├─ lab (import, validate)│  │
│  │              │  │ └─ reporting (dashboards)│  │
│  └──────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
  OpenClinica  ERPNext  Nextcloud   SENAITE
```

### Synchronization Strategy

| Flow Type | Use Case | Implementation |
|-----------|----------|----------------|
| **Synchronous** | Subject registration, lab result upload | Django → OpenClinica API (real-time) |
| **Asynchronous** | Site status sync, document metadata sync | Celery tasks running on schedule (hourly) |
| **Event-Driven** | SAE deadline alerts, approval notifications | Django signals + Celery beat scheduler |

### Integration Metadata

The custom Django database stores mapping IDs between systems:

| System | Stored Mapping | Example |
|--------|---------------|---------|
| OpenClinica | `openclinica_study_oid`, `openclinica_crf_oid`, `openclinica_ae_id` | `S_HACT001` |
| Keycloak | `keycloak_id` (UUID) | `a1b2c3-d4e5-f6g7-...` |
| ERPNext | `erpnext_site_id` | `SITE-00001` |
| SENAITE | `senaite_sample_id` | `SAMP-2026-0001` |
| Nextcloud | `file_url` in various tables | `/regulatory/IRB_approval_v2.pdf` |

---

## 14. Infrastructure & Deployment

### Docker Compose Architecture

All services run as Docker containers orchestrated by Docker Compose:

```yaml
# Conceptual service layout
services:
  nginx:              # Reverse proxy, SSL termination
  react-frontend:     # Custom React SPA (static files via nginx)
  django-api:         # Custom Django backend + Celery worker
  celery-worker:      # Async task processing
  celery-beat:        # Scheduled task triggers
  redis:              # Cache + message broker
  openclinica:        # OpenClinica CE (Tomcat/Java)
  keycloak:           # Keycloak IAM server
  erpnext:            # ERPNext (Frappe framework)
  nextcloud:          # Document management
  senaite:            # LIMS (Plone-based)
  postgres-custom:    # PostgreSQL for custom HACT DB
  postgres-oc:        # PostgreSQL for OpenClinica
  postgres-keycloak:  # PostgreSQL for Keycloak
  # (ERPNext uses MariaDB; SENAITE may use ZoDB/Postgres)
```

### Server Resource Requirements

| Resource | Minimum (Dev/Staging) | Recommended (Production) | Notes |
|----------|----------------------|--------------------------|-------|
| vCPUs | 8 cores | 12+ cores | Java apps (OpenClinica, Keycloak) need multiple cores |
| RAM | 16 GB | 48–64 GB | Allocate heap space for Java + DB caches |
| Storage (SSD) | 100 GB | 200–400 GB | Separate partition for `/var/lib/docker` |
| Network | 100 Mbps | 1 Gbps | TLS for all inter-service communication |

### Backup Strategy

| Component | Backup Method | Frequency | Retention |
|-----------|--------------|-----------|-----------|
| PostgreSQL databases | `pg_dump` via cron container | Nightly | 30 days daily + 52 weeks weekly |
| MariaDB (ERPNext) | `mysqldump` | Nightly | 30 days daily |
| Nextcloud files | Docker volume rsync | Nightly | 30 days + monthly archive |
| Docker volumes (config) | Volume snapshot | Weekly | 12 weeks |
| Off-site copy | Encrypted S3 bucket | Daily | Per retention policy |
| Restore drill | Full restore test in staging | Monthly | — |

---

## 15. Security & Compliance

### Security Architecture

```
┌─────────────────────────────────────────────┐
│              Security Layers                │
├─────────────────────────────────────────────┤
│ Layer 1: Network                            │
│   • TLS 1.3 everywhere (nginx terminates)   │
│   • Docker network isolation                │
│   • Firewall: only 443/80 exposed           │
├─────────────────────────────────────────────┤
│ Layer 2: Identity & Access                  │
│   • Keycloak SSO with OAuth2/OIDC           │
│   • Two-Factor Authentication (2FA/MFA)     │
│   • Role-Based Access Control (RBAC)        │
│   • Session management & timeout            │
├─────────────────────────────────────────────┤
│ Layer 3: Data Protection                    │
│   • AES-256 encryption at rest              │
│   • Field-level encryption for PII/PHI      │
│   • PostgreSQL row-level security            │
├─────────────────────────────────────────────┤
│ Layer 4: Audit & Compliance                 │
│   • Immutable audit trail (append-only)     │
│   • Electronic signatures (21 CFR Part 11)  │
│   • Complete data provenance                │
├─────────────────────────────────────────────┤
│ Layer 5: Operational Security               │
│   • Automated vulnerability scanning        │
│   • Container image hardening               │
│   • Secret management (Docker secrets)      │
│   • Log aggregation & monitoring            │
└─────────────────────────────────────────────┘
```

### Regulatory Compliance Checklist

| Standard | Key Requirements | How Addressed |
|----------|-----------------|---------------|
| **ICH-GCP E6(R2)** | Data integrity, audit trail, informed consent | OpenClinica audit trail; consent tracking module |
| **21 CFR Part 11** | Electronic signatures, audit trail, access controls | Keycloak auth; e-signature workflow; immutable logs |
| **CDISC SDTM** | Standardized data format for regulatory submission | OpenClinica CDISC export; custom SDTM mapping |
| **GDPR / Local DPA** | Data minimization, right to access, encryption | Field-level encryption; access logs; data export tools |
| **ICH E2B(R3)** | Standardized safety reporting format | Custom E2B XML generator for SAEs |

---

## 16. Development Phases & Roadmap

### Phase Overview

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 4
Environment &    Core Platform    Clinical         Safety, Lab &    Polish &
Infrastructure   (Foundation)     Workflows        Regulatory       Launch
                                                                    
Week 1-2         Week 3-5         Week 6-8         Week 9-11        Week 12-14
─────────────────────────────────────────────────────────────────────────────▶

Docker Setup     Django + React   OpenClinica      Safety Module    E2E Testing
PostgreSQL       Auth/RBAC via    eCRF + Visits    Lab Integration  UAT
Keycloak Deploy  Keycloak         Subject Mgmt     Regulatory/eTMF  Bug Fixes
OpenClinica      Study/Site Mgmt  Query Workflow   CIOMS Generation Documentation
ERPNext Deploy   Enrollment       Data Review      Reporting        Deployment
Nextcloud Setup  Dashboards       DB Lock/Export   Audit Viewer     Training
SENAITE Deploy   Basic Frontend   Coding Module    Export/SDTM
```

### Phase 0: Environment & Infrastructure (Weeks 1–2)

| Task | Deliverable | Owner |
|------|-------------|-------|
| Provision server (cloud VM or on-premise) | Running Linux server | DevOps |
| Docker Compose setup for all services | Working `docker-compose.yml` | DevOps |
| Deploy PostgreSQL cluster | Running databases for all services | DevOps |
| Deploy Keycloak + configure realms/clients | SSO working, OIDC configured | DevOps |
| Deploy OpenClinica CE | Running instance accessible via browser | DevOps |
| Deploy ERPNext | Running instance for site/ops management | DevOps |
| Deploy Nextcloud | Running instance for document management | DevOps |
| Deploy SENAITE | Running instance for lab management | DevOps |
| Configure Nginx reverse proxy + TLS | All services behind single domain with SSL | DevOps |
| Implement backup strategy | Nightly automated backups running | DevOps |

### Phase 1: Core Platform — Foundation (Weeks 3–5)

| Task | Deliverable | Owner |
|------|-------------|-------|
| Initialize Django project with app structure | Project scaffolded with `auth`, `clinical`, `ops`, `safety`, `lab`, `outputs`, `audit` apps | Backend |
| Initialize React project with Vite | SPA shell with routing, state management | Frontend |
| Implement Keycloak integration (Django + React) | SSO login/logout, token management | Full-stack |
| Build Django models for all 7 schemas | Migration scripts executed, tables created | Backend |
| Build Study Management CRUD APIs + UI | Create/edit/view studies with protocol metadata | Full-stack |
| Build Site Management CRUD APIs + UI | Register sites, manage contacts, track status | Full-stack |
| Implement RBAC middleware | Role-based API permissions enforced | Backend |
| Build enrollment dashboard | Real-time enrollment charts and tables | Frontend |
| Sync Keycloak roles → OpenClinica users | Auto-provision users in OpenClinica | Backend |

### Phase 2: Clinical Workflows (Weeks 6–8)

| Task | Deliverable | Owner |
|------|-------------|-------|
| Configure OpenClinica studies via API | Study/CRF structure synced from Django metadata | Backend |
| Build Subject Registration flow | Register subjects through React → Django → OpenClinica | Full-stack |
| Implement Visit Tracking views | Subject visit timeline with completion status | Full-stack |
| Configure eCRFs in OpenClinica | First set of CRFs built and mapped to visits | Data Mgmt |
| Build Data Entry screens (OpenClinica embedded or proxied) | Site coordinators can enter data | Full-stack |
| Implement Query Management views | View/respond to queries from custom dashboard | Full-stack |
| Build Data Review dashboard | Missing data, query counts, form completion | Frontend |
| Implement Database Lock workflow | Pre-lock checklist → lock → snapshot | Full-stack |
| Build CDISC SDTM export pipeline | Locked data exportable in SDTM format | Backend |

### Phase 3: Safety, Lab & Regulatory (Weeks 9–11)

| Task | Deliverable | Owner |
|------|-------------|-------|
| Build AE/SAE capture enhanced views | Structured SAE entry with seriousness criteria | Full-stack |
| Implement CIOMS I form generator | Auto-generate CIOMS PDF from SAE data | Backend |
| Build Safety Dashboard | AE frequency, SAE timeline, deadline tracker | Frontend |
| Implement Lab Data Import engine | CSV import → validation → push to OpenClinica | Backend |
| Build SENAITE integration | Sample tracking synced with subject visits | Backend |
| Build Lab Dashboard | Completeness, turnaround, flagged results | Frontend |
| Build Regulatory Document module (Nextcloud integration) | Upload/version/track regulatory docs | Full-stack |
| Implement deadline alerting system | Email/in-app alerts for approaching deadlines | Backend |
| Build Unified Audit Log viewer | Aggregate logs from all systems | Full-stack |
| Build Reporting module | Configurable reports with export | Full-stack |

### Phase 4: Polish & Launch (Weeks 12–14)

| Task | Deliverable | Owner |
|------|-------------|-------|
| End-to-end testing (full trial simulation) | QA report with zero critical bugs | QA |
| Performance testing & optimization | Response times within NFR targets | DevOps |
| Security audit & penetration testing | Security report with remediations | Security |
| User Acceptance Testing (UAT) with HACT team | UAT feedback log, all issues resolved | All |
| System validation documentation | IQ/OQ/PQ protocols and evidence | QA |
| User manuals & training materials | Site Coordinator Guide, Data Manager Guide, Admin Guide | Docs |
| API documentation (Swagger/OpenAPI) | Interactive API docs published | Backend |
| Architecture documentation | System diagrams, deployment guide, runbooks | DevOps |
| Production deployment & go-live | Live system accessible to authorized users | DevOps |
| Post-go-live monitoring plan | Monitoring dashboards, alert rules, escalation paths | DevOps |

---

## 17. Risk Assessment

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|-----------|------------|
| R1 | OpenClinica CE API limitations | High | Medium | Prototype key integrations in Phase 0; prepare fallback to direct DB access if needed |
| R2 | System validation complexity (21 CFR Part 11) | High | High | Start validation documentation from Day 1; engage regulatory consultant early |
| R3 | Server resource contention (many containers) | Medium | Medium | Monitor with Docker stats; right-size containers; scale vertically if needed |
| R4 | Data migration from existing sources (Excel/paper) | Medium | High | Build data import tools; validate migration with checksums |
| R5 | User adoption resistance | Medium | Medium | Involve end-users in UAT; provide comprehensive training; iterative UI improvement |
| R6 | Internet connectivity at some sites | High | Medium | Future phase: offline-capable progressive web app; current: require stable connection |
| R7 | Open-source component deprecation | Medium | Low | Pin versions; monitor project health; maintain fork readiness |
| R8 | Security breach / data leak | Critical | Low | Defense-in-depth security; regular pen-testing; incident response plan |
| R9 | Integration complexity across 6+ systems | High | High | Django orchestrator pattern centralizes complexity; comprehensive integration tests |
| R10 | Regulatory authority inspection findings | High | Medium | Mock audits quarterly; maintain inspection-ready eTMF |

---

## 18. Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **System Uptime** | ≥ 99.5% | Docker health checks + uptime monitoring |
| **Data Entry Speed** | < 10 min per CRF | Time tracking in eCRF submission logs |
| **Query Resolution Time** | < 5 business days average | Query lifecycle timestamps |
| **Safety Report Compliance** | 100% of SAEs reported within regulatory timelines | CIOMS submission tracking |
| **Audit Trail Coverage** | 100% of data changes logged | Audit log analysis |
| **User Satisfaction** | ≥ 4.0 / 5.0 | Post-training and quarterly surveys |
| **Data Export Accuracy** | 100% match between DB and export files | Automated export validation scripts |
| **Backup Recovery** | Successful restore within 4 hours | Monthly restoration drills |
| **Page Load Time** | < 2 seconds (P95) | Frontend performance monitoring |
| **Test Coverage** | ≥ 80% for custom code | pytest/jest coverage reports |

### Go/No-Go Criteria for Production Launch

- [ ] All P0 functional requirements implemented and tested
- [ ] Zero critical or high-severity bugs outstanding
- [ ] UAT completed with sign-off from Study Lead, Data Manager, and Safety Officer
- [ ] Backup and restore procedure tested successfully
- [ ] Security audit completed with no critical findings
- [ ] System validation documentation approved
- [ ] User training completed for all initial roles
- [ ] Monitoring and alerting operational

---

## 19. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **AE** | Adverse Event — any untoward medical occurrence in a trial subject |
| **CDISC** | Clinical Data Interchange Standards Consortium |
| **CIOMS** | Council for International Organizations of Medical Sciences — standardized safety reporting form |
| **CRA** | Clinical Research Associate — monitors trial sites |
| **CRF** | Case Report Form — data collection instrument |
| **CTMS** | Clinical Trial Management System |
| **DPA** | Data Protection Authority |
| **DSUR** | Development Safety Update Report |
| **eCRF** | Electronic Case Report Form |
| **EDC** | Electronic Data Capture |
| **eTMF** | Electronic Trial Master File |
| **ICH-GCP** | International Council for Harmonisation — Good Clinical Practice |
| **IRB/EC** | Institutional Review Board / Ethics Committee |
| **LIMS** | Laboratory Information Management System |
| **MedDRA** | Medical Dictionary for Regulatory Activities |
| **OIDC** | OpenID Connect |
| **PI** | Principal Investigator |
| **RBAC** | Role-Based Access Control |
| **SAE** | Serious Adverse Event |
| **SDTM** | Study Data Tabulation Model |
| **SSO** | Single Sign-On |
| **UAT** | User Acceptance Testing |
| **USUBJID** | Unique Subject Identifier (CDISC standard) |

### Appendix B: Reference Documents

| Document | Location | Description |
|----------|----------|-------------|
| HACT Clinical Workflow & Requirements Summary | `HACT CTMS/` | Comprehensive workflow and requirements analysis by Turemo Bedaso |
| Clinical Trial Management System — Roadmap and Task List | `HACT CTMS/` | 4-week implementation plan |
| HACT DBMS Simple Picture (v3) | `HACT CTMS/hact_dbms_simple_v3.html` | Simple schema architecture overview |
| HACT Wellcome Trust Document | `HACT CTMS/HACT_Welcome_Trust.pdf` | Organizational background |
| OpenClinica Documentation | [docs.openclinica.com](https://docs.openclinica.com) | Official OpenClinica CE documentation |
| CDISC Standards | [cdisc.org/standards](https://www.cdisc.org/standards) | CDISC data standard specifications |

### Appendix C: Open-Source License Summary

| Component | License | Commercial Use | Modifications | Distribution | Patent Grant |
|-----------|---------|---------------|---------------|-------------|-------------|
| OpenClinica CE | LGPL 3.0 | ✅ | ✅ (share changes) | ✅ | ✅ |
| Django | BSD 3-Clause | ✅ | ✅ | ✅ | — |
| React | MIT | ✅ | ✅ | ✅ | — |
| Keycloak | Apache 2.0 | ✅ | ✅ | ✅ | ✅ |
| ERPNext | GPL 3.0 | ✅ | ✅ (share changes) | ✅ | ✅ |
| Nextcloud | AGPL 3.0 | ✅ | ✅ (share changes) | ✅ | — |
| SENAITE | GPL 2.0 | ✅ | ✅ (share changes) | ✅ | — |
| PostgreSQL | PostgreSQL License | ✅ | ✅ | ✅ | — |

> **Note:** GPL/AGPL licenses require that modifications to these components be shared under the same license. Custom code that merely *integrates* with these tools via APIs does not need to be GPL-licensed.

---

**Document prepared by:** HACT CTMS Development Team
**Next Steps:** Review and approve this PRD → Proceed to Phase 0 (Infrastructure Setup)
