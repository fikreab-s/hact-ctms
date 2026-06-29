/**
 * EdcSubjectList — Mobile subject list for CRCs.
 *
 * Features:
 * - Search subjects by ID
 * - Status filter tabs
 * - Pull-to-refresh
 * - Offline cache
 * - "Enroll New" floating button
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { HiOutlineSearch, HiOutlinePlus, HiOutlineChevronRight, HiOutlineCalendar, HiOutlineUser } from 'react-icons/hi'
import apiClient from '../../api/client'
import { API } from '../../api/endpoints'
import useEdcStore from '../../store/edcOfflineStore'

const STATUS_TABS = [
  { key: '', label: 'All' },
  { key: 'enrolled', label: 'Enrolled' },
  { key: 'screened', label: 'Screened' },
  { key: 'completed', label: 'Completed' },
]

const STATUS_COLORS = {
  enrolled: 'bg-emerald-100 text-emerald-700',
  screened: 'bg-sky-100 text-sky-700',
  completed: 'bg-indigo-100 text-indigo-700',
  discontinued: 'bg-rose-100 text-rose-700',
  screen_failed: 'bg-slate-100 text-slate-600',
}

export default function EdcSubjectList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const { cacheSubjects, getCachedSubjects, isOnline } = useEdcStore()

  const { data: subjects, isLoading, refetch } = useQuery({
    queryKey: ['edc-subjects', search, statusFilter],
    queryFn: async () => {
      const params = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await apiClient.get(API.EDC_SUBJECTS, { params })
      return res.data.results || res.data
    },
    staleTime: 30 * 1000,
    retry: 1,
  })

  // Cache subjects for offline use
  useEffect(() => {
    if (subjects?.length) {
      cacheSubjects(subjects)
    }
  }, [subjects, cacheSubjects])

  // Load cached subjects when offline
  const [offlineSubjects, setOfflineSubjects] = useState([])
  useEffect(() => {
    if (!isOnline) {
      getCachedSubjects().then(setOfflineSubjects)
    }
  }, [isOnline, getCachedSubjects])

  const displaySubjects = isOnline ? (subjects || []) : offlineSubjects

  return (
    <div className="flex flex-col h-full">
      {/* ── Search Bar ── */}
      <div className="px-4 pt-4 pb-2">
        <div className="relative">
          <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search subject ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent
                       shadow-sm placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* ── Status Tabs ── */}
      <div className="flex gap-2 px-4 pb-3 overflow-x-auto scrollbar-none">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setStatusFilter(tab.key)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all
              ${statusFilter === tab.key
                ? 'bg-primary-600 text-white shadow-sm'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── Subject Cards ── */}
      <div className="flex-1 overflow-y-auto px-4 pb-20 space-y-2.5">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin mb-3" />
            <span className="text-sm">Loading subjects...</span>
          </div>
        ) : displaySubjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <HiOutlineUser className="w-12 h-12 mb-3 text-slate-300" />
            <span className="text-sm font-medium">No subjects found</span>
            <span className="text-xs mt-1">Tap + to enroll a new subject</span>
          </div>
        ) : (
          displaySubjects.map((subject) => (
            <button
              key={subject.id}
              onClick={() => navigate(`/edc/subject/${subject.id}`)}
              className="w-full bg-white rounded-xl border border-slate-200 p-4 text-left
                         hover:shadow-md hover:border-primary-300 transition-all active:scale-[0.99]"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Subject ID */}
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-slate-800 truncate">
                      {subject.subject_identifier}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${STATUS_COLORS[subject.status] || 'bg-slate-100 text-slate-600'}`}>
                      {subject.status}
                    </span>
                  </div>

                  {/* Site */}
                  <div className="text-xs text-slate-500 mt-1">
                    {subject.site_name} · {subject.site_code}
                  </div>

                  {/* Enrollment info */}
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                    {subject.enrollment_date && (
                      <span className="flex items-center gap-1">
                        <HiOutlineCalendar className="w-3.5 h-3.5" />
                        {subject.enrollment_date}
                      </span>
                    )}
                    {subject.pending_visits > 0 && (
                      <span className="text-amber-600 font-medium">
                        {subject.pending_visits} visit{subject.pending_visits > 1 ? 's' : ''} due
                      </span>
                    )}
                  </div>
                </div>

                <HiOutlineChevronRight className="w-5 h-5 text-slate-300 mt-1 flex-shrink-0" />
              </div>
            </button>
          ))
        )}
      </div>

      {/* ── Floating Enroll Button ── */}
      <button
        onClick={() => navigate('/edc/enroll')}
        className="fixed bottom-16 right-5 w-14 h-14 bg-primary-600 text-white rounded-full shadow-xl
                   flex items-center justify-center hover:bg-primary-700 active:scale-95 transition-all
                   z-50"
      >
        <HiOutlinePlus className="w-7 h-7" />
      </button>
    </div>
  )
}
