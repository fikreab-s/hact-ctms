import { FiExternalLink, FiAlertCircle } from 'react-icons/fi'
import { useIntegrationStatus } from '../api/queries'

const SYSTEM_CONFIG = {
  openclinica: {
    label: 'OpenClinica CE',
    desc: 'Electronic Data Capture — manage CRFs, study forms, and clinical data.',
    icon: '📋',
    path: '/OpenClinica/',
    loginHint: 'root / Admin@2026!',
  },
  senaite: {
    label: 'SENAITE LIMS',
    desc: 'Laboratory Information System — manage lab samples, results, and workflows.',
    icon: '🔬',
    path: '/senaite/',
    loginHint: 'admin / admin',
  },
  nextcloud: {
    label: 'Nextcloud eTMF',
    desc: 'Document Management — upload, organize, and share trial master file documents.',
    icon: '📁',
    path: '/nextcloud/',
    loginHint: 'admin / Admin@2026!',
  },
  erpnext: {
    label: 'ERPNext',
    desc: 'Site Operations & Contracts — manage site budgets, contracts, and procurement.',
    icon: '📊',
    path: '/erpnext/',
    loginHint: 'Administrator / Admin@2026!',
  },
}

export default function ExternalSystemPage({ systemKey }) {
  const config = SYSTEM_CONFIG[systemKey]
  const { data } = useIntegrationStatus()
  const status = data?.[systemKey]?.status || 'unknown'
  const isHealthy = status === 'healthy'

  const origin = window.location.origin
  const systemUrl = `${origin}${config.path}`

  if (!config) {
    return <div className="p-8 text-slate-500">System not found.</div>
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header bar */}
      <div className="flex items-center justify-between px-5 py-3 bg-white border-b border-slate-200">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h1 className="text-lg font-semibold text-slate-800">{config.label}</h1>
            <p className="text-xs text-slate-500">{config.desc}</p>
          </div>
          <span className={`ml-3 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
            isHealthy ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${isHealthy ? 'bg-emerald-500' : 'bg-rose-500'}`} />
            {isHealthy ? 'Connected' : 'Offline'}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">Login: {config.loginHint}</span>
          <a
            href={systemUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-primary-50 text-primary-700 hover:bg-primary-100 border border-primary-200 transition-colors"
          >
            <FiExternalLink className="w-3.5 h-3.5" />
            Open in New Tab
          </a>
        </div>
      </div>

      {/* Embedded iframe */}
      {isHealthy ? (
        <div className="flex-1 relative">
          <iframe
            src={systemUrl}
            title={config.label}
            className="absolute inset-0 w-full h-full border-0"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-downloads"
          />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-3">
            <FiAlertCircle className="w-12 h-12 text-rose-300 mx-auto" />
            <h2 className="text-lg font-semibold text-slate-700">{config.label} is Offline</h2>
            <p className="text-sm text-slate-500 max-w-md">
              This service is currently unavailable. Please ensure it's running on the server.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
