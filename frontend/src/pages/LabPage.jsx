import { useState, useRef } from 'react'
import { FiUpload, FiActivity, FiRefreshCw, FiPlus, FiDroplet } from 'react-icons/fi'
import {
  useLabResults, useImportLabCSV,
  useSamples, useCreateSample, useSyncLabResults,
  useSubjects,
} from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import usePermission from '../auth/usePermission'
import toast from 'react-hot-toast'

const SAMPLE_TYPES = ['Blood', 'Serum', 'Plasma', 'Urine', 'CSF', 'Stool', 'Swab', 'Tissue']

export default function LabPage() {
  const { can } = usePermission()
  const [tab, setTab] = useState('results')
  const [page, setPage] = useState(1)
  const [flagFilter, setFlagFilter] = useState('')
  const [showSample, setShowSample] = useState(false)
  const fileRef = useRef(null)

  const { data, isLoading } = useLabResults({ page, flag: flagFilter || undefined })
  const { data: samplesData, isLoading: samplesLoading } = useSamples()
  const importCSV = useImportLabCSV()
  const createSample = useCreateSample()
  const syncResults = useSyncLabResults()

  const results = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)
  const samples = samplesData?.results || samplesData || []

  const handleImport = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await importCSV.mutateAsync(formData)
      toast.success(`Imported ${res.imported_count || 0} lab results!`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'CSV import failed')
    }
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleSync = async () => {
    try {
      const res = await syncResults.mutateAsync({})
      toast.success(res.task_result || 'Lab results synced from SENAITE.')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Sync failed')
    }
  }

  const handleCreateSample = async (e) => {
    e.preventDefault()
    const form = e.target
    const payload = {
      subject: form.subject.value,
      sample_type: form.sample_type.value,
      collection_date: form.collection_date.value,
    }
    try {
      await createSample.mutateAsync(payload)
      toast.success('Sample registered — pushing to SENAITE...')
      setShowSample(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to register sample')
    }
  }

  const TabButton = ({ id, label, count }) => (
    <button
      onClick={() => setTab(id)}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
        tab === id ? 'bg-primary-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
      }`}
    >
      {label}{typeof count === 'number' ? ` (${count})` : ''}
    </button>
  )

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">Laboratory</h1>
          <p className="text-sm text-slate-500 mt-0.5">{totalCount} results · {samples.length} samples</p>
        </div>
        <div className="flex items-center gap-2">
          {can('SYNC_LAB_RESULTS') && (
            <button
              onClick={handleSync}
              disabled={syncResults.isPending}
              className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              <FiRefreshCw className={`w-4 h-4 ${syncResults.isPending ? 'animate-spin' : ''}`} />
              {syncResults.isPending ? 'Syncing...' : 'Sync from SENAITE'}
            </button>
          )}
          {can('REGISTER_SAMPLE') && (
            <button
              onClick={() => setShowSample(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
            >
              <FiPlus className="w-4 h-4" /> Register Sample
            </button>
          )}
          {can('IMPORT_LAB_CSV') && (
            <label className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg transition-colors cursor-pointer">
              <FiUpload className="w-4 h-4" />
              {importCSV.isPending ? 'Importing...' : 'Import CSV'}
              <input type="file" accept=".csv" className="hidden" ref={fileRef} onChange={handleImport} disabled={importCSV.isPending} />
            </label>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <TabButton id="results" label="Results" count={totalCount} />
        <TabButton id="samples" label="Samples" count={samples.length} />
      </div>

      {tab === 'results' && (
        <>
          <div className="flex items-center gap-3">
            <select value={flagFilter} onChange={(e) => { setFlagFilter(e.target.value); setPage(1) }}
              className="px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
              <option value="">All Flags</option>
              <option value="N">Normal</option>
              <option value="H">High</option>
              <option value="L">Low</option>
            </select>
          </div>

          {isLoading ? <LoadingSpinner text="Loading lab results..." /> : results.length === 0 ? (
            <EmptyState title="No lab results" message="Register a sample, sync from SENAITE, or import a CSV to get started." icon={FiActivity} />
          ) : (
            <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                      <th className="px-5 py-3">Subject</th>
                      <th className="px-5 py-3">Test</th>
                      <th className="px-5 py-3">Result</th>
                      <th className="px-5 py-3">Unit</th>
                      <th className="px-5 py-3">Ref Range</th>
                      <th className="px-5 py-3">Flag</th>
                      <th className="px-5 py-3">Date</th>
                      <th className="px-5 py-3">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {results.map(r => (
                      <tr key={r.id} className="hover:bg-card-hover transition-colors">
                        <td className="px-5 py-3 font-medium text-slate-700">{r.subject_identifier}</td>
                        <td className="px-5 py-3 text-slate-700">{r.test_name}</td>
                        <td className="px-5 py-3 font-medium text-slate-800">{r.result_value}</td>
                        <td className="px-5 py-3 text-slate-500">{r.unit}</td>
                        <td className="px-5 py-3 text-slate-500">{r.reference_range_low}–{r.reference_range_high}</td>
                        <td className="px-5 py-3"><StatusBadge status={r.flag} /></td>
                        <td className="px-5 py-3 text-slate-600">{r.result_date}</td>
                        <td className="px-5 py-3 text-slate-500">{r.senaite_sample_id || '—'}</td>
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
        </>
      )}

      {tab === 'samples' && (
        samplesLoading ? <LoadingSpinner text="Loading samples..." /> : samples.length === 0 ? (
          <EmptyState title="No samples registered" message="Register a sample to push it to SENAITE for analysis." icon={FiDroplet} />
        ) : (
          <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border bg-slate-50/50">
                    <th className="px-5 py-3">Subject</th>
                    <th className="px-5 py-3">Sample Type</th>
                    <th className="px-5 py-3">Collection Date</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3">SENAITE ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {samples.map(s => (
                    <tr key={s.id} className="hover:bg-card-hover transition-colors">
                      <td className="px-5 py-3 font-medium text-slate-700">{s.subject_identifier}</td>
                      <td className="px-5 py-3 text-slate-700">{s.sample_type}</td>
                      <td className="px-5 py-3 text-slate-600">{s.collection_date}</td>
                      <td className="px-5 py-3"><StatusBadge status={s.status} /></td>
                      <td className="px-5 py-3 text-slate-500">
                        {s.senaite_sample_id || <span className="text-amber-500">pending…</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      )}

      {can('REGISTER_SAMPLE') && showSample && (
        <RegisterSampleModal
          onClose={() => setShowSample(false)}
          onSubmit={handleCreateSample}
          pending={createSample.isPending}
        />
      )}
    </div>
  )
}

function RegisterSampleModal({ onClose, onSubmit, pending }) {
  const { data: subjectsData } = useSubjects({ page_size: 500 })
  const subjects = subjectsData?.results || subjectsData || []
  const today = new Date().toISOString().slice(0, 10)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">Register Sample</h2>
        <p className="text-sm text-slate-500 mb-5">Records a collection in CTMS and automatically registers it in SENAITE for lab analysis.</p>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Subject *</label>
            <select name="subject" required className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
              <option value="">Select a subject...</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>{s.subject_identifier}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Sample Type *</label>
            <select name="sample_type" required defaultValue="Blood" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/30">
              {SAMPLE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Collection Date *</label>
            <input type="date" name="collection_date" required defaultValue={today} max={today} className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg">Cancel</button>
            <button type="submit" disabled={pending} className="px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg disabled:opacity-50">
              {pending ? 'Registering...' : 'Register & Push to SENAITE'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
