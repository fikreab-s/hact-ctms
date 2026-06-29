/**
 * EdcSyncStatus — Shows all queued/pending submissions and sync history.
 *
 * Features:
 * - Pending queue (from IndexedDB)
 * - Manual "Sync Now" button
 * - Recent submissions (from server)
 * - Error display with retry
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  HiOutlineArrowLeft, HiOutlineRefresh, HiOutlineCloudUpload,
  HiOutlineCheckCircle, HiOutlineExclamationCircle, HiOutlineTrash,
  HiOutlineClock,
} from 'react-icons/hi'
import apiClient from '../../api/client'
import { API } from '../../api/endpoints'
import useEdcStore from '../../store/edcOfflineStore'

export default function EdcSyncStatus() {
  const navigate = useNavigate()
  const {
    pendingCount, isSyncing, syncErrors, lastSyncAt, isOnline,
    syncPending, getPendingSubmissions, removePending,
  } = useEdcStore()

  const [pendingItems, setPendingItems] = useState([])

  // Load pending items from IndexedDB
  useEffect(() => {
    getPendingSubmissions().then(setPendingItems)
  }, [getPendingSubmissions, pendingCount])

  // Fetch recent server-side submissions
  const { data: serverData } = useQuery({
    queryKey: ['edc-sync-status'],
    queryFn: async () => {
      const res = await apiClient.get(API.EDC_SYNC_STATUS)
      return res.data
    },
    enabled: isOnline,
    refetchInterval: 30000, // refresh every 30s
  })

  const handleSync = async () => {
    await syncPending()
    getPendingSubmissions().then(setPendingItems)
  }

  const handleRemovePending = async (uuid) => {
    if (confirm('Remove this queued submission? Data will be lost.')) {
      await removePending(uuid)
      getPendingSubmissions().then(setPendingItems)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="px-4 py-3 bg-white border-b border-slate-200">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/edc')} className="p-1 -ml-1">
            <HiOutlineArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="flex-1">
            <h1 className="text-base font-semibold text-slate-800">Sync Status</h1>
            <p className="text-xs text-slate-500">
              {isOnline ? 'Online' : 'Offline'} · {pendingCount} pending
            </p>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing || !isOnline || pendingCount === 0}
            className="flex items-center gap-1.5 px-3 py-2 bg-primary-600 text-white rounded-xl
                       text-xs font-medium hover:bg-primary-700 transition disabled:opacity-50"
          >
            <HiOutlineRefresh className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            Sync Now
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {/* ── Pending Queue ── */}
        <section>
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <HiOutlineClock className="w-4 h-4" />
            Pending Queue ({pendingItems.length})
          </h2>

          {pendingItems.length === 0 ? (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
              <HiOutlineCheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="text-sm text-emerald-700 font-medium">All synced!</p>
              <p className="text-xs text-emerald-600 mt-0.5">No pending submissions</p>
            </div>
          ) : (
            <div className="space-y-2">
              {pendingItems.map((item) => (
                <div
                  key={item.offline_uuid}
                  className="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-center gap-3"
                >
                  <HiOutlineCloudUpload className="w-5 h-5 text-amber-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-700 font-medium truncate">
                      Form #{item.form_id} · Subject #{item.subject_id}
                    </p>
                    <p className="text-[10px] text-slate-500">
                      Captured: {new Date(item.captured_at).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemovePending(item.offline_uuid)}
                    className="p-1.5 text-slate-400 hover:text-rose-500 transition"
                    title="Remove"
                  >
                    <HiOutlineTrash className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Sync Errors ── */}
        {syncErrors.length > 0 && (
          <section>
            <h2 className="text-xs font-semibold text-rose-600 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <HiOutlineExclamationCircle className="w-4 h-4" />
              Sync Errors ({syncErrors.length})
            </h2>
            <div className="space-y-2">
              {syncErrors.map((err, idx) => (
                <div key={idx} className="bg-rose-50 border border-rose-200 rounded-xl p-3">
                  <p className="text-sm text-rose-700 font-medium">
                    Form #{err.form_id} · Subject #{err.subject_id}
                  </p>
                  <p className="text-xs text-rose-600 mt-0.5">{err.error}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Recent Submissions (Server) ── */}
        <section>
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <HiOutlineCheckCircle className="w-4 h-4" />
            Recent Submissions
          </h2>

          {!serverData?.submissions?.length ? (
            <p className="text-sm text-slate-400 text-center py-4">No recent submissions</p>
          ) : (
            <div className="space-y-2">
              {serverData.submissions.map((sub) => (
                <div
                  key={sub.id}
                  className="bg-white border border-slate-200 rounded-xl p-3 flex items-center gap-3"
                >
                  <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center flex-shrink-0">
                    <HiOutlineCheckCircle className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-700 font-medium truncate">
                      {sub.form_name}
                    </p>
                    <p className="text-[10px] text-slate-500">
                      {sub.subject_identifier} · {sub.status} · {new Date(sub.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Last Sync ── */}
        {lastSyncAt && (
          <p className="text-[10px] text-slate-400 text-center">
            Last sync: {new Date(lastSyncAt).toLocaleString()}
          </p>
        )}
      </div>
    </div>
  )
}
