import { useState, useRef } from 'react'
import { FiUpload, FiActivity } from 'react-icons/fi'
import { useLabResults, useImportLabCSV } from '../api/queries'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import usePermission from '../auth/usePermission'
import toast from 'react-hot-toast'

export default function LabPage() {
  const { can } = usePermission()
  const [page, setPage] = useState(1)
  const [flagFilter, setFlagFilter] = useState('')
  const fileRef = useRef(null)

  const { data, isLoading } = useLabResults({ page, flag: flagFilter || undefined })
  const importCSV = useImportLabCSV()

  const results = data?.results || []
  const totalCount = data?.count || 0
  const totalPages = Math.ceil(totalCount / 25)

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

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Laboratory Results</h1>
          <p className="text-sm text-slate-500 mt-0.5">{totalCount} lab results</p>
        </div>
        {can('IMPORT_LAB_CSV') && (
          <label className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer shadow-sm">
            <FiUpload className="w-4 h-4" />
            {importCSV.isPending ? 'Importing...' : 'Import CSV'}
            <input type="file" accept=".csv" className="hidden" ref={fileRef} onChange={handleImport} disabled={importCSV.isPending} />
          </label>
        )}
      </div>

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
        <EmptyState title="No lab results" message="Import a CSV file to get started." icon={FiActivity} />
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
                  <th className="px-5 py-3">Visit</th>
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
                    <td className="px-5 py-3 text-slate-600">{r.visit_name || '—'}</td>
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
