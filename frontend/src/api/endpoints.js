/**
 * API Endpoint Constants
 * Organized by backend Django app module.
 */

export const API = {
  // ── Auth ──
  AUTH: {
    ME: 'accounts/auth/me/',
    STATUS: 'accounts/auth/status/',
  },

  // ── Clinical ──
  STUDIES: 'clinical/studies/',
  SITES: 'clinical/sites/',
  SUBJECTS: 'clinical/subjects/',
  VISITS: 'clinical/visits/',
  SUBJECT_VISITS: 'clinical/subject-visits/',
  FORMS: 'clinical/forms/',
  ITEMS: 'clinical/items/',
  FORM_INSTANCES: 'clinical/form-instances/',
  ITEM_RESPONSES: 'clinical/item-responses/',
  QUERIES: 'clinical/queries/',

  // ── Safety ──
  ADVERSE_EVENTS: 'safety/adverse-events/',
  CIOMS_FORMS: 'safety/cioms-forms/',
  SAFETY_REVIEWS: 'safety/safety-reviews/',

  // ── Lab ──
  LAB_RESULTS: 'lab/results/',
  REFERENCE_RANGES: 'lab/reference-ranges/',
  SAMPLES: 'lab/samples/',

  // ── Outputs ──
  SNAPSHOTS: 'outputs/snapshots/',
  QUALITY_REPORTS: 'outputs/quality-reports/',

  // ── Audit ──
  AUDIT_LOGS: 'audit/logs/',

  // ── Ops ──
  CONTRACTS: 'ops/contracts/',
  TRAINING_RECORDS: 'ops/training-records/',
  MILESTONES: 'ops/milestones/',
}

// Keycloak token endpoint (goes through NGINX proxy → Keycloak:8080)
export const KEYCLOAK_TOKEN_URL = '/auth/realms/hact/protocol/openid-connect/token'

// Public client for React SPA — NO client_secret required.
// Django keeps its own confidential 'hact-ctms' client for server-side operations.
// Both clients share the same Keycloak realm signing keys, so tokens are valid for both.
export const KEYCLOAK_CLIENT_ID = 'hact-ctms-frontend'
