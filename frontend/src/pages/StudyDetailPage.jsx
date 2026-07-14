import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  FiArrowLeft, FiMapPin, FiUsers, FiCalendar, FiAlertTriangle,
  FiPlus, FiDownload, FiFileText, FiFlag, FiCheckCircle, FiClock, FiEdit2,
} from 'react-icons/fi'
import {
  useStudy, useSubjects, useTransitionStudy, useCreateSite, useUpdateStudy,
  useExportCSV, useExportODM, useMilestones, useCreateMilestone, useUpdateMilestone,
} from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import usePermission from '../auth/usePermission'
import { downloadFile } from '../api/client'
import toast from 'react-hot-toast'

export default function StudyDetailPage() {
  const { id } = useParams()
  const { can } = usePermission()
  const { data: study, isLoading } = useStudy(id)
  const { data: subjectsData } = useSubjects({ study: id })
  const transition = useTransitionStudy()
  const createSite = useCreateSite()
  const updateStudy = useUpdateStudy()
  const exportCSV = useExportCSV()
  const exportODM = useExportODM()
  const { data: milestonesData } = useMilestones({ study: id })
  const createMilestone = useCreateMilestone()
  const updateMilestone = useUpdateMilestone()
  const [showCreateSite, setShowCreateSite] = useState(false)
  const [showCreateMilestone, setShowCreateMilestone] = useState(false)
  const [showEdit, setShowEdit] = useState(false)

  if (isLoading) return <LoadingSpinner text="Loading study..." />
  if (!study) return <p className="text-slate-500 p-6">Study not found.</p>

  const subjects = subjectsData?.results || []
  const sites = study.sites || []
  const visits = study.visits || []
  const milestones = milestonesData?.results || []
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

  const handleEdit = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await updateStudy.mutateAsync({
        id: study.id,
        name: form.get('name'),
        sponsor: form.get('sponsor'),
        phase: form.get('phase'),
        start_date: form.get('start_date') || null,
        openclinica_study_oid: form.get('openclinica_study_oid')?.trim() || '',
        openclinica_study_identifier: form.get('openclinica_study_identifier')?.trim() || '',
      })
      toast.success('Study updated')
      setShowEdit(false)
    } catch (err) {
      const detail = err.response?.data
      const message = typeof detail === 'object'
        ? Object.values(detail).flat().join(', ')
        : detail?.detail || 'Failed to update study'
      toast.error(message)
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

  const handleExport = async (type) => {
    const fn = type === 'csv' ? exportCSV : exportODM
    try {
      const result = await fn.mutateAsync({ study: parseInt(id) })
      toast.success(`${type.toUpperCase()} export generated!`)
      if (result.download_url) await downloadFile(result.download_url)
    } catch (err) {
      toast.error(err.response?.data?.detail || `${type.toUpperCase()} export failed`)
    }
  }

  const handleCreateMilestone = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await createMilestone.mutateAsync({
        study: parseInt(id),
        milestone_type: form.get('milestone_type'),
        planned_date: form.get('planned_date'),
        status: 'planned',
      })
      toast.success('Milestone created')
      setShowCreateMilestone(false)
      e.target.reset()
    } catch (err) {
      toast.error('Failed to create milestone')
    }
  }

  const handleCompleteMilestone = async (msId) => {
    try {
      await updateMilestone.mutateAsync({ id: msId, status: 'completed', actual_date: new Date().toISOString().split('T')[0] })
      toast.success('Milestone completed')
    } catch (err) {
      toast.error('Failed to update milestone')
    }
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div>
        <Link to="/studies" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 mb-3">
          <FiArrowLeft className="w-4 h-4" /> Back to Studies
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">{study.protocol_number}</h1>
            <p className="text-sm text-slate-500 mt-0.5">{study.name}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <StatusBadge status={study.status} className="text-sm px-3 py-1" />
            {can('CREATE_STUDY') && !isLocked && (
              <button
                onClick={() => setShowEdit(true)}
                className="inline-flex items-center gap-1.5 px-3 py-2 border border-border text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                id="edit-study-btn"
              >
                <FiEdit2 className="w-4 h-4" /> Edit
              </button>
            )}
            {can('TRANSITION_STUDY') && nextStatus && (
              <button
                onClick={handleTransition}
                disabled={transition.isPending}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
              >
                {transition.isPending ? 'Processing...' : `Move to ${nextStatus}`}
              </button>
            )}
            {can('EXPORT_CSV') && (
              <button onClick={() => handleExport('csv')}
                disabled={exportCSV.isPending}
                className="inline-flex items-center gap-1.5 px-3 py-2 border border-border text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors disabled:opacity-50">
                <FiDownload className="w-4 h-4" /> {exportCSV.isPending ? 'Exporting...' : 'CSV'}
              </button>
            )}
            {can('EXPORT_ODM') && (
              <button onClick={() => handleExport('odm')}
                disabled={exportODM.isPending}
                className="inline-flex items-center gap-1.5 px-3 py-2 border border-emerald-200 text-sm font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors disabled:opacity-50">
                <FiFileText className="w-4 h-4" /> {exportODM.isPending ? 'Exporting...' : 'ODM XML'}
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
      <div className="bg-card rounded-xl border border-border p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-sm">
        <div><span className="text-slate-500 block text-xs mb-1">Sponsor</span><span className="font-medium text-slate-700">{study.sponsor || '—'}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Start Date</span><span className="font-medium text-slate-700">{study.start_date || '—'}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Open Queries</span><span className="font-medium text-rose-600">{study.open_queries_count || 0}</span></div>
        <div>
          <span className="text-slate-500 block text-xs mb-1">OpenClinica Protocol ID</span>
          {study.openclinica_study_identifier
            ? <span className="font-medium text-slate-700 font-mono">{study.openclinica_study_identifier}</span>
            : <span className="font-medium text-amber-600">Not linked</span>}
        </div>
        <div>
          <span className="text-slate-500 block text-xs mb-1">OpenClinica OID</span>
          {study.openclinica_study_oid
            ? <span className="font-medium text-slate-700 font-mono">{study.openclinica_study_oid}</span>
            : <span className="font-medium text-amber-600">—</span>}
        </div>
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

      {/* ── Milestones ── */}
      <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FiFlag className="w-4 h-4 text-primary-500" />
            <h2 className="font-semibold text-slate-800">Milestones</h2>
            <span className="text-xs text-slate-400 ml-1">
              {milestones.filter(m => m.status === 'completed').length}/{milestones.length} completed
            </span>
          </div>
          {can('MANAGE_MILESTONES') && !isLocked && (
            <button onClick={() => setShowCreateMilestone(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg hover:bg-primary-100 transition-colors">
              <FiPlus className="w-3.5 h-3.5" /> Add Milestone
            </button>
          )}
        </div>

        {milestones.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-slate-400">
            No milestones defined yet.
          </div>
        ) : (
          <div className="divide-y divide-border">
            {milestones.map(ms => (
              <div key={ms.id} className="px-5 py-3 flex items-center justify-between hover:bg-card-hover transition-colors">
                <div className="flex items-center gap-3">
                  {ms.status === 'completed' ? (
                    <FiCheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
                  ) : ms.status === 'delayed' ? (
                    <FiAlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                  ) : (
                    <FiClock className="w-4 h-4 text-slate-400 shrink-0" />
                  )}
                  <div>
                    <p className={`text-sm font-medium ${ms.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-700'}`}>
                      {ms.milestone_type}
                    </p>
                    <p className="text-xs text-slate-400">
                      Planned: {ms.planned_date}
                      {ms.actual_date && <span className="ml-2 text-emerald-600">✓ {ms.actual_date}</span>}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={ms.status} />
                  {can('MANAGE_MILESTONES') && ms.status !== 'completed' && (
                    <button onClick={() => handleCompleteMilestone(ms.id)}
                      className="text-xs text-emerald-600 hover:text-emerald-700 font-medium hover:underline">
                      Complete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Milestone Modal */}
      {can('MANAGE_MILESTONES') && showCreateMilestone && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowCreateMilestone(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Add Milestone</h2>
            <form onSubmit={handleCreateMilestone} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Milestone Type *</label>
                <select name="milestone_type" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                  <option value="">Select...</option>
                  <option value="First Patient In">First Patient In</option>
                  <option value="50% Enrollment">50% Enrollment</option>
                  <option value="Last Patient In">Last Patient In</option>
                  <option value="Last Patient Out">Last Patient Out</option>
                  <option value="Database Lock">Database Lock</option>
                  <option value="Statistical Analysis Complete">Statistical Analysis Complete</option>
                  <option value="Final Report">Final Report</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Planned Date *</label>
                <input name="planned_date" type="date" required className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreateMilestone(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={createMilestone.isPending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {createMilestone.isPending ? 'Creating...' : 'Add Milestone'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Study Modal */}
      {can('CREATE_STUDY') && showEdit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowEdit(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-slate-800 mb-1">Edit Study</h2>
            <p className="text-sm text-slate-500 mb-5">{study.protocol_number}</p>
            <form onSubmit={handleEdit} className="space-y-4" id="edit-study-form">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Study Name *</label>
                <input name="name" required defaultValue={study.name} className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Phase</label>
                  <select name="phase" defaultValue={study.phase} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="I">Phase I</option>
                    <option value="II">Phase II</option>
                    <option value="III">Phase III</option>
                    <option value="IV">Phase IV</option>
                    <option value="I/II">Phase I/II</option>
                    <option value="II/III">Phase II/III</option>
                    <option value="NA">Not Applicable</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Start Date</label>
                  <input name="start_date" type="date" defaultValue={study.start_date || ''} className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Sponsor</label>
                <input name="sponsor" defaultValue={study.sponsor} className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">OpenClinica Unique Protocol ID</label>
                <input name="openclinica_study_identifier" defaultValue={study.openclinica_study_identifier} className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 font-mono" placeholder="HACTPSBIV2 (optional)" />
                <p className="text-xs text-slate-400 mt-1">The OpenClinica study's "Unique Protocol ID". Required for enrolled subjects to sync to the EDC. This is NOT the S_… OID.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">OpenClinica Study OID</label>
                <input name="openclinica_study_oid" defaultValue={study.openclinica_study_oid} className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 font-mono" placeholder="S_HACTPSBI (optional)" />
                <p className="text-xs text-slate-400 mt-1">The OpenClinica-generated Study OID (used when importing form data). Leave blank to disable OpenClinica sync.</p>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowEdit(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={updateStudy.isPending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {updateStudy.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
