import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiMapPin, FiUsers, FiCalendar, FiAlertTriangle } from 'react-icons/fi'
import { useStudy, useSubjects, useTransitionStudy } from '../api/queries'
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

  if (isLoading) return <LoadingSpinner text="Loading study..." />
  if (!study) return <p className="text-slate-500 p-6">Study not found.</p>

  const subjects = subjectsData?.results || []
  const sites = study.sites || []
  const visits = study.visits || []

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
        <div className="px-5 py-4 border-b border-border">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiMapPin className="w-4 h-4" /> Sites ({sites.length})</h3>
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
    </div>
  )
}
