# Relational Database Schema Design – HACT CTMS

## 1. Overview

This document presents the final relational database schema design for the HACT CTMS custom PostgreSQL database. The database serves as the primary data repository for all clinical and operational data, as agreed with stakeholders. It replaces the earlier approach that relied on OpenClinica for clinical data storage; instead, the custom database now stores all core data while OpenClinica may be used as a complementary EDC tool for specific advanced features.

The design is organized into logical schemas (**auth**, **clinical**, **ops**, **safety**, **lab**, **outputs**, **audit**) to maintain separation of concerns and facilitate extensibility. All tables include audit columns (`created_at`, `created_by`, `updated_at`, `updated_by`) and integrate with external systems (Keycloak, Nextcloud, SENAITE, ERPNext) where needed.

## 2. Key Principles

- **Separation of Concerns** – Logical schemas group related tables (e.g., auth for identity, clinical for study and data collection, ops for site operations, safety for pharmacovigilance, lab for laboratory data, outputs for reporting, audit for logs).
- **Auditability** – Every table includes timestamp and user tracking. A central `audit_log` table captures all data changes.
- **Integration** – External system IDs are stored as reference columns to enable synchronization (e.g., Keycloak user IDs, Nextcloud file URLs).
- **Extensibility** – Schemas and tables are designed to accommodate future modules (e.g., finance, inventory) without major refactoring.

## 3. Database Schemas & Table Definitions

### Schema: auth – Identity & Access Management

| Table | Description | Columns |
|---|---|---|
| users | Local user records linked to Keycloak | id (PK), keycloak_id (uuid, unique), username, email, first_name, last_name, is_active, created_at, updated_at |
| roles | Role definitions (e.g., data_manager, site_coordinator) | id (PK), name (unique), description |
| user_roles | Many-to-many mapping | id (PK), user_id (FK→users.id), role_id (FK→roles.id) |
| site_staff | Links users to sites with a role | id (PK), site_id (FK→ops.sites.id), user_id (FK→users.id), role_at_site (varchar), start_date, end_date |
| external_system_identities | Maps local user to external system IDs | id (PK), user_id (FK→users.id), system_name (e.g., 'openclinica', 'nextcloud'), external_user_id, external_username, created_at |

### Schema: clinical – Study & Data Collection

| Table | Description | Columns |
|---|---|---|
| studies | Study metadata | id (PK), name, protocol_number (unique), phase, sponsor, start_date, end_date, status (planning, active, locked, archived), created_at, updated_at |
| sites | Participating sites | id (PK), study_id (FK→studies.id), site_code (unique within study), name, address, country, principal_investigator, status, activation_date |
| subjects | Enrolled subjects | id (PK), study_id (FK→studies.id), site_id (FK→sites.id), subject_identifier (unique within study), screening_number, enrollment_date, completion_date, status (screened, enrolled, completed, discontinued), consent_signed_date |
| visits | Visit definitions per study | id (PK), study_id (FK→studies.id), visit_name, visit_order, planned_day (days from baseline), is_screening, is_baseline, is_follow_up |
| subject_visits | Subject-specific visit schedule (actual dates) | id (PK), subject_id (FK→subjects.id), visit_id (FK→visits.id), scheduled_date, actual_date, status (planned, completed, missed) |
| forms | Case Report Form definitions | id (PK), study_id (FK→studies.id), name, version, description, is_active |
| items | Individual form fields | id (PK), form_id (FK→forms.id), field_name, field_label, field_type, required, validation_rule, options (jsonb), order |
| form_instances | Filled forms for a subject/visit | id (PK), form_id (FK→forms.id), subject_id (FK→subjects.id), subject_visit_id (FK→subject_visits.id, nullable), instance_number, status (draft, submitted, signed, locked), submitted_at, signed_by (FK→users.id), signed_at |
| item_responses | Values entered for each item | id (PK), form_instance_id (FK→form_instances.id), item_id (FK→items.id), value (text), updated_at, updated_by (FK→users.id) |
| queries | Data discrepancy queries | id (PK), item_response_id (FK→item_responses.id), raised_by (FK→users.id), raised_at, query_text, status (open, answered, closed), response_text, resolved_by (FK→users.id), resolved_at |

### Schema: safety – Pharmacovigilance

