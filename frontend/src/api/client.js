/**
 * Axios HTTP Client — preconfigured for HACT CTMS API.
 *
 * Features:
 * - Base URL: /api/v1/
 * - Bearer token injection from Zustand auth store
 * - 401 auto-logout (token expired)
 * - Request/response interceptors
 */

import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1/',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// ── Request Interceptor: Inject Bearer Token ──
apiClient.interceptors.request.use(
  (config) => {
    // Dynamically import to avoid circular deps
    const token = localStorage.getItem('hact_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor: Handle 401 ──
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('hact_access_token')
      localStorage.removeItem('hact_refresh_token')
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
