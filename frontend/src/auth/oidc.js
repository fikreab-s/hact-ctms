/**
 * OIDC Authorization Code + PKCE Utilities
 * ==========================================
 * Implements the OAuth 2.0 Authorization Code flow with PKCE (RFC 7636)
 * for Keycloak integration. This is the recommended flow for SPAs
 * (no client secret exposed to the browser).
 *
 * PKCE flow:
 *   1. Generate random code_verifier (43-128 chars)
 *   2. Hash it with SHA-256 → base64url encode → code_challenge
 *   3. Send code_challenge to /auth endpoint
 *   4. Exchange authorization_code + code_verifier for tokens at /token endpoint
 */

import { KEYCLOAK_CLIENT_ID } from '../api/endpoints'

// ── Keycloak OIDC endpoints (via NGINX proxy) ──
const KC_BASE = '/auth/realms/hact/protocol/openid-connect'
export const OIDC_ENDPOINTS = {
  authorize: `${KC_BASE}/auth`,
  token: `${KC_BASE}/token`,
  logout: `${KC_BASE}/logout`,
  userinfo: `${KC_BASE}/userinfo`,
}

// ── PKCE: Generate cryptographically random code verifier ──
export function generateCodeVerifier() {
  const array = new Uint8Array(64)
  crypto.getRandomValues(array)
  return base64UrlEncode(array)
}

// ── PKCE: Generate code challenge from verifier (SHA-256) ──
export async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return base64UrlEncode(new Uint8Array(digest))
}

// ── Base64 URL-safe encoding (no padding) ──
function base64UrlEncode(buffer) {
  const str = String.fromCharCode(...buffer)
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

// ── Generate random state parameter (CSRF protection) ──
export function generateState() {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return base64UrlEncode(array)
}

// ── Build the authorization URL ──
export async function buildAuthorizationUrl(redirectUri) {
  const codeVerifier = generateCodeVerifier()
  const codeChallenge = await generateCodeChallenge(codeVerifier)
  const state = generateState()

  // Store verifier and state for the callback
  sessionStorage.setItem('pkce_code_verifier', codeVerifier)
  sessionStorage.setItem('pkce_state', state)
  sessionStorage.setItem('pkce_redirect_uri', redirectUri)

  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    response_type: 'code',
    scope: 'openid profile email',
    redirect_uri: redirectUri,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    state,
  })

  return `${OIDC_ENDPOINTS.authorize}?${params.toString()}`
}

// ── Exchange authorization code for tokens ──
export async function exchangeCodeForTokens(code, redirectUri) {
  const codeVerifier = sessionStorage.getItem('pkce_code_verifier')

  if (!codeVerifier) {
    throw new Error('Missing PKCE code verifier. Please login again.')
  }

  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    grant_type: 'authorization_code',
    code,
    redirect_uri: redirectUri,
    code_verifier: codeVerifier,
  })

  const response = await fetch(OIDC_ENDPOINTS.token, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.error_description || 'Token exchange failed')
  }

  // Clean up PKCE state
  sessionStorage.removeItem('pkce_code_verifier')
  sessionStorage.removeItem('pkce_state')
  sessionStorage.removeItem('pkce_redirect_uri')

  return response.json()
}

// ── Refresh access token using refresh_token ──
export async function refreshAccessToken(refreshToken) {
  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    grant_type: 'refresh_token',
    refresh_token: refreshToken,
  })

  const response = await fetch(OIDC_ENDPOINTS.token, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  })

  if (!response.ok) {
    throw new Error('Token refresh failed')
  }

  return response.json()
}

// ── Build Keycloak logout URL ──
export function buildLogoutUrl(idTokenHint, postLogoutRedirectUri) {
  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    post_logout_redirect_uri: postLogoutRedirectUri,
  })
  if (idTokenHint) {
    params.set('id_token_hint', idTokenHint)
  }
  return `${OIDC_ENDPOINTS.logout}?${params.toString()}`
}

// ── Parse JWT payload (without verification — just decoding) ──
export function parseJwtPayload(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64).split('').map(c =>
        '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      ).join('')
    )
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

// ── Get token expiry in milliseconds from now ──
export function getTokenExpiresIn(token) {
  const payload = parseJwtPayload(token)
  if (!payload?.exp) return 0
  return (payload.exp * 1000) - Date.now()
}
