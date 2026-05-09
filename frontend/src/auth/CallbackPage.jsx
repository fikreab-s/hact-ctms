/**
 * OIDC Callback Page
 * ==================
 * Handles the redirect back from Keycloak after successful authentication.
 * Exchanges the authorization code for tokens using PKCE code_verifier.
 */

import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { FiShield, FiAlertCircle } from 'react-icons/fi'
import useAuthStore from '../store/authStore'

export default function CallbackPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleOidcCallback } = useAuthStore()
  const [error, setError] = useState(null)
  const processingRef = useRef(false) // Prevent double-execution in StrictMode

  useEffect(() => {
    // Guard: only process once (React StrictMode runs effects twice in dev)
    if (processingRef.current) return
    processingRef.current = true

    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const errorParam = searchParams.get('error')
    const errorDesc = searchParams.get('error_description')

    // Handle Keycloak errors (e.g., user cancelled, 2FA failed)
    if (errorParam) {
      setError(errorDesc || `Authentication error: ${errorParam}`)
      return
    }

    if (!code) {
      setError('No authorization code received.')
      return
    }

    // Verify state matches (CSRF protection)
    const savedState = sessionStorage.getItem('pkce_state')
    if (state !== savedState) {
      setError('State mismatch. Possible CSRF attack. Please login again.')
      return
    }

    // Exchange code for tokens
    const redirectUri = `${window.location.origin}/auth/callback`

    handleOidcCallback(code, redirectUri)
      .then((success) => {
        if (success) {
          // Redirect to the page the user originally wanted, or dashboard
          const returnTo = sessionStorage.getItem('hact_return_to') || '/'
          sessionStorage.removeItem('hact_return_to')
          navigate(returnTo, { replace: true })
        } else {
          setError('Failed to complete authentication.')
        }
      })
      .catch((err) => {
        setError(err.message || 'Authentication failed.')
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-primary-900 to-slate-900 px-4">
        <div className="relative w-full max-w-md text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-rose-600 shadow-lg mb-4">
            <FiAlertCircle className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Authentication Failed</h1>
          <p className="text-slate-400 mb-6 text-sm">{error}</p>
          <button onClick={() => navigate('/login', { replace: true })}
            className="px-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white font-medium rounded-lg transition-all text-sm">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-primary-900 to-slate-900 px-4">
      <div className="relative w-full max-w-md text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 shadow-lg shadow-primary-600/30 mb-4 animate-pulse">
          <FiShield className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-xl font-semibold text-white">Completing sign-in...</h1>
        <p className="text-slate-400 mt-2 text-sm">Exchanging credentials securely</p>
        <div className="mt-6 flex justify-center">
          <svg className="animate-spin w-6 h-6 text-primary-400" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      </div>
    </div>
  )
}
