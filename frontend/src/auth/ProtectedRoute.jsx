/**
 * ProtectedRoute — guards all authenticated routes.
 *
 * - Redirects to /login if not authenticated (saves return URL)
 * - Fetches user profile on page reload
 * - Checks route-level RBAC permissions
 */

import { useEffect } from 'react'
import { Outlet, Navigate, useLocation } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { canAccessRoute, ROUTE_ACCESS } from './roleConfig'
import AccessDenied from '../components/AccessDenied'

export default function ProtectedRoute() {
  const { isAuthenticated, user, roles, fetchUser } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    // If we have a token but no user data, fetch the profile
    if (isAuthenticated && !user) {
      fetchUser()
    }
  }, [isAuthenticated, user, fetchUser])

  // Not authenticated → save return URL and redirect to login
  if (!isAuthenticated) {
    sessionStorage.setItem('hact_return_to', location.pathname)
    return <Navigate to="/login" replace />
  }

  // Still loading user data → show nothing (or a loading state)
  if (!user) {
    return null
  }

  // Check route-level permission
  const currentPath = location.pathname
  const isSuperuser = user?.is_superuser || false

  // Find matching route (handle parameterized routes)
  let matchedRoute = currentPath
  if (currentPath.startsWith('/studies/') && currentPath !== '/studies') {
    matchedRoute = '/studies/:id'
  } else if (currentPath.startsWith('/subjects/') && currentPath !== '/subjects') {
    matchedRoute = '/subjects/:id'
  }

  // Check if user has access to this route
  if (!canAccessRoute(roles, isSuperuser, matchedRoute)) {
    const neededRoles = ROUTE_ACCESS[matchedRoute]
    const roleLabel = neededRoles
      ? neededRoles.filter(r => r !== 'admin').join(', ').replace(/_/g, ' ')
      : 'unknown'
    return <AccessDenied requiredRole={roleLabel} />
  }

  return <Outlet />
}
