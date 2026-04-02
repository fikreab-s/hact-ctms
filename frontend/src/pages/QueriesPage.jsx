import { useState } from 'react'
import { FiSearch } from 'react-icons/fi'
import { useQueries as useQueriesData, useAnswerQuery, useCloseQuery } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import toast from 'react-hot-toast'

export default function QueriesPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')
  const [answerModal, setAnswerModal] = useState(null)

  const { data, isLoading } = useQueriesData({ page, status: statusFilter || undefined })
  const answerQuery = useAnswerQuery()
  const closeQuery = useCloseQuery()

  const queries = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  const handleAnswer = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await answerQuery.mutateAsync({ id: answerModal.id, response_text: form.get('response_text') })
      toast.success('Query answered!')
      setAnswerModal(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to answer query')
    }
  }

  const handleClose = async (query) => {
    try {
      await closeQuery.mutateAsync({ id: query.id, reason: 'Resolved' })
      toast.success('Query closed!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to close query')
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Queries</h1>
        <p className="text-sm text-slate-500 mt-0.5">{totalCount} data queries</p>
      </div>

      <div className="flex items-center gap-3">
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="answered">Answered</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      {isLoading ? <LoadingSpinner text="Loading queries..." /> : queries.length === 0 ? (
        <EmptyState title="No queries found" message="Queries are generated during data review." />
      ) : (
        <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                  <th className="px-5 py-3">ID</th>
                  <th className="px-5 py-3">Subject</th>
                  <th className="px-5 py-3">Form</th>
                  <th className="px-5 py-3">Field</th>
                  <th className="px-5 py-3">Query Text</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Raised By</th>
                  <th className="px-5 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {queries.map(q => (
                  <tr key={q.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 text-slate-500">#{q.id}</td>
                    <td className="px-5 py-3 font-medium text-slate-700">{q.subject_identifier || '—'}</td>
                    <td className="px-5 py-3 text-slate-600">{q.form_name || '—'}</td>
                    <td className="px-5 py-3 text-slate-600">{q.field_name || '—'}</td>
                    <td className="px-5 py-3 text-slate-700 max-w-xs truncate">{q.query_text}</td>
                    <td className="px-5 py-3"><StatusBadge status={q.status} /></td>
                    <td className="px-5 py-3 text-slate-600">{q.raised_by_username || '—'}</td>
                    <td className="px-5 py-3 flex gap-2">
                      {q.status === 'open' && (
                        <button onClick={() => setAnswerModal(q)} className="text-xs text-primary-600 hover:text-primary-700 font-medium">Answer</button>
                      )}
                      {(q.status === 'open' || q.status === 'answered') && (
                        <button onClick={() => handleClose(q)} className="text-xs text-slate-500 hover:text-slate-700 font-medium">Close</button>
                      )}
                    </td>
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

      {/* Answer Modal */}
      {answerModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setAnswerModal(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-1">Answer Query</h2>
            <p className="text-sm text-slate-500 mb-4">{answerModal.query_text}</p>
            <form onSubmit={handleAnswer} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Response *</label>
                <textarea name="response_text" required rows="3" className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="Explain the correction..." />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setAnswerModal(null)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={answerQuery.isPending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {answerQuery.isPending ? 'Sending...' : 'Submit Answer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
