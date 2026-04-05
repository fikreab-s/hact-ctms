import { useState } from 'react'
import { FiDownload } from 'react-icons/fi'
import { useAuditLogs } from '../api/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import usePermission from '../auth/usePermission'
import apiClient from '../api/client'
import toast from 'react-hot-toast'

export default function AuditPage() {
  const { can } = usePermission()
  const [page, setPage] = useState(1)
  const [actionFilter, setActionFilter] = useState('')

  const { data, isLoading } = useAuditLogs({ page, action: actionFilter || undefined })

  const logs = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  const handleExport = async () => {
    try {
      toast.loading('Exporting audit trail...', { id: 'export' })
      // Fetch all pages of audit logs
      let allLogs = []
      let nextPage = 1
      let hasMore = true
      while (hasMore) {
        const res = await apiClient.get('audit/logs/', { params: { page: nextPage, page_size: 100 } })
        allLogs = allLogs.concat(res.data.results || [])
        hasMore = !!res.data.next
        nextPage++
      }

      // Build CSV
      const headers = ['Timestamp', 'User', 'Action', 'Table', 'Record ID', 'Changes']
      const rows = allLogs.map(log => [
        log.timestamp || log.created_at || '',
        log.user_username || log.user || '',
        log.action || '',
        log.table_name || '',
        log.record_id || '',
        log.changes ? JSON.stringify(log.changes).replace(/"/g, '""') : '',
      ])
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit_trail_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast.success(`Exported ${allLogs.length} audit records!`, { id: 'export' })
    } catch (err) {
      toast.error('Failed to export audit trail', { id: 'export' })
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Audit Trail</h1>
          <p className="text-sm text-slate-500 mt-0.5">{totalCount} audit log entries</p>
        </div>
        {can('EXPORT_AUDIT') && (
          <button onClick={handleExport} className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm" id="export-audit-btn">
            <FiDownload className="w-4 h-4" /> Export CSV
          </button>
        )}
      </div>

      <div className="flex items-center gap-3">
        <select value={actionFilter} onChange={(e) => { setActionFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
          <option value="">All Actions</option>
          <option value="CREATE">Create</option>
          <option value="UPDATE">Update</option>
          <option value="DELETE">Delete</option>
        </select>
      </div>

      {isLoading ? <LoadingSpinner text="Loading audit logs..." /> : logs.length === 0 ? (
        <EmptyState title="No audit logs" message="System activity will be tracked here." />
      ) : (
        <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                  <th className="px-5 py-3">Timestamp</th>
                  <th className="px-5 py-3">User</th>
                  <th className="px-5 py-3">Action</th>
                  <th className="px-5 py-3">Table</th>
                  <th className="px-5 py-3">Record ID</th>
                  <th className="px-5 py-3">Changes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 text-slate-600 text-xs whitespace-nowrap">{new Date(log.timestamp || log.created_at).toLocaleString()}</td>
                    <td className="px-5 py-3 text-slate-700 font-medium">{log.user_username || log.user || '—'}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                        log.action === 'CREATE' ? 'bg-emerald-100 text-emerald-700' :
                        log.action === 'UPDATE' ? 'bg-sky-100 text-sky-700' :
                        log.action === 'DELETE' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-600'
                      }`}>{log.action}</span>
                    </td>
                    <td className="px-5 py-3 text-slate-600">{log.table_name || '—'}</td>
                    <td className="px-5 py-3 text-slate-500">{log.record_id || '—'}</td>
                    <td className="px-5 py-3 text-slate-500 text-xs max-w-xs truncate">{log.changes ? JSON.stringify(log.changes).substring(0, 80) : '—'}</td>
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
