/**
 * Role-Based Access Configuration (RBAC)
 * ========================================
 * Central configuration mapping each role to:
 * - Allowed navigation items (sidebar)
 * - Allowed routes (pages)
 * - Allowed actions (buttons)
 *
 * Derived from backend permission_classes in core/permissions.py
 */

// ── All 9 HACT roles ──
export const ROLES = {
  ADMIN: 'admin',
  STUDY_ADMIN: 'study_admin',
  DATA_MANAGER: 'data_manager',
  SITE_COORDINATOR: 'site_coordinator',
  MONITOR: 'monitor',
  SAFETY_OFFICER: 'safety_officer',
  LAB_MANAGER: 'lab_manager',
  OPS_MANAGER: 'ops_manager',
  AUDITOR: 'auditor',
}

// ── Route access per role ──
// Maps each route path to the roles that can access it.
// "dashboard" and "studies" (read) are available to most authenticated users.
export const ROUTE_ACCESS = {
  '/': [
    // Dashboard — available to all authenticated users
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER,
    ROLES.SITE_COORDINATOR, ROLES.MONITOR, ROLES.SAFETY_OFFICER,
    ROLES.LAB_MANAGER, ROLES.OPS_MANAGER, ROLES.AUDITOR,
  ],
  '/studies': [
    // Studies list (read) — IsReadOnlyOrStudyAdmin → any authenticated user can read
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER,
    ROLES.SITE_COORDINATOR, ROLES.MONITOR, ROLES.SAFETY_OFFICER,
    ROLES.LAB_MANAGER, ROLES.AUDITOR,
  ],
  '/studies/:id': [
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER,
    ROLES.SITE_COORDINATOR, ROLES.MONITOR, ROLES.SAFETY_OFFICER,
    ROLES.LAB_MANAGER, ROLES.AUDITOR,
  ],
  '/subjects': [
    // Subjects list (read) — IsReadOnlyOrDataManager → any authenticated user can read
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER,
    ROLES.SITE_COORDINATOR, ROLES.MONITOR,
  ],
  '/queries': [
    // Queries list (read) — IsReadOnlyOrDataManager → any authenticated user can read
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER,
    ROLES.SITE_COORDINATOR, ROLES.MONITOR,
  ],
  '/safety': [
    // Safety — IsSafetyOfficer → only safety_officer, study_admin, admin
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.SAFETY_OFFICER,
  ],
  '/lab': [
    // Lab — IsLabManager → only lab_manager, study_admin, admin
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.LAB_MANAGER,
  ],
  '/audit': [
    // Audit — IsAuditor → only auditor, study_admin, admin
    ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.AUDITOR,
  ],
}

// ── Sidebar navigation per role ──
// Which nav items appear for each role
export const SIDEBAR_ACCESS = {
  [ROLES.ADMIN]: ['/', '/studies', '/subjects', '/queries', '/safety', '/lab', '/audit'],
  [ROLES.STUDY_ADMIN]: ['/', '/studies', '/subjects', '/queries', '/safety', '/lab', '/audit'],
  [ROLES.DATA_MANAGER]: ['/', '/studies', '/subjects', '/queries'],
  [ROLES.SITE_COORDINATOR]: ['/', '/studies', '/subjects', '/queries'],
  [ROLES.MONITOR]: ['/', '/studies', '/subjects', '/queries'],
  [ROLES.SAFETY_OFFICER]: ['/', '/studies', '/safety'],
  [ROLES.LAB_MANAGER]: ['/', '/studies', '/lab'],
  [ROLES.OPS_MANAGER]: ['/'],
  [ROLES.AUDITOR]: ['/', '/studies', '/audit'],
}

// ── Action-level permissions ──
// Which roles can perform specific UI actions
export const ACTION_PERMISSIONS = {
  // Study actions
  CREATE_STUDY: [ROLES.ADMIN, ROLES.STUDY_ADMIN],
  EDIT_STUDY: [ROLES.ADMIN, ROLES.STUDY_ADMIN],
  TRANSITION_STUDY: [ROLES.ADMIN, ROLES.STUDY_ADMIN],
  CREATE_SITE: [ROLES.ADMIN, ROLES.STUDY_ADMIN],

  // Subject actions
  CREATE_SUBJECT: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER],
  ENROLL_SUBJECT: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER, ROLES.SITE_COORDINATOR],
  WITHDRAW_SUBJECT: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER, ROLES.SITE_COORDINATOR],

  // Query actions
  CREATE_QUERY: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER],
  ANSWER_QUERY: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER, ROLES.SITE_COORDINATOR],
  CLOSE_QUERY: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.DATA_MANAGER],

  // Safety actions
  CREATE_AE: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.SAFETY_OFFICER],

  // Lab actions
  IMPORT_LAB_CSV: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.LAB_MANAGER],

  // Audit actions
  EXPORT_AUDIT: [ROLES.ADMIN, ROLES.STUDY_ADMIN, ROLES.AUDITOR],
}

// ── Helper functions ──

/**
 * Check if a user with given roles can access a route.
 * Superusers always pass.
 */
export function canAccessRoute(userRoles, isSuperuser, routePath) {
  if (isSuperuser) return true
  // Match exact or parameterized route
  const allowedRoles = ROUTE_ACCESS[routePath]
  if (!allowedRoles) return true // Unknown route = allow (defensive)
  return userRoles.some(role => allowedRoles.includes(role))
}

/**
 * Check if a user can perform a specific action.
 */
export function canPerformAction(userRoles, isSuperuser, actionKey) {
  if (isSuperuser) return true
  const allowedRoles = ACTION_PERMISSIONS[actionKey]
  if (!allowedRoles) return false
  return userRoles.some(role => allowedRoles.includes(role))
}

/**
 * Get the sidebar routes a user should see based on their roles.
 * If user has multiple roles, union all accessible routes.
 */
export function getSidebarRoutes(userRoles, isSuperuser) {
  if (isSuperuser) {
    return ['/', '/studies', '/subjects', '/queries', '/safety', '/lab', '/audit']
  }

  const routes = new Set()
  for (const role of userRoles) {
    const roleRoutes = SIDEBAR_ACCESS[role] || ['/']
    roleRoutes.forEach(r => routes.add(r))
  }
  return Array.from(routes)
}

/**
 * Map route paths to their labels (for AccessDenied messages etc.)
 */
export const ROUTE_LABELS = {
  '/': 'Dashboard',
  '/studies': 'Studies',
  '/subjects': 'Subjects',
  '/queries': 'Queries',
  '/safety': 'Safety',
  '/lab': 'Laboratory',
  '/audit': 'Audit Trail',
}
