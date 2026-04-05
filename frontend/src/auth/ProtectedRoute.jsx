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

  // Not authenticated → redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Still loading user data → show nothing (or a loading state)
  if (!user) {
    return null
  }

  // Check route-level permission
  // Match the current path against ROUTE_ACCESS keys
  const currentPath = location.pathname
  const isSuperuser = user?.is_superuser || false

  // Find matching route (handle parameterized routes like /studies/:id)
  let matchedRoute = currentPath
  if (currentPath.startsWith('/studies/') && currentPath !== '/studies') {
    matchedRoute = '/studies/:id'
  }

  // Check if user has access to this route
  if (!canAccessRoute(roles, isSuperuser, matchedRoute)) {
    // Find needed roles for error message
    const neededRoles = ROUTE_ACCESS[matchedRoute]
    const roleLabel = neededRoles
      ? neededRoles.filter(r => r !== 'admin').join(', ').replace(/_/g, ' ')
      : 'unknown'
    return <AccessDenied requiredRole={roleLabel} />
  }

  return <Outlet />
}
