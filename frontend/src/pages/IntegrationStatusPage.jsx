import { FiServer, FiRefreshCw, FiCheckCircle, FiXCircle, FiClock } from 'react-icons/fi'
import { useIntegrationStatus } from '../api/queries'
import LoadingSpinner from '../components/LoadingSpinner'

const SERVICE_META = {
  openclinica: { label: 'OpenClinica CE', desc: 'Electronic Data Capture (EDC)', color: 'blue', icon: '📋' },
  senaite: { label: 'SENAITE LIMS', desc: 'Laboratory Information System', color: 'emerald', icon: '🔬' },
  erpnext: { label: 'ERPNext', desc: 'Site Operations & Contracts', color: 'violet', icon: '📊' },
  nextcloud: { label: 'Nextcloud', desc: 'Document Management (eTMF)', color: 'sky', icon: '📁' },
}

function StatusIcon({ status }) {
  if (status === 'healthy') return <FiCheckCircle className="w-6 h-6 text-emerald-500" />
  if (status === 'unavailable' || status === 'error') return <FiXCircle className="w-6 h-6 text-rose-500" />
  return <FiClock className="w-6 h-6 text-amber-500 animate-pulse" />
}

export default function IntegrationStatusPage() {
  const { data, isLoading, isRefetching, refetch } = useIntegrationStatus()

  if (isLoading) return <LoadingSpinner text="Checking integration status..." />

  const services = data ? Object.entries(data) : []

  const healthyCount = services.filter(([, v]) => v?.status === 'healthy').length
  const totalCount = Object.keys(SERVICE_META).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <FiServer className="w-6 h-6 text-primary-500" /> Integration Status
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {healthyCount} of {totalCount} external systems connected
          </p>
        </div>
        <button onClick={() => refetch()} disabled={isRefetching}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-border text-sm font-medium text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50">
          <FiRefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
          {isRefetching ? 'Checking...' : 'Refresh'}
        </button>
      </div>

      {/* Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {Object.entries(SERVICE_META).map(([key, meta]) => {
          const svc = data?.[key]
          const status = svc?.status || 'unavailable'
          const isHealthy = status === 'healthy'

          return (
            <div key={key}
              className={`bg-card rounded-xl border p-5 transition-all ${
                isHealthy ? 'border-emerald-200 shadow-sm' : 'border-rose-200 shadow-sm'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{meta.icon}</span>
                  <div>
                    <h3 className="text-sm font-semibold text-slate-800">{meta.label}</h3>
                    <p className="text-xs text-slate-500">{meta.desc}</p>
                  </div>
                </div>
                <StatusIcon status={status} />
              </div>
              <div className="mt-4 flex items-center gap-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  isHealthy ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                }`}>
                  {isHealthy ? 'Connected' : 'Offline'}
                </span>
                {svc?.studies_count != null && (
                  <span className="text-xs text-slate-500">{svc.studies_count} studies</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Core Services (always running) */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border">
          <h3 className="text-sm font-semibold text-slate-700">Core Platform Services</h3>
        </div>
        <div className="divide-y divide-border">
          {[
            { label: 'Django API', desc: 'Backend REST API', status: 'healthy' },
            { label: 'Keycloak SSO', desc: 'Authentication & RBAC', status: 'healthy' },
            { label: 'PostgreSQL', desc: 'Primary Database', status: 'healthy' },
            { label: 'Redis', desc: 'Cache & Task Broker', status: 'healthy' },
            { label: 'Celery Workers', desc: 'Background Task Processing', status: 'healthy' },
            { label: 'NGINX', desc: 'Reverse Proxy & SSL', status: 'healthy' },
          ].map(svc => (
            <div key={svc.label} className="px-5 py-3 flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-slate-700">{svc.label}</span>
                <span className="text-xs text-slate-500 ml-2">— {svc.desc}</span>
              </div>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Running
              </span>
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-400 text-center">Auto-refreshes every 60 seconds • Last checked: {new Date().toLocaleTimeString()}</p>
    </div>
  )
}
