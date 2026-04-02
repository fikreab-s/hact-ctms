/**
 * Auth Store — Zustand
 * Manages: access token, refresh token, current user, roles
 */

import { create } from 'zustand'
import axios from 'axios'
import apiClient from '../api/client'
import { API, KEYCLOAK_TOKEN_URL, KEYCLOAK_CLIENT_ID } from '../api/endpoints'

const useAuthStore = create((set, get) => ({
  // State
  accessToken: localStorage.getItem('hact_access_token') || null,
  refreshToken: localStorage.getItem('hact_refresh_token') || null,
  user: null,
  roles: [],
  isAuthenticated: !!localStorage.getItem('hact_access_token'),
  isLoading: false,
  error: null,

  // ── Login via Keycloak password grant ──
  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      // 1. Get token from Keycloak
      const params = new URLSearchParams({
        client_id: KEYCLOAK_CLIENT_ID,
        grant_type: 'password',
        username,
        password,
      })

      const tokenRes = await axios.post(KEYCLOAK_TOKEN_URL, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      const { access_token, refresh_token } = tokenRes.data
      localStorage.setItem('hact_access_token', access_token)
      localStorage.setItem('hact_refresh_token', refresh_token)

      // 2. Fetch user profile from Django
      const meRes = await apiClient.get(API.AUTH.ME)
      const user = meRes.data

      set({
        accessToken: access_token,
        refreshToken: refresh_token,
        user,
        roles: user.roles || [],
        isAuthenticated: true,
        isLoading: false,
      })

      return true
    } catch (err) {
      const message =
        err.response?.data?.error_description ||
        err.response?.data?.detail ||
        'Login failed. Check your credentials.'
      set({ error: message, isLoading: false, isAuthenticated: false })
      return false
    }
  },

  // ── Fetch current user profile ──
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
    } catch {
      // Token expired or invalid
      get().logout()
    }
  },

  // ── Logout ──
  logout: () => {
    localStorage.removeItem('hact_access_token')
    localStorage.removeItem('hact_refresh_token')
    set({
      accessToken: null,
      refreshToken: null,
      user: null,
      roles: [],
      isAuthenticated: false,
      error: null,
    })
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
}))

export default useAuthStore
