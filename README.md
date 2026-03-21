# HACT Clinical Trial Management System (CTMS)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source Clinical Trial Management System built for the **Horn of Africa Clinical Trials (HACT)** organization.

## Overview

The HACT CTMS is a composable, open-source platform designed to manage the full lifecycle of clinical research — from protocol design through data collection, safety monitoring, regulatory compliance, and final dataset export for statistical analysis.

## Architecture

The system uses a **composable open-source stack**:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| EDC / Clinical Data | OpenClinica CE | eCRF design, data entry, queries, audit trail |
| Custom Backend | Django + DRF | API gateway, orchestration, safety/regulatory/lab modules |
| Custom Frontend | React + Vite | Unified SPA for dashboards and administration |
| Identity & Access | Keycloak | SSO, OAuth2/OIDC, 2FA |
| Operations | ERPNext | Site management, contracts, milestones |
| Documents (eTMF) | Nextcloud | Regulatory document management |
| Lab Information | SENAITE | Sample tracking, lab workflows |
| Database | PostgreSQL | Primary data store |
| Infrastructure | Docker Compose | Containerized deployment |

## Repository Structure

```
hact-ctms-dev/
├── docs/
│   └── PRODUCT_REQUIREMENTS_DOCUMENT.md   # Full PRD (start here)
├── backend/                                # Django API (coming soon)
├── frontend/                               # React SPA (coming soon)
├── infrastructure/                         # Docker Compose, Nginx configs (coming soon)
├── database/                               # SQL migrations and schema (coming soon)
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)
- PostgreSQL 16+ (for local development)

### Documentation

Start with the [Product Requirements Document](docs/PRODUCT_REQUIREMENTS_DOCUMENT.md) for the complete system specification.

## Key Features

- **12-Step Clinical Trial Lifecycle** support (protocol to archive)
- **Electronic Data Capture** via OpenClinica eCRFs
- **Safety Reporting** with CIOMS form generation
- **Regulatory (eTMF)** document management with version control
- **Lab Integration** with sample tracking and result import
- **RBAC** with Keycloak SSO across all systems
- **Audit Trail** meeting ICH-GCP and 21 CFR Part 11 requirements
- **CDISC SDTM** compliant data export
- **Real-time Dashboards** for enrollment, safety, and data quality

## Development Phases

| Phase | Weeks | Focus |
|-------|-------|-------|
| Phase 0 | 1-2 | Infrastructure & Docker deployment |
| Phase 1 | 3-5 | Core platform (auth, study/site management) |
| Phase 2 | 6-8 | Clinical workflows (eCRF, visits, queries) |
| Phase 3 | 9-11 | Safety, lab, regulatory modules |
| Phase 4 | 12-14 | Testing, UAT, documentation, launch |

## Standards & Compliance

- ICH-GCP E6(R2)
- 21 CFR Part 11 (electronic signatures)
- CDISC SDTM/ADaM
- GDPR / Data Protection

## Contributing

This project is under active development by the HACT team. Contribution guidelines will be published as the project matures.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Contact

- **Organization:** Horn of Africa Clinical Trials (HACT)
- **Website:** [hacts.org](https://hacts.org)
