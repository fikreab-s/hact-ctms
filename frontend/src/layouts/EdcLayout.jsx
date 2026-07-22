/**
 * EdcLayout — Standalone mobile EDC layout.
 *
 * NO sidebar, NO dashboard navigation.
 * Just a slim header bar with: logo, user, sync status, logout.
 * Bottom bar: online/offline indicator + pending count.
 */

import { useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { HiOutlineCloudUpload, HiOutlineLogout, HiOutlineRefresh, HiOutlineStatusOnline, HiOutlineStatusOffline } from 'react-icons/hi'
import useAuthStore from '../store/authStore'
import useEdcStore from '../store/edcOfflineStore'
import FeedbackWidget from '../components/FeedbackWidget'

export default function EdcLayout() {
  const { user, logout } = useAuthStore()
  const { isOnline, pendingCount, isSyncing, init, syncPending } = useEdcStore()
  const navigate = useNavigate()

  useEffect(() => {
    const cleanup = init()
    return cleanup
  }, [init])

  return (
    <div className="flex flex-col h-dvh bg-slate-50">
      {/* ── Top Header Bar ── */}
      <header className="flex items-center justify-between px-4 py-3 bg-primary-700 text-white shadow-lg flex-shrink-0">
        {/* Left: Logo */}
        <button
          onClick={() => navigate('/edc')}
          className="flex items-center gap-2"
        >
          <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center text-sm font-bold">
            H
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight">HACT EDC</div>
            <div className="text-[10px] text-primary-200 leading-tight">Mobile Data Capture</div>
          </div>
        </button>

        {/* Right: Sync + User + Logout */}
        <div className="flex items-center gap-3">
          {/* Sync button */}
          {pendingCount > 0 && (
            <button
              onClick={syncPending}
              disabled={isSyncing || !isOnline}
              className="relative flex items-center gap-1 px-2.5 py-1.5 bg-white/15 rounded-lg text-xs font-medium hover:bg-white/25 transition disabled:opacity-50"
            >
              <HiOutlineCloudUpload className={`w-4 h-4 ${isSyncing ? 'animate-pulse' : ''}`} />
              <span>{pendingCount}</span>
            </button>
          )}

          {/* User initial */}
          <div className="w-7 h-7 bg-white/20 rounded-full flex items-center justify-center text-xs font-bold">
            {user?.first_name?.[0] || user?.username?.[0] || '?'}
          </div>

          {/* Logout */}
          <button
            onClick={logout}
            className="p-1.5 hover:bg-white/15 rounded-lg transition"
            title="Sign out"
          >
            <HiOutlineLogout className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>

      {/* ── Bottom Status Bar ── */}
      <footer className="flex items-center justify-between px-4 py-2 bg-slate-800 text-slate-300 text-xs flex-shrink-0">
        {/* Online/Offline */}
        <div className="flex items-center gap-1.5">
          {isOnline ? (
            <>
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
              <span>Online</span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 bg-rose-400 rounded-full" />
              <span className="text-rose-300">Offline — data saved locally</span>
            </>
          )}
        </div>

        {/* Pending count */}
        <div className="flex items-center gap-2">
          {pendingCount > 0 && (
            <span className="text-amber-300">
              {pendingCount} pending sync
            </span>
          )}
          {isSyncing && (
            <HiOutlineRefresh className="w-3.5 h-3.5 animate-spin text-sky-300" />
          )}
        </div>
      </footer>
      <FeedbackWidget />
    </div>
  )
}
