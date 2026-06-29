/**
 * EdcVisitForms — Lists available CRFs for a specific visit.
 *
 * Shows which forms are available, which are completed, and which need filling.
 * Tap a form → opens the CRF form renderer.
 */

import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  HiOutlineArrowLeft, HiOutlineDocumentText, HiOutlineCheckCircle,
  HiOutlinePencilAlt, HiOutlineChevronRight, HiOutlineLockClosed,
} from 'react-icons/hi'
import apiClient from '../../api/client'

const FORM_STATUS_CONFIG = {
  submitted: { icon: HiOutlineCheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50', label: 'Submitted' },
  signed: { icon: HiOutlineLockClosed, color: 'text-indigo-600', bg: 'bg-indigo-50', label: 'Signed' },
  locked: { icon: HiOutlineLockClosed, color: 'text-slate-500', bg: 'bg-slate-100', label: 'Locked' },
  draft: { icon: HiOutlinePencilAlt, color: 'text-amber-600', bg: 'bg-amber-50', label: 'Draft' },
  null: { icon: HiOutlineDocumentText, color: 'text-primary-600', bg: 'bg-primary-50', label: 'Not Started' },
}

export default function EdcVisitForms() {
  const { subjectId, visitId } = useParams()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['edc-visit-forms', subjectId, visitId],
    queryFn: async () => {
      const res = await apiClient.get(
        `edc/subjects/${subjectId}/visits/${visitId}/forms/`
      )
      return res.data
    },
  })

  const forms = data?.forms || []

  const handleFormTap = (form) => {
    // Locked forms can't be edited
    if (form.instance_status === 'locked' || form.instance_status === 'signed') return
    navigate(`/edc/subject/${subjectId}/visit/${visitId}/form/${form.id}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="px-4 py-3 bg-white border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/edc/subject/${subjectId}`)} className="p-1 -ml-1">
            <HiOutlineArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="text-base font-semibold text-slate-800 truncate">
              {data?.visit_name}
            </h1>
            <p className="text-xs text-slate-500">
              {data?.subject_identifier} · {forms.length} form{forms.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </div>

      {/* ── Form List ── */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {forms.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <HiOutlineDocumentText className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p className="text-sm font-medium">No forms assigned</p>
            <p className="text-xs mt-1">Contact your study coordinator</p>
          </div>
        ) : (
          forms.map((form) => {
            const statusKey = form.instance_status || 'null'
            const config = FORM_STATUS_CONFIG[statusKey] || FORM_STATUS_CONFIG['null']
            const Icon = config.icon
            const isLocked = statusKey === 'locked' || statusKey === 'signed'

            return (
              <button
                key={form.id}
                onClick={() => handleFormTap(form)}
                disabled={isLocked}
                className={`w-full flex items-center gap-3 p-4 rounded-xl border text-left transition-all
                  ${isLocked
                    ? 'bg-slate-50 border-slate-100 opacity-60 cursor-not-allowed'
                    : 'bg-white border-slate-200 hover:shadow-md hover:border-primary-300 active:scale-[0.99]'
                  }`}
              >
                {/* Icon */}
                <div className={`w-10 h-10 ${config.bg} rounded-xl flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-5 h-5 ${config.color}`} />
                </div>

                {/* Form info */}
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-slate-800 truncate">
                    {form.name}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={`text-[10px] font-medium ${config.color}`}>
                      {config.label}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      · v{form.version} · {form.items?.length || 0} fields
                    </span>
                  </div>
                </div>

                {!isLocked && (
                  <HiOutlineChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
                )}
              </button>
            )
          })
        )}
      </div>
    </div>
  )
}
