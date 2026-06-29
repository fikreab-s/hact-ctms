/**
 * EdcVisitSchedule — Visit timeline for a subject.
 *
 * Shows all visits with status: Done (green), Due (amber), Future (gray), Missed (red).
 * Tap a Due/Planned visit → opens the CRF form selection.
 */

import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  HiOutlineArrowLeft, HiOutlineCheckCircle, HiOutlineClock,
  HiOutlineExclamationCircle, HiOutlineChevronRight, HiOutlineDocumentText,
} from 'react-icons/hi'
import apiClient from '../../api/client'
import { API } from '../../api/endpoints'

const VISIT_STATUS_CONFIG = {
  completed: {
    icon: HiOutlineCheckCircle,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50 border-emerald-200',
    dot: 'bg-emerald-500',
    label: 'Completed',
  },
  planned: {
    icon: HiOutlineClock,
    color: 'text-amber-600',
    bg: 'bg-amber-50 border-amber-200',
    dot: 'bg-amber-500',
    label: 'Due',
  },
  missed: {
    icon: HiOutlineExclamationCircle,
    color: 'text-rose-600',
    bg: 'bg-rose-50 border-rose-200',
    dot: 'bg-rose-500',
    label: 'Missed',
  },
}

export default function EdcVisitSchedule() {
  const { subjectId } = useParams()
  const navigate = useNavigate()

  // Fetch subject details with visits
  const { data: subject, isLoading } = useQuery({
    queryKey: ['edc-subject', subjectId],
    queryFn: async () => {
      const res = await apiClient.get(`${API.EDC_SUBJECTS}${subjectId}/`)
      return res.data
    },
    staleTime: 0,  // Always refetch — visit status may have changed after CRF submit
  })

  const visits = subject?.visits || []

  // Determine if a visit is actionable (can fill CRF)
  const isActionable = (visit) =>
    visit.status === 'planned' || visit.status === 'completed'

  const handleVisitTap = (visit) => {
    if (!isActionable(visit)) return
    navigate(`/edc/subject/${subjectId}/visit/${visit.id}/forms`)
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
          <button onClick={() => navigate('/edc')} className="p-1 -ml-1">
            <HiOutlineArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="text-base font-semibold text-slate-800 truncate">
              {subject?.subject_identifier}
            </h1>
            <p className="text-xs text-slate-500">
              {subject?.site_name} · {subject?.status}
            </p>
          </div>
        </div>
      </div>

      {/* ── Subject Info Card ── */}
      <div className="mx-4 mt-4 p-3.5 bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <span className="text-slate-400 block">Enrolled</span>
            <span className="text-slate-700 font-medium">{subject?.enrollment_date || '—'}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Consent</span>
            <span className="text-slate-700 font-medium">{subject?.consent_signed_date || '—'}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Study</span>
            <span className="text-slate-700 font-medium truncate block">{subject?.study_name}</span>
          </div>
          <div>
            <span className="text-slate-400 block">Screening #</span>
            <span className="text-slate-700 font-medium">{subject?.screening_number || '—'}</span>
          </div>
        </div>
      </div>

      {/* ── Visit Timeline ── */}
      <div className="px-4 pt-4 pb-2">
        <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
          <HiOutlineDocumentText className="w-4 h-4" />
          Visit Schedule
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-8">
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-slate-200" />

          {/* Visit items */}
          <div className="space-y-3">
            {visits.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">No visits scheduled</p>
            ) : (
              visits.map((visit, idx) => {
                const config = VISIT_STATUS_CONFIG[visit.status] || VISIT_STATUS_CONFIG.planned
                const Icon = config.icon
                const actionable = isActionable(visit)

                return (
                  <button
                    key={idx}
                    onClick={() => handleVisitTap(visit)}
                    disabled={!actionable}
                    className={`w-full relative pl-10 pr-3 py-3 rounded-xl border text-left transition-all
                      ${actionable
                        ? `${config.bg} hover:shadow-md active:scale-[0.99] cursor-pointer`
                        : 'bg-slate-50 border-slate-100 cursor-default opacity-60'
                      }`}
                  >
                    {/* Timeline dot */}
                    <div className={`absolute left-[11px] top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full ${config.dot} ring-2 ring-white`} />

                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-slate-800 truncate">
                            {visit.visit_name}
                          </span>
                          <span className={`text-[10px] font-medium ${config.color}`}>
                            {config.label}
                          </span>
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          Day {visit.planned_day}
                          {visit.scheduled_date && ` · ${visit.scheduled_date}`}
                          {visit.actual_date && ` · Done ${visit.actual_date}`}
                        </div>
                        {visit.forms_completed !== undefined && (
                          <div className="text-[10px] text-slate-400 mt-1">
                            {visit.forms_completed}/{visit.forms_total} forms completed
                          </div>
                        )}
                      </div>

                      {actionable && (
                        <HiOutlineChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
