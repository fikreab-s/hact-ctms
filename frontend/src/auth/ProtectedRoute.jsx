import { useEffect } from 'react'
import { Outlet, Navigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

export default function ProtectedRoute() {
  const { isAuthenticated, user, fetchUser } = useAuthStore()

  useEffect(() => {
    // If we have a token but no user data, fetch the profile
    if (isAuthenticated && !user) {
      fetchUser()
    }
  }, [isAuthenticated, user, fetchUser])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
