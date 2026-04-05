/**
 * usePermission — React hook for checking role-based permissions.
 *
 * Usage:
 *   const { can } = usePermission()
 *   {can('CREATE_STUDY') && <button>New Study</button>}
 */

import useAuthStore from '../store/authStore'
import { canPerformAction } from '../auth/roleConfig'

export default function usePermission() {
  const { roles, user } = useAuthStore()
  const isSuperuser = user?.is_superuser || false

  const can = (actionKey) => canPerformAction(roles, isSuperuser, actionKey)

  return { can, roles, isSuperuser }
}
