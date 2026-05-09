import { useState } from 'react'
import { FiAlertTriangle, FiPlus, FiFileText, FiDownload } from 'react-icons/fi'
import { useAdverseEvents, useCreateAdverseEvent, useSubjects, useCreateCiomsForm, useGenerateCiomsPdf } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import usePermission from '../auth/usePermission'
import toast from 'react-hot-toast'

export default function SafetyPage() {
  const { can } = usePermission()
  const [page, setPage] = useState(1)
  const [saeOnly, setSaeOnly] = useState(false)
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useAdverseEvents({ page, serious: saeOnly ? 'true' : undefined })
  const createAE = useCreateAdverseEvent()
  const { data: subjectsData } = useSubjects({ page_size: 200, status: 'enrolled' })
  const subjects = subjectsData?.results || []
  const createCioms = useCreateCiomsForm()
  const generatePdf = useGenerateCiomsPdf()

  const handleGenerateCioms = async (aeId) => {
    try {
      const cioms = await createCioms.mutateAsync({ adverse_event: aeId, status: 'draft' })
      const result = await generatePdf.mutateAsync(cioms.id)
      toast.success('CIOMS I PDF generated!')
      if (result.download_url) window.open(result.download_url, '_blank')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate CIOMS PDF')
    }
  }

  const events = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

  const handleCreate = async (e) => {
    e.preventDefault()
    const form = new FormData(e.target)
    try {
      await createAE.mutateAsync({
        subject: parseInt(form.get('subject')),
        ae_term: form.get('ae_term'),
        onset_date: form.get('onset_date'),
        severity: form.get('severity'),
        is_serious: form.get('is_serious') === 'true',
        seriousness_criteria: form.get('seriousness_criteria') || '',
        causality: form.get('causality'),
        outcome: form.get('outcome'),
        action_taken: form.get('action_taken'),
        description: form.get('description'),
      })
      toast.success('Adverse event reported successfully.')
      setShowCreate(false)
    } catch (err) {
      const detail = err.response?.data
      const message = typeof detail === 'object'
        ? Object.values(detail).flat().join(', ')
        : detail?.detail || 'Failed to report adverse event'
      toast.error(message)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Safety & Adverse Events</h1>
          <p className="text-sm text-slate-500 mt-0.5">{totalCount} adverse events recorded</p>
        </div>
        {can('CREATE_AE') && (
          <button onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            id="create-ae-btn">
            <FiPlus className="w-4 h-4" /> Report AE
          </button>
        )}
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
                  {can('GENERATE_CIOMS') && <th className="px-5 py-3 text-center">CIOMS</th>}
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
                      {(ae.serious || ae.is_serious) ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">
                          <FiAlertTriangle className="w-3 h-3" /> SAE
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">No</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.causality_display || ae.causality}</td>
                    <td className="px-5 py-3 text-slate-600 capitalize">{ae.outcome_display || ae.outcome}</td>
                    <td className="px-5 py-3 text-slate-600">{ae.onset_date || ae.start_date}</td>
                    <td className="px-5 py-3 text-right font-medium text-slate-700">{ae.days_open}</td>
                    {can('GENERATE_CIOMS') && (
                      <td className="px-5 py-3 text-center">
                        {(ae.serious || ae.is_serious) ? (
                          <button onClick={() => handleGenerateCioms(ae.id)}
                            disabled={generatePdf.isPending}
                            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-violet-700 bg-violet-50 hover:bg-violet-100 rounded-md transition-colors disabled:opacity-50"
                            title="Generate CIOMS I PDF">
                            <FiFileText className="w-3 h-3" /> CIOMS
                          </button>
                        ) : (
                          <span className="text-xs text-slate-300">—</span>
                        )}
                      </td>
                    )}
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

      {/* Create AE Modal */}
      {can('CREATE_AE') && showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setShowCreate(false)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-rose-700 mb-1">Report Adverse Event</h2>
            <p className="text-sm text-slate-500 mb-5">Record a new AE/SAE for an enrolled subject</p>
            <form onSubmit={handleCreate} className="space-y-4" id="create-ae-form">
              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Subject *</label>
                <select name="subject" required className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-rose-500/30">
                  <option value="">Select enrolled subject...</option>
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.subject_identifier} — {s.site_code} ({s.study_protocol})</option>
                  ))}
                </select>
              </div>

              {/* AE Term */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">AE Term *</label>
                <input name="ae_term" required className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/30"
                  placeholder="e.g., Headache, Nausea, Severe anemia" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Onset Date */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Onset Date *</label>
                  <input name="onset_date" type="date" required className="w-full px-3 py-2 border border-border rounded-lg text-sm" />
                </div>

                {/* Severity */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Severity *</label>
                  <select name="severity" required className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="">Select...</option>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Is Serious */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Serious Adverse Event (SAE)?</label>
                  <select name="is_serious" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="false">No</option>
                    <option value="true">Yes — SAE</option>
                  </select>
                </div>

                {/* Seriousness Criteria */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">SAE Criteria</label>
                  <select name="seriousness_criteria" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="">N/A</option>
                    <option value="death">Death</option>
                    <option value="life_threatening">Life-threatening</option>
                    <option value="required_hospitalization">Requires hospitalization</option>
                    <option value="persistent_disability">Persistent disability</option>
                    <option value="congenital_anomaly">Congenital anomaly</option>
                    <option value="medically_important">Medically important</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Causality */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Causality *</label>
                  <select name="causality" required className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="">Select...</option>
                    <option value="not_related">Not related</option>
                    <option value="unlikely">Unlikely</option>
                    <option value="possible">Possible</option>
                    <option value="probably_related">Probably related</option>
                    <option value="definitely_related">Definitely related</option>
                  </select>
                </div>

                {/* Outcome */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Outcome *</label>
                  <select name="outcome" required className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white">
                    <option value="">Select...</option>
                    <option value="recovered">Recovered</option>
                    <option value="recovering">Recovering</option>
                    <option value="not_recovered">Not recovered</option>
                    <option value="fatal">Fatal</option>
                    <option value="unknown">Unknown</option>
                  </select>
                </div>
              </div>

              {/* Action Taken */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Action Taken</label>
                <input name="action_taken" className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/30"
                  placeholder="e.g., Drug interrupted, dose reduced, concomitant medication" />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <textarea name="description" rows={3}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/30"
                  placeholder="Detailed narrative of the adverse event..." />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
                <button type="submit" disabled={createAE.isPending}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
                  {createAE.isPending ? 'Reporting...' : 'Report Adverse Event'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