| Table | Description | Columns |
|---|---|---|
| adverse_events | Adverse event records | id (PK), subject_id (FK→subjects.id), study_id (FK→studies.id), ae_term, start_date, end_date, severity (mild, moderate, severe), serious (boolean), serious_criteria, causality, outcome, action_taken, reported_at, reported_by (FK→users.id) |
| cioms_forms | CIOMS form tracking for serious AEs | id (PK), ae_id (FK→adverse_events.id), form_version, generated_date, submission_deadline, submitted_date, regulatory_authority, status (draft, submitted, approved), file_url (link to Nextcloud) |
| safety_reviews | Safety committee reviews, DSUR etc. | id (PK), study_id (FK→studies.id), review_type (DSUR, DMC, quarterly), review_date, summary, file_url |

### Schema: lab – Laboratory & Biomarker Data

| Table | Description | Columns |
|---|---|---|
| lab_results | Laboratory test results | id (PK), subject_id (FK→subjects.id), subject_visit_id (FK→subject_visits.id, nullable), test_name, result_value, unit, reference_range_low, reference_range_high, flag (H, L, N), result_date, imported_at, imported_by (FK→users.id) |
| reference_ranges | Reference ranges per study/test/demographics | id (PK), study_id (FK→studies.id), test_name, gender (M, F, all), age_lower, age_upper, range_low, range_high |
| sample_collections | Sample tracking (optional, if using SENAITE) | id (PK), subject_id (FK→subjects.id), senaite_sample_id (varchar), collection_date, sample_type, status (collected, in progress, completed) |

### Schema: ops – Operational & Site Management

| Table | Description | Columns |
|---|---|---|
| contracts | Site contracts | id (PK), site_id (FK→sites.id), contract_number (unique), start_date, end_date, status, budget_amount, file_url |
| training_records | Site staff training records | id (PK), site_id (FK→sites.id), staff_name, training_type, training_date, certificate_url |
| milestones | Study milestones (study-level or site-level) | id (PK), study_id (FK→studies.id), site_id (FK→sites.id, nullable), milestone_type, planned_date, actual_date, status |

### Schema: outputs – Reporting & Data Exports

| Table | Description | Columns |
|---|---|---|
| dataset_snapshot | Exported dataset snapshots | id (PK), study_id (FK→studies.id), snapshot_date (timestamp), snapshot_type (SDTM, ADaM, raw), file_url, generated_by (FK→users.id), description, criteria (jsonb) |
| data_quality_reports | Data quality report logs | id (PK), study_id (FK→studies.id), report_type (missing data, out-of-range, query status), generated_at, report_data (jsonb), file_url |

### Schema: audit – Audit Trail

| Table | Description | Columns |
|---|---|---|
| audit_log | Captures all data changes (insert, update, delete) for all tables | id (bigserial PK), user_id (FK→users.id), action (create, update, delete, login, export, lock), table_name, record_id, old_value (jsonb), new_value (jsonb), ip_address (inet), user_agent, timestamp (timestamptz) |

## 4. Integration Points with External Systems

| External System | Data Stored in Custom DB | Purpose |
|---|---|---|
| **Keycloak** | `users.keycloak_id`, `external_system_identities` | Map local users to Keycloak identities; synchronize roles via `user_roles`. |
| **OpenClinica** | `studies.openclinica_study_oid`, `visits.openclinica_event_definition_oid`, `forms.openclinica_crf_oid` (optional) | Link to OpenClinica entities if used as secondary system. |
| **Nextcloud** | `file_url` columns in `contracts`, `training_records`, `cioms_forms`, `dataset_snapshot`, etc. | Store actual documents in Nextcloud, reference via URL. |
| **SENAITE** | `sample_collections.senaite_sample_id` | Track samples managed in SENAITE. |
| **ERPNext** | `sites.erpnext_site_id`, `contracts.erpnext_contract_id` (optional) | Sync site and contract data if ERPNext is used. |

## 6. Indexing & Performance Recommendations

- Foreign keys (e.g., `subject_id`, `study_id`, `site_id`) in all tables.
- Frequently searched columns: `subject_identifier`, `study_id`, `status` in `studies`, `subjects`.
- `audit_log.timestamp` for efficient audit trail queries.
- Use PostgreSQL’s JSONB indexes for `audit_log.old_value` and `new_value` if needed.

## 7. Key Relationships Explanation

