/**
 * Auth Store — Zustand (OIDC Authorization Code + PKCE)
 * ======================================================
 * Manages: access token, refresh token, ID token, user profile, roles.
 *
 * Auth Flow:
 *   1. User clicks "Sign in" → redirected to Keycloak login page
 *   2. Keycloak authenticates (username/password + optional 2FA/OTP)
 *   3. Keycloak redirects back to /auth/callback with authorization code
 *   4. CallbackPage calls handleOidcCallback → exchanges code for tokens
 *   5. Token refresh runs automatically before expiry
 *   6. Session timeout after 30 min of inactivity
 *
 * Security:
 *   - No client_secret in the browser (public client)
 *   - PKCE prevents authorization code interception
 *   - State parameter prevents CSRF
 *   - 2FA is enforced by Keycloak (if configured in realm)
 */

import { create } from 'zustand'
import apiClient from '../api/client'
import { API } from '../api/endpoints'
import {
  exchangeCodeForTokens,
  refreshAccessToken,
  buildLogoutUrl,
  getTokenExpiresIn,
} from '../auth/oidc'

// Session timeout: 30 minutes of inactivity
const SESSION_TIMEOUT_MS = 30 * 60 * 1000

// Refresh token 60 seconds before expiry
const REFRESH_BUFFER_MS = 60 * 1000

