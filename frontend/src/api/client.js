/**
 * Axios HTTP Client — preconfigured for HACT CTMS API.
 *
 * Features:
 * - Base URL: /api/v1/
 * - Bearer token injection from localStorage
 * - 401 interceptor with automatic token refresh retry
 * - Queues failed requests during refresh to avoid race conditions
 */

import axios from 'axios'
import { refreshAccessToken } from '../auth/oidc'

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
    const token = localStorage.getItem('hact_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor: Handle 401 with token refresh ──
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Only handle 401 errors (unauthorized / token expired)
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // If already refreshing, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return apiClient(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    const refreshToken = localStorage.getItem('hact_refresh_token')

    if (!refreshToken) {
      // No refresh token — redirect to login
      isRefreshing = false
      processQueue(new Error('No refresh token'), null)
      localStorage.removeItem('hact_access_token')
      localStorage.removeItem('hact_refresh_token')
      localStorage.removeItem('hact_id_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    try {
      const tokens = await refreshAccessToken(refreshToken)

      localStorage.setItem('hact_access_token', tokens.access_token)
      if (tokens.refresh_token) {
        localStorage.setItem('hact_refresh_token', tokens.refresh_token)
      }
      if (tokens.id_token) {
        localStorage.setItem('hact_id_token', tokens.id_token)
      }

      isRefreshing = false
      processQueue(null, tokens.access_token)

      // Retry the original request with new token
      originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`
      return apiClient(originalRequest)
    } catch (refreshError) {
      // Refresh failed — logout
      isRefreshing = false
      processQueue(refreshError, null)
      localStorage.removeItem('hact_access_token')
      localStorage.removeItem('hact_refresh_token')
      localStorage.removeItem('hact_id_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(refreshError)
    }
  }
)

/**
 * Download an auth-protected file through the API client so the Bearer token
 * (and 401→refresh handling) is applied — then trigger a browser save.
 *
 * The API returns URLs like `/api/v1/outputs/snapshots/7/download/`; the axios
 * client already prefixes `/api/v1/`, so we strip it to get the relative path.
 * Using `window.open()` on these URLs fails because a plain navigation does not
 * carry the Authorization header, yielding a 401.
 */
export async function downloadFile(downloadUrl) {
  const relative = String(downloadUrl).replace(/^\/?api\/v1\//, '').replace(/^\//, '')
  const res = await apiClient.get(relative, { responseType: 'blob' })

  const contentType = res.headers['content-type'] || 'application/octet-stream'
  const disposition = res.headers['content-disposition'] || ''
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition)
  const filename = match
    ? decodeURIComponent(match[1])
    : relative.replace(/\/+$/, '').split('/').filter(Boolean).slice(-2, -1)[0] || 'download'

  const blobUrl = URL.createObjectURL(new Blob([res.data], { type: contentType }))
  const a = document.createElement('a')
  a.href = blobUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(blobUrl)
  return filename
}

export default apiClient
