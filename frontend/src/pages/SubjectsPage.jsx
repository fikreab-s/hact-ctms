import { useState } from 'react'
import { FiSearch } from 'react-icons/fi'
import { useSubjects, useEnrollSubject } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import toast from 'react-hot-toast'

export default function SubjectsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [enrollModal, setEnrollModal] = useState(null)

  const { data, isLoading } = useSubjects({ page, search: search || undefined, status: statusFilter || undefined })
  const enroll = useEnrollSubject()

  const subjects = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  const handleEnroll = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await enroll.mutateAsync({
        id: enrollModal.id,
        consent_signed_date: form.get('consent_signed_date'),
        enrollment_date: form.get('enrollment_date'),
      })
      toast.success(`Subject ${enrollModal.subject_identifier} enrolled!`)
      setEnrollModal(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Enrollment failed')
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Subjects</h1>
        <p className="text-sm text-slate-500 mt-0.5">{totalCount} subjects across all studies</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input type="text" placeholder="Search by ID or screening number..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-9 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400" />
        </div>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
          <option value="">All Statuses</option>
          <option value="screened">Screened</option>
          <option value="enrolled">Enrolled</option>
          <option value="completed">Completed</option>
          <option value="discontinued">Discontinued</option>
          <option value="screen_failed">Screen Failed</option>
        </select>
      </div>

      {isLoading ? <LoadingSpinner text="Loading subjects..." /> : subjects.length === 0 ? (
        <EmptyState title="No subjects found" message="Subjects will appear here once they are registered in a study." />
      ) : (
        <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                  <th className="px-5 py-3">Subject ID</th>
                  <th className="px-5 py-3">Study</th>
                  <th className="px-5 py-3">Site</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Consent Date</th>
                  <th className="px-5 py-3">Enrollment Date</th>
                  <th className="px-5 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {subjects.map(s => (
                  <tr key={s.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-700">{s.subject_identifier}</td>
                    <td className="px-5 py-3 text-slate-600">{s.study_protocol}</td>
                    <td className="px-5 py-3 text-slate-600">{s.site_code}</td>
                    <td className="px-5 py-3"><StatusBadge status={s.status} /></td>
                    <td className="px-5 py-3 text-slate-600">{s.consent_signed_date || '—'}</td>
                    <td className="px-5 py-3 text-slate-600">{s.enrollment_date || '—'}</td>
                    <td className="px-5 py-3">
                      {s.status === 'screened' && (
                        <button onClick={() => setEnrollModal(s)} className="text-xs text-primary-600 hover:text-primary-700 font-medium">Enroll</button>
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

      {/* Enroll Modal */}
      {enrollModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setEnrollModal(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-1">Enroll Subject</h2>
            <p className="text-sm text-slate-500 mb-5">{enrollModal.subject_identifier} at {enrollModal.site_code}</p>
            <form onSubmit={handleEnroll} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Consent Signed Date *</label>
                <input name="consent_signed_date" type="date" required className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Enrollment Date</label>
                <input name="enrollment_date" type="date" className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setEnrollModal(null)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={enroll.isPending} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {enroll.isPending ? 'Enrolling...' : 'Enroll Subject'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