const useAuthStore = create((set, get) => {
  // ── Internal timer refs ──
  let refreshTimer = null
  let sessionTimer = null
  let activityListenersAttached = false

  // ── Reset activity timer on user interaction ──
  const resetSessionTimer = () => {
    if (sessionTimer) clearTimeout(sessionTimer)
    if (!get().isAuthenticated) return

    sessionTimer = setTimeout(() => {
      console.warn('[Auth] Session timed out due to inactivity')
      get().logout()
    }, SESSION_TIMEOUT_MS)
  }

  // ── Attach activity listeners (once) ──
  const attachActivityListeners = () => {
    if (activityListenersAttached) return
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart']
    events.forEach(evt => window.addEventListener(evt, resetSessionTimer, { passive: true }))
    activityListenersAttached = true
  }

  // ── Detach activity listeners ──
  const detachActivityListeners = () => {
    if (!activityListenersAttached) return
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart']
    events.forEach(evt => window.removeEventListener(evt, resetSessionTimer))
    activityListenersAttached = false
  }

  // ── Schedule silent token refresh ──
  const scheduleTokenRefresh = (accessToken) => {
    if (refreshTimer) clearTimeout(refreshTimer)

    const expiresIn = getTokenExpiresIn(accessToken)
    const refreshIn = Math.max(expiresIn - REFRESH_BUFFER_MS, 5000)

    console.info(`[Auth] Token refresh scheduled in ${Math.round(refreshIn / 1000)}s`)

    refreshTimer = setTimeout(async () => {
      const rt = localStorage.getItem('hact_refresh_token')
      if (!rt) {
        get().logout()
        return
      }

      try {
        const tokens = await refreshAccessToken(rt)
        localStorage.setItem('hact_access_token', tokens.access_token)
        if (tokens.refresh_token) {
          localStorage.setItem('hact_refresh_token', tokens.refresh_token)
        }
        if (tokens.id_token) {
          localStorage.setItem('hact_id_token', tokens.id_token)
        }

        set({
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token || rt,
          idToken: tokens.id_token || get().idToken,
        })

        // Schedule next refresh
        scheduleTokenRefresh(tokens.access_token)
        console.info('[Auth] Token refreshed successfully')
      } catch (err) {
        console.warn('[Auth] Token refresh failed, logging out:', err.message)
        get().logout()
      }
    }, refreshIn)
  }

  return {
    // ── State ──
    accessToken: localStorage.getItem('hact_access_token') || null,
    refreshToken: localStorage.getItem('hact_refresh_token') || null,
    idToken: localStorage.getItem('hact_id_token') || null,
    user: null,
    roles: [],
    isAuthenticated: !!localStorage.getItem('hact_access_token'),
    isLoading: false,
    error: null,

    // ── OIDC Callback Handler ──
    // Called by CallbackPage after Keycloak redirects back
    handleOidcCallback: async (code, redirectUri) => {
      set({ isLoading: true, error: null })
      try {
        // 1. Exchange authorization code for tokens
        const tokens = await exchangeCodeForTokens(code, redirectUri)

        const { access_token, refresh_token, id_token } = tokens
        localStorage.setItem('hact_access_token', access_token)
        localStorage.setItem('hact_refresh_token', refresh_token)
        if (id_token) localStorage.setItem('hact_id_token', id_token)

        // 2. Fetch user profile from Django
        const meRes = await apiClient.get(API.AUTH.ME, {
          headers: { Authorization: `Bearer ${access_token}` },
        })
        const user = meRes.data

        set({
          accessToken: access_token,
          refreshToken: refresh_token,
          idToken: id_token || null,
          user,
          roles: user.roles || [],
          isAuthenticated: true,
          isLoading: false,
        })

        // 3. Start token refresh schedule
        scheduleTokenRefresh(access_token)

        // 4. Start session timeout tracking
        attachActivityListeners()
        resetSessionTimer()

        return true
      } catch (err) {
        const message =
          err.response?.data?.error_description ||
          err.response?.data?.detail ||
          err.message ||
          'Authentication failed.'
        set({ error: message, isLoading: false, isAuthenticated: false })
        return false
      }
    },

    // ── Fetch current user profile (on page reload) ──
    fetchUser: async () => {
      const token = localStorage.getItem('hact_access_token')
      if (!token) return

      try {
        const res = await apiClient.get(API.AUTH.ME)
        set({
          user: res.data,
          roles: res.data.roles || [],
          isAuthenticated: true,
        })

        // Restart refresh schedule and session timer
        scheduleTokenRefresh(token)
        attachActivityListeners()
        resetSessionTimer()
      } catch {
        // Token expired or invalid — try refresh
        const rt = localStorage.getItem('hact_refresh_token')
        if (rt) {
          try {
            const tokens = await refreshAccessToken(rt)
            localStorage.setItem('hact_access_token', tokens.access_token)
            if (tokens.refresh_token) localStorage.setItem('hact_refresh_token', tokens.refresh_token)
            if (tokens.id_token) localStorage.setItem('hact_id_token', tokens.id_token)

            set({
              accessToken: tokens.access_token,
              refreshToken: tokens.refresh_token || rt,
              idToken: tokens.id_token || null,
            })

            // Retry fetching user
            const res = await apiClient.get(API.AUTH.ME, {
              headers: { Authorization: `Bearer ${tokens.access_token}` },
            })
            set({
              user: res.data,
              roles: res.data.roles || [],
              isAuthenticated: true,
            })

            scheduleTokenRefresh(tokens.access_token)
            attachActivityListeners()
            resetSessionTimer()
          } catch {
            // Refresh also failed — logout
            get().logout()
          }
        } else {
          get().logout()
        }
      }
    },

    // ── Logout (with Keycloak session end) ──
    logout: () => {
      // Clear timers
      if (refreshTimer) clearTimeout(refreshTimer)
      if (sessionTimer) clearTimeout(sessionTimer)
      refreshTimer = null
      sessionTimer = null
      detachActivityListeners()

      const idToken = localStorage.getItem('hact_id_token')

      // Clear local storage
      localStorage.removeItem('hact_access_token')
      localStorage.removeItem('hact_refresh_token')
      localStorage.removeItem('hact_id_token')

      set({
        accessToken: null,
        refreshToken: null,
        idToken: null,
        user: null,
        roles: [],
        isAuthenticated: false,
        error: null,
      })

      // Redirect to Keycloak logout (ends SSO session too)
      const postLogoutUri = `${window.location.origin}/login`
      const logoutUrl = buildLogoutUrl(idToken, postLogoutUri)
      window.location.href = logoutUrl
    },

    // ── Role check helpers ──
    hasRole: (roleName) => {
      const { roles, user } = get()
      if (user?.is_superuser) return true
      return roles.includes(roleName)
    },

    hasAnyRole: (...roleNames) => {
      const { roles, user } = get()
      if (user?.is_superuser) return true
      return roleNames.some((r) => roles.includes(r))
    },

    clearError: () => set({ error: null }),
  }
})

export default useAuthStore
