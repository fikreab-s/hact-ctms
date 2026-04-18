import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiMapPin, FiUsers, FiCalendar, FiAlertTriangle, FiPlus } from 'react-icons/fi'
import { useStudy, useSubjects, useTransitionStudy, useCreateSite } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import usePermission from '../auth/usePermission'
import toast from 'react-hot-toast'

export default function StudyDetailPage() {
  const { id } = useParams()
  const { can } = usePermission()
  const { data: study, isLoading } = useStudy(id)
  const { data: subjectsData } = useSubjects({ study: id })
  const transition = useTransitionStudy()
  const createSite = useCreateSite()
  const [showCreateSite, setShowCreateSite] = useState(false)

  if (isLoading) return <LoadingSpinner text="Loading study..." />
  if (!study) return <p className="text-slate-500 p-6">Study not found.</p>

  const subjects = subjectsData?.results || []
  const sites = study.sites || []
  const visits = study.visits || []
  const isLocked = study.status === 'locked' || study.status === 'archived'

  const nextStatus = { planning: 'active', active: 'locked', locked: 'archived' }[study.status]

  const handleTransition = async () => {
    if (!nextStatus) return
    if (nextStatus === 'locked' && !confirm('Locking will freeze all data. Continue?')) return
    try {
      await transition.mutateAsync({ id: study.id, status: nextStatus })
      toast.success(`Study transitioned to ${nextStatus}`)
    } catch (err) {
      toast.error(err.response?.data?.status?.[0] || err.response?.data?.detail || 'Transition failed')
    }
  }

  const handleCreateSite = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await createSite.mutateAsync({
        study: parseInt(id),
        site_code: form.get('site_code'),
        name: form.get('name'),
        country: form.get('country') || 'Ethiopia',
        principal_investigator: form.get('principal_investigator'),
        status: 'active',
        activation_date: form.get('activation_date') || null,
      })
      toast.success('Site created successfully!')
      setShowCreateSite(false)
    } catch (err) {
      const detail = err.response?.data
      const message = typeof detail === 'object'
        ? Object.values(detail).flat().join(', ')
        : detail?.detail || 'Failed to create site'
      toast.error(message)
    }
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div>
        <Link to="/studies" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 mb-3">
          <FiArrowLeft className="w-4 h-4" /> Back to Studies
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 tracking-tight">{study.protocol_number}</h1>
            <p className="text-sm text-slate-500 mt-0.5">{study.name}</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={study.status} className="text-sm px-3 py-1" />
            {can('TRANSITION_STUDY') && nextStatus && (
              <button
                onClick={handleTransition}
                disabled={transition.isPending}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
              >
                {transition.isPending ? 'Processing...' : `Move to ${nextStatus}`}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Locked/Archived Study Banner */}
      {isLocked && (
        <div className="flex items-center gap-3 px-5 py-3 bg-amber-50 border border-amber-200 rounded-xl text-sm">
          <FiAlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />
          <div>
            <span className="font-semibold text-amber-800">
              {study.status === 'locked' ? 'Study Locked' : 'Study Archived'}
            </span>
            <span className="text-amber-700 ml-1">
              — All data is frozen. No subjects, visits, or form data can be modified.
            </span>
          </div>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium">Phase</p>
          <p className="text-xl font-bold text-slate-800 mt-1">{study.phase}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium">Sites</p>
          <p className="text-xl font-bold text-slate-800 mt-1">{study.site_count}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium">Subjects</p>
          <p className="text-xl font-bold text-slate-800 mt-1">{study.subject_count}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium">Enrolled</p>
          <p className="text-xl font-bold text-emerald-600 mt-1">{study.enrolled_count}</p>
        </div>
      </div>

      {/* Info + Sponsor */}
      <div className="bg-card rounded-xl border border-border p-5 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
        <div><span className="text-slate-500 block text-xs mb-1">Sponsor</span><span className="font-medium text-slate-700">{study.sponsor || '—'}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Start Date</span><span className="font-medium text-slate-700">{study.start_date || '—'}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Open Queries</span><span className="font-medium text-rose-600">{study.open_queries_count || 0}</span></div>
      </div>

      {/* Sites Table */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiMapPin className="w-4 h-4" /> Sites ({sites.length})</h3>
          {can('CREATE_SITE') && !isLocked && (
            <button
              onClick={() => setShowCreateSite(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-xs font-medium rounded-lg transition-colors"
              id="create-site-btn"
            >
              <FiPlus className="w-3.5 h-3.5" /> New Site
            </button>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium text-slate-500 uppercase border-b border-border">
                <th className="px-5 py-3">Code</th>
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Country</th>
                <th className="px-5 py-3">PI</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Enrolled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {sites.map(site => (
                <tr key={site.id} className="hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-medium text-slate-700">{site.site_code}</td>
                  <td className="px-5 py-3 text-slate-600">{site.name}</td>
                  <td className="px-5 py-3 text-slate-600">{site.country}</td>
                  <td className="px-5 py-3 text-slate-600">{site.principal_investigator}</td>
                  <td className="px-5 py-3"><StatusBadge status={site.status} /></td>
                  <td className="px-5 py-3 text-right font-medium text-emerald-600">{site.enrolled_count}</td>
                </tr>
              ))}
              {sites.length === 0 && <tr><td colSpan="6" className="px-5 py-6 text-center text-slate-400">No sites configured</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {/* Subjects Table */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiUsers className="w-4 h-4" /> Subjects ({subjectsData?.count || 0})</h3>
          <Link to="/subjects" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all →</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium text-slate-500 uppercase border-b border-border">
                <th className="px-5 py-3">Subject ID</th>
                <th className="px-5 py-3">Site</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Enrollment Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {subjects.slice(0, 10).map(s => (
                <tr key={s.id} className="hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-medium text-slate-700">{s.subject_identifier}</td>
                  <td className="px-5 py-3 text-slate-600">{s.site_code}</td>
                  <td className="px-5 py-3"><StatusBadge status={s.status} /></td>
                  <td className="px-5 py-3 text-slate-600">{s.enrollment_date || '—'}</td>
                </tr>
              ))}
              {subjects.length === 0 && <tr><td colSpan="4" className="px-5 py-6 text-center text-slate-400">No subjects enrolled</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Site Modal */}
      {can('CREATE_SITE') && showCreateSite && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowCreateSite(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-1">Add New Site</h2>
            <p className="text-sm text-slate-500 mb-5">Add a participating clinical site to {study.protocol_number}</p>
            <form onSubmit={handleCreateSite} className="space-y-4" id="create-site-form">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Site Code *</label>
                  <input name="site_code" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="ETH-ADD-001" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Country</label>
                  <input name="country" defaultValue="Ethiopia" className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Site Name *</label>
                <input name="name" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="Tikur Anbessa Hospital — Addis Ababa" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Principal Investigator</label>
                <input name="principal_investigator" className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" placeholder="Dr. Turemo Bedaso" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Activation Date</label>
                <input name="activation_date" type="date" className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreateSite(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={createSite.isPending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {createSite.isPending ? 'Creating...' : 'Create Site'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
