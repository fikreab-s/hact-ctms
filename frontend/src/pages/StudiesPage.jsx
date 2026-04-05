import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FiPlus, FiSearch } from 'react-icons/fi'
import { useStudies, useCreateStudy } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import usePermission from '../auth/usePermission'
import toast from 'react-hot-toast'

export default function StudiesPage() {
  const { can } = usePermission()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useStudies({ page, search: search || undefined, status: statusFilter || undefined })
  const createStudy = useCreateStudy()

  const studies = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  const handleCreate = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await createStudy.mutateAsync({
        name: form.get('name'),
        protocol_number: form.get('protocol_number'),
        phase: form.get('phase'),
        sponsor: form.get('sponsor'),
        start_date: form.get('start_date') || null,
      })
      toast.success('Study created successfully!')
      setShowCreate(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create study')
    }
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Studies</h1>
          <p className="text-sm text-slate-500 mt-0.5">{totalCount} studies registered</p>
        </div>
        {can('CREATE_STUDY') && (
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            id="create-study-btn"
          >
            <FiPlus className="w-4 h-4" /> New Study
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search by protocol or name..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-9 pr-4 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30"
        >
          <option value="">All Statuses</option>
          <option value="planning">Planning</option>
          <option value="active">Active</option>
          <option value="locked">Locked</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <LoadingSpinner text="Loading studies..." />
      ) : studies.length === 0 ? (
        <EmptyState title="No studies found" message="Create your first study to get started." />
      ) : (
        <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                  <th className="px-5 py-3">Protocol</th>
                  <th className="px-5 py-3">Study Name</th>
                  <th className="px-5 py-3">Phase</th>
                  <th className="px-5 py-3">Sponsor</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3 text-right">Sites</th>
                  <th className="px-5 py-3 text-right">Subjects</th>
                  <th className="px-5 py-3 text-right">Enrolled</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {studies.map(study => (
                  <tr key={study.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3">
                      <Link to={`/studies/${study.id}`} className="text-primary-600 hover:text-primary-700 font-medium">
                        {study.protocol_number}
                      </Link>
                    </td>
                    <td className="px-5 py-3 text-slate-700 max-w-xs truncate">{study.name}</td>
                    <td className="px-5 py-3 text-slate-600">{study.phase}</td>
                    <td className="px-5 py-3 text-slate-600 max-w-xs truncate">{study.sponsor}</td>
                    <td className="px-5 py-3"><StatusBadge status={study.status} /></td>
                    <td className="px-5 py-3 text-right text-slate-600">{study.site_count}</td>
                    <td className="px-5 py-3 text-right text-slate-600">{study.subject_count}</td>
                    <td className="px-5 py-3 text-right font-medium text-emerald-600">{study.enrolled_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-5 py-3 border-t border-border flex items-center justify-between text-sm">
              <span className="text-slate-500">Page {page} of {totalPages} ({totalCount} total)</span>
              <div className="flex gap-2">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border border-border rounded-md text-slate-600 hover:bg-slate-50 disabled:opacity-40">Previous</button>
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-3 py-1 border border-border rounded-md text-slate-600 hover:bg-slate-50 disabled:opacity-40">Next</button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Modal — only rendered if user has permission */}
      {can('CREATE_STUDY') && showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-5">Create New Study</h2>
            <form onSubmit={handleCreate} className="space-y-4" id="create-study-form">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Protocol Number *</label>
                <input name="protocol_number" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="HACT-2026-002" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Study Name *</label>
                <input name="name" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="Phase III RCT of..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Phase</label>
                  <select name="phase" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="I">Phase I</option>
                    <option value="II">Phase II</option>
                    <option value="III" selected>Phase III</option>
                    <option value="IV">Phase IV</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Start Date</label>
                  <input name="start_date" type="date" className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Sponsor</label>
                <input name="sponsor" className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="Horn of Africa Clinical Trials" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={createStudy.isPending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {createStudy.isPending ? 'Creating...' : 'Create Study'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
