import { useState } from 'react'
import { FiAlertTriangle } from 'react-icons/fi'
import { useAdverseEvents } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'

export default function SafetyPage() {
  const [page, setPage] = useState(1)
  const [saeOnly, setSaeOnly] = useState(false)

  const { data, isLoading } = useAdverseEvents({ page, serious: saeOnly ? 'true' : undefined })

  const events = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Safety & Adverse Events</h1>
        <p className="text-sm text-slate-500 mt-0.5">{totalCount} adverse events recorded</p>
      </div>

      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
          <input type="checkbox" checked={saeOnly} onChange={(e) => { setSaeOnly(e.target.checked); setPage(1) }}
            className="w-4 h-4 rounded border-border text-rose-600 focus:ring-rose-500" />
          Show SAEs only
        </label>
      </div>

      {isLoading ? <LoadingSpinner text="Loading adverse events..." /> : events.length === 0 ? (
        <EmptyState title="No adverse events" message="Safety events will be tracked here." icon={FiAlertTriangle} />
      ) : (
        <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                  <th className="px-5 py-3">ID</th>
                  <th className="px-5 py-3">Subject</th>
                  <th className="px-5 py-3">AE Term</th>
                  <th className="px-5 py-3">Severity</th>
                  <th className="px-5 py-3">SAE</th>
                  <th className="px-5 py-3">Causality</th>
                  <th className="px-5 py-3">Outcome</th>
                  <th className="px-5 py-3">Start Date</th>
                  <th className="px-5 py-3 text-right">Days Open</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {events.map(ae => (
                  <tr key={ae.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 text-slate-500">#{ae.id}</td>
                    <td className="px-5 py-3 font-medium text-slate-700">{ae.subject_identifier}</td>
                    <td className="px-5 py-3 text-slate-700">{ae.ae_term}</td>
                    <td className="px-5 py-3"><StatusBadge status={ae.severity} /></td>
                    <td className="px-5 py-3">
                      {ae.serious ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">
                          <FiAlertTriangle className="w-3 h-3" /> SAE
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">No</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.causality_display || ae.causality}</td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.outcome_display || ae.outcome}</td>
                    <td className="px-5 py-3 text-slate-600">{ae.start_date}</td>
                    <td className="px-5 py-3 text-right font-medium text-slate-700">{ae.days_open}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="px-5 py-3 border-t border-border flex items-center justify-between text-sm">
              <span className="text-slate-500">Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border border-border rounded-md text-slate-600 hover:bg-slate-50 disabled:opacity-40">Previous</button>
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-3 py-1 border border-border rounded-md text-slate-600 hover:bg-slate-50 disabled:opacity-40">Next</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
