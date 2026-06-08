/**
 * Login Page — OIDC Authorization Code + PKCE
 * =============================================
 * Instead of a username/password form, this page redirects
 * the user to Keycloak's login page. Keycloak handles:
 *   - Username/password authentication
 *   - Two-Factor Authentication (OTP/TOTP)
 *   - Account lockout and password policies
 *   - "Remember me" and SSO session management
 *
 * After successful authentication, Keycloak redirects back
 * to /auth/callback with an authorization code.
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiShield, FiLock, FiCheckCircle } from 'react-icons/fi'
import useAuthStore from '../store/authStore'
import { buildAuthorizationUrl } from './oidc'

export default function LoginPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [isRedirecting, setIsRedirecting] = useState(false)

  // If already authenticated, go to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const handleLogin = async () => {
    setIsRedirecting(true)
    try {
      const redirectUri = `${window.location.origin}/auth/callback`
      const authUrl = await buildAuthorizationUrl(redirectUri)
      window.location.href = authUrl
    } catch (err) {
      console.error('Failed to build auth URL:', err)
      setIsRedirecting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-primary-900 to-slate-900 px-4">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      <div className="relative w-full max-w-md">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 shadow-lg shadow-primary-600/30 mb-4">
            <FiShield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">HACT CTMS</h1>
          <p className="text-slate-400 mt-2 text-sm">Clinical Trial Management System</p>
        </div>

        {/* Login Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-3">Sign in to your account</h2>
          <p className="text-slate-400 text-sm mb-6">
            You'll be redirected to the secure Keycloak identity provider for authentication.
          </p>

          {/* Security Features */}
          <div className="space-y-2.5 mb-6">
            {[
              { icon: FiLock, text: 'Secure OIDC Authorization Code + PKCE' },
              { icon: FiCheckCircle, text: 'Two-Factor Authentication (if enabled)' },
              { icon: FiShield, text: 'ICH-GCP & 21 CFR Part 11 compliant' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3 text-sm text-slate-300">
                <Icon className="w-4 h-4 text-primary-400 shrink-0" />
                <span>{text}</span>
              </div>
            ))}
          </div>

          <button
            onClick={handleLogin}
            disabled={isRedirecting}
            id="login-button"
            className="w-full py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/25 hover:shadow-primary-500/40 text-sm"
          >
            {isRedirecting ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Redirecting to Keycloak...
              </span>
            ) : (
              'Sign in with Keycloak SSO'
            )}
          </button>
        </div>

        <p className="text-center text-slate-500 text-xs mt-6">
          Horn of Africa Clinical Trials — ICH-GCP Compliant
        </p>
      </div>
    </div>
  )
}