### Authentication & User Management (auth)
- **Users ↔ Roles (Many-to-Many via user_roles):** A user can have many roles; a role can be assigned to many users.
- **Users ↔ Site Staff (One-to-Many):** A user can be associated with multiple sites; a site can have many staff users.
- **Users ↔ External System Identities (One-to-Many):** A user may have multiple external identities (e.g., OpenClinica, Nextcloud).

### Study & Site Structure (clinical, ops)
- **Studies ↔ Sites (One-to-Many):** A study includes multiple sites.
- **Sites ↔ Subjects (One-to-Many):** A site hosts many subjects.
- **Studies ↔ Subjects (One-to-Many):** A study enrolls many subjects.
- **Studies ↔ Visits (One-to-Many):** A study defines many visit templates.
- **Subjects ↔ Subject Visits (One-to-Many):** A subject has many scheduled visits.
- **Visits ↔ Subject Visits (One-to-Many):** A visit definition can be applied to many subjects.

### Forms & Data Collection (clinical)
- **Studies ↔ Forms (One-to-Many):** A study can have many forms (CRFs).
- **Forms ↔ Items (One-to-Many):** A form contains many items (fields).
- **Subjects ↔ Form Instances (One-to-Many):** A subject can have many completed forms.
- **Subject Visits ↔ Form Instances (One-to-Many):** A form instance may be linked to a specific visit.
- **Forms ↔ Form Instances (One-to-Many):** A form definition can be instantiated many times.
- **Form Instances ↔ Item Responses (One-to-Many):** A form instance contains many item responses.
- **Items ↔ Item Responses (One-to-Many):** An item definition can have many responses across different form instances.

### Queries & Data Cleaning (clinical)
- **Item Responses ↔ Queries (One-to-Many):** A single response can have multiple queries.
- **Users ↔ Queries (One-to-Many):** A user can raise many queries and also resolve many queries.

### Safety & Pharmacovigilance (safety)
- **Subjects ↔ Adverse Events (One-to-Many):** A subject may experience many adverse events.
- **Studies ↔ Adverse Events (One-to-Many):** A study can have many adverse events across its subjects.
- **Adverse Events ↔ CIOMS Forms (One-to-Many):** A serious adverse event may generate one or more CIOMS forms.

### Laboratory Data (lab)
- **Subjects ↔ Lab Results (One-to-Many):** A subject can have many lab results.
- **Subject Visits ↔ Lab Results (One-to-Many, optional):** A lab result may be linked to a specific visit.
- **Studies ↔ Reference Ranges (One-to-Many):** A study may define many reference ranges for various tests/demographics.

### Operational Data (ops)
- **Sites ↔ Contracts (One-to-Many):** A site can have multiple contracts.
- **Sites ↔ Training Records (One-to-Many):** A site can have many training records for its staff.
- **Studies ↔ Milestones (One-to-Many):** A study can have many milestones (study-level or site-level).
- **Sites ↔ Milestones (One-to-Many):** A site can have many site-specific milestones.

### Reporting & Exports (outputs)
- **Studies ↔ Dataset Snapshots (One-to-Many):** A study may have many exported dataset snapshots.
- **Users ↔ Dataset Snapshots (One-to-Many):** A user can generate many snapshots.

### Audit Trail (audit)
- **Users ↔ Audit Log (One-to-Many):** A user can perform many actions recorded in the audit log.

## 8. Implementation Notes

- **Triggers:** Use database triggers or Django signals to automatically populate `audit_log` on changes.
- **Soft Deletes:** Consider adding a `deleted_at` column for soft deletion instead of permanent deletion.
- **Backup:** All tables reside in one PostgreSQL database, simplifying backup compared to a distributed model.
- **Validation:** For regulatory compliance, ensure that electronic signatures and audit logs meet 21 CFR Part 11 requirements.

## 9. Conclusion

This schema design meets all stakeholder requirements, including the core tables: `users`, `roles`, `user_roles`, `studies`, `sites`, `subjects`, `forms`, `items`, `form_instances`, `item_responses`, `queries`, `adverse_events`, `lab_results`, `dataset_snapshot`, and `audit_log`. It also includes necessary supporting tables (`visits`, `subject_visits`, `site_staff`, `contracts`, `training_records`, `milestones`, `cioms_forms`, `reference_ranges`, `sample_collections`) to provide a complete CTMS solution. The design is scalable, auditable, and ready for implementation in Week 2.