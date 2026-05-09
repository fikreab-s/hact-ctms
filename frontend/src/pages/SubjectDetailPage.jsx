import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiCalendar, FiActivity, FiAlertTriangle, FiUser, FiClock } from 'react-icons/fi'
import { useSubject, useAdverseEvents, useLabResults } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import usePermission from '../auth/usePermission'
import { useWithdrawSubject } from '../api/queries'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function SubjectDetailPage() {
  const { id } = useParams()
  const { can } = usePermission()
  const { data: subject, isLoading } = useSubject(id)
  const { data: aeData } = useAdverseEvents({ subject: id })
  const { data: labData } = useLabResults({ subject: id })
  const withdraw = useWithdrawSubject()
  const [showWithdraw, setShowWithdraw] = useState(false)

  if (isLoading) return <LoadingSpinner text="Loading subject..." />
  if (!subject) return <p className="text-slate-500 p-6">Subject not found.</p>

  const adverseEvents = aeData?.results || []
  const labResults = labData?.results || []
  const visits = subject.subject_visits || []
  const saeCount = adverseEvents.filter(ae => ae.serious || ae.is_serious).length
  const abnormalLabs = labResults.filter(r => r.flag === 'H' || r.flag === 'L').length

  const handleWithdraw = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await withdraw.mutateAsync({
        id: subject.id,
        reason: form.get('reason'),
        completion_date: form.get('completion_date') || undefined,
      })
      toast.success(`Subject ${subject.subject_identifier} withdrawn.`)
      setShowWithdraw(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.reason?.[0] || 'Withdrawal failed')
    }
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div>
        <Link to="/subjects" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 mb-3">
          <FiArrowLeft className="w-4 h-4" /> Back to Subjects
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-3">
              <FiUser className="w-6 h-6 text-primary-500" />
              {subject.subject_identifier}
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {subject.study_protocol} — {subject.site_name || subject.site_code}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={subject.status} className="text-sm px-3 py-1" />
            {can('WITHDRAW_SUBJECT') && subject.status === 'enrolled' && (
              <button onClick={() => setShowWithdraw(true)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-lg transition-colors">
                Withdraw
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium flex items-center gap-1"><FiCalendar className="w-3 h-3" /> Consent Date</p>
          <p className="text-lg font-bold text-slate-800 mt-1">{subject.consent_signed_date || '—'}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium flex items-center gap-1"><FiClock className="w-3 h-3" /> Enrollment</p>
          <p className="text-lg font-bold text-slate-800 mt-1">{subject.enrollment_date || '—'}</p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium flex items-center gap-1"><FiAlertTriangle className="w-3 h-3" /> Adverse Events</p>
          <p className="text-lg font-bold text-slate-800 mt-1">{adverseEvents.length} <span className="text-xs font-normal text-rose-500">{saeCount > 0 ? `(${saeCount} SAE)` : ''}</span></p>
        </div>
        <div className="bg-card rounded-xl border border-border p-4">
          <p className="text-xs text-slate-500 font-medium flex items-center gap-1"><FiActivity className="w-3 h-3" /> Lab Results</p>
          <p className="text-lg font-bold text-slate-800 mt-1">{labResults.length} <span className="text-xs font-normal text-amber-500">{abnormalLabs > 0 ? `(${abnormalLabs} flagged)` : ''}</span></p>
        </div>
      </div>

      {/* Subject Info */}
      <div className="bg-card rounded-xl border border-border p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-sm">
        <div><span className="text-slate-500 block text-xs mb-1">Screening #</span><span className="font-medium text-slate-700">{subject.screening_number || '—'}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Study</span><span className="font-medium text-slate-700">{subject.study_protocol}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Site</span><span className="font-medium text-slate-700">{subject.site_code} — {subject.site_name}</span></div>
        <div><span className="text-slate-500 block text-xs mb-1">Completion</span><span className="font-medium text-slate-700">{subject.completion_date || '—'}</span></div>
      </div>

      {/* Visits Timeline */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiCalendar className="w-4 h-4" /> Visits ({visits.length})</h3>
        </div>
        {visits.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase border-b border-border">
                  <th className="px-5 py-3">Visit</th>
                  <th className="px-5 py-3">Scheduled</th>
                  <th className="px-5 py-3">Actual</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Window</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {visits.map(sv => (
                  <tr key={sv.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 font-medium text-slate-700">{sv.visit_name}</td>
                    <td className="px-5 py-3 text-slate-600">{sv.scheduled_date || '—'}</td>
                    <td className="px-5 py-3 text-slate-600">{sv.actual_date || '—'}</td>
                    <td className="px-5 py-3"><StatusBadge status={sv.status} /></td>
                    <td className="px-5 py-3">
                      {sv.is_within_window === true && <span className="text-xs text-emerald-600 font-medium">✓ In window</span>}
                      {sv.is_within_window === false && <span className="text-xs text-rose-600 font-medium">✗ Out of window</span>}
                      {sv.is_within_window == null && <span className="text-xs text-slate-400">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-5 py-8 text-center text-slate-400 text-sm">No visits recorded</div>
        )}
      </div>

      {/* Adverse Events */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiAlertTriangle className="w-4 h-4" /> Adverse Events ({adverseEvents.length})</h3>
          <Link to="/safety" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all →</Link>
        </div>
        {adverseEvents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase border-b border-border">
                  <th className="px-5 py-3">AE Term</th>
                  <th className="px-5 py-3">Severity</th>
                  <th className="px-5 py-3">SAE</th>
                  <th className="px-5 py-3">Causality</th>
                  <th className="px-5 py-3">Outcome</th>
                  <th className="px-5 py-3">Onset</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {adverseEvents.map(ae => (
                  <tr key={ae.id} className="hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 text-slate-700">{ae.ae_term}</td>
                    <td className="px-5 py-3"><StatusBadge status={ae.severity} /></td>
                    <td className="px-5 py-3">
                      {(ae.serious || ae.is_serious) ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">SAE</span>
                      ) : <span className="text-xs text-slate-400">No</span>}
                    </td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.causality}</td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.outcome}</td>
                    <td className="px-5 py-3 text-slate-600">{ae.onset_date || ae.start_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-5 py-8 text-center text-slate-400 text-sm">No adverse events reported</div>
        )}
      </div>

      {/* Lab Results */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2"><FiActivity className="w-4 h-4" /> Lab Results ({labResults.length})</h3>
          <Link to="/lab" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all →</Link>
        </div>
        {labResults.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase border-b border-border">
                  <th className="px-5 py-3">Test</th>
                  <th className="px-5 py-3">Result</th>
                  <th className="px-5 py-3">Unit</th>
                  <th className="px-5 py-3">Ref Range</th>
                  <th className="px-5 py-3">Flag</th>
                  <th className="px-5 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {labResults.map(r => (
                  <tr key={r.id} className={`hover:bg-card-hover transition-colors ${r.flag !== 'N' ? 'bg-rose-50/30' : ''}`}>
                    <td className="px-5 py-3 font-medium text-slate-700">{r.test_name}</td>
                    <td className="px-5 py-3 font-medium text-slate-800">{r.result_value}</td>
                    <td className="px-5 py-3 text-slate-500">{r.unit}</td>
                    <td className="px-5 py-3 text-slate-500">{r.reference_range_low}–{r.reference_range_high}</td>
                    <td className="px-5 py-3"><StatusBadge status={r.flag} /></td>
                    <td className="px-5 py-3 text-slate-600">{r.result_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-5 py-8 text-center text-slate-400 text-sm">No lab results available</div>
        )}
      </div>

      {/* Withdraw Modal */}
      {showWithdraw && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowWithdraw(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-rose-700 mb-1">Withdraw Subject</h2>
            <p className="text-sm text-slate-500 mb-5">{subject.subject_identifier} — this action cannot be undone.</p>
            <form onSubmit={handleWithdraw} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Reason for Withdrawal *</label>
                <textarea name="reason" required rows={3}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/30"
                  placeholder="e.g., Adverse event, Lost to follow-up, Consent withdrawn..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Completion Date</label>
                <input name="completion_date" type="date" className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowWithdraw(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={withdraw.isPending}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {withdraw.isPending ? 'Withdrawing...' : 'Confirm Withdrawal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
