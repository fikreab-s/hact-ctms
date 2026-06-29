/**
 * EDC Offline Store — IndexedDB-backed queue for offline CRF submissions.
 *
 * Features:
 * - Queues form submissions when offline
 * - Auto-syncs when navigator.onLine becomes true
 * - Caches subject list and form schemas for offline use
 * - Generates client-side UUIDs for deduplication
 */

import { create } from 'zustand'
import apiClient from '../api/client'
import { API } from '../api/endpoints'

// ── IndexedDB Helpers ──
const DB_NAME = 'hact_edc_offline'
const DB_VERSION = 1

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = (e) => {
      const db = e.target.result
      if (!db.objectStoreNames.contains('submissions')) {
        db.createObjectStore('submissions', { keyPath: 'offline_uuid' })
      }
      if (!db.objectStoreNames.contains('cache')) {
        db.createObjectStore('cache', { keyPath: 'key' })
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function dbPut(storeName, data) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    tx.objectStore(storeName).put(data)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

async function dbGetAll(storeName) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readonly')
    const req = tx.objectStore(storeName).getAll()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function dbDelete(storeName, key) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite')
    tx.objectStore(storeName).delete(key)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

async function dbGet(storeName, key) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readonly')
    const req = tx.objectStore(storeName).get(key)
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ── UUID Generator ──
function generateUUID() {
  return crypto.randomUUID?.() ||
    'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
    })
}

// ── Store ──
const useEdcStore = create((set, get) => ({
  // ── State ──
  isOnline: navigator.onLine,
  pendingCount: 0,
  isSyncing: false,
  syncErrors: [],
  lastSyncAt: null,

  // Cached data
  cachedSubjects: [],
  cachedForms: {},

  // ── Initialize: attach online/offline listeners ──
  init: () => {
    const handleOnline = () => {
      set({ isOnline: true })
      get().syncPending()
    }
    const handleOffline = () => set({ isOnline: false })

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Load pending count on init
    get().loadPendingCount()

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  },

  // ── Load pending submission count from IndexedDB ──
  loadPendingCount: async () => {
    try {
      const submissions = await dbGetAll('submissions')
      set({ pendingCount: submissions.length })
    } catch {
      set({ pendingCount: 0 })
    }
  },

  // ── Queue a CRF submission (for offline or immediate send) ──
  submitCrf: async (formData) => {
    const offlineUuid = generateUUID()
    const submission = {
      ...formData,
      offline_uuid: offlineUuid,
      captured_at: new Date().toISOString(),
      queued_at: new Date().toISOString(),
    }

    if (navigator.onLine) {
      // Try to send immediately
      try {
        const res = await apiClient.post(API.EDC_SUBMIT, submission)
        return { success: true, data: res.data, offline: false }
      } catch (err) {
        // Log the actual error for debugging
        console.error('[EDC Submit] API error:', err.response?.status, err.response?.data)

        // Extract error message from DRF response
        const errData = err.response?.data
        let errorMsg = err.message
        if (errData) {
          if (typeof errData === 'string') errorMsg = errData
          else if (errData.detail) errorMsg = errData.detail
          else if (errData.non_field_errors) errorMsg = errData.non_field_errors.join(', ')
          else errorMsg = JSON.stringify(errData)
        }

        // If server error, queue for retry
        await dbPut('submissions', submission)
        await get().loadPendingCount()
        return {
          success: false,
          error: errorMsg,
          offline: true,
          queued: true,
        }
      }
    } else {
      // Offline — queue it
      await dbPut('submissions', submission)
      await get().loadPendingCount()
      return { success: true, offline: true, queued: true }
    }
  },

  // ── Sync all pending submissions ──
  syncPending: async () => {
    if (get().isSyncing || !navigator.onLine) return

    set({ isSyncing: true, syncErrors: [] })
    const errors = []

    try {
      const submissions = await dbGetAll('submissions')

      for (const sub of submissions) {
        try {
          await apiClient.post(API.EDC_SUBMIT, sub)
          await dbDelete('submissions', sub.offline_uuid)
        } catch (err) {
          errors.push({
            offline_uuid: sub.offline_uuid,
            form_id: sub.form_id,
            subject_id: sub.subject_id,
            error: err.response?.data?.detail || err.message,
          })
        }
      }

      await get().loadPendingCount()
      set({
        isSyncing: false,
        syncErrors: errors,
        lastSyncAt: new Date().toISOString(),
      })
    } catch {
      set({ isSyncing: false })
    }
  },

  // ── Cache subjects for offline use ──
  cacheSubjects: async (subjects) => {
    set({ cachedSubjects: subjects })
    try {
      await dbPut('cache', { key: 'subjects', data: subjects, cachedAt: new Date().toISOString() })
    } catch { /* ignore cache errors */ }
  },

  // ── Get cached subjects ──
  getCachedSubjects: async () => {
    try {
      const cached = await dbGet('cache', 'subjects')
      if (cached) {
        set({ cachedSubjects: cached.data })
        return cached.data
      }
    } catch { /* ignore */ }
    return []
  },

  // ── Cache a form schema for offline use ──
  cacheFormSchema: async (formId, schema) => {
    set((state) => ({
      cachedForms: { ...state.cachedForms, [formId]: schema },
    }))
    try {
      await dbPut('cache', { key: `form_${formId}`, data: schema, cachedAt: new Date().toISOString() })
    } catch { /* ignore */ }
  },

  // ── Get cached form schema ──
  getCachedFormSchema: async (formId) => {
    // Check memory first
    const mem = get().cachedForms[formId]
    if (mem) return mem

    // Check IndexedDB
    try {
      const cached = await dbGet('cache', `form_${formId}`)
      if (cached) {
        set((state) => ({
          cachedForms: { ...state.cachedForms, [formId]: cached.data },
        }))
        return cached.data
      }
    } catch { /* ignore */ }
    return null
  },

  // ── Get all pending submissions ──
  getPendingSubmissions: async () => {
    try {
      return await dbGetAll('submissions')
    } catch {
      return []
    }
  },

  // ── Remove a specific pending submission ──
  removePending: async (offlineUuid) => {
    await dbDelete('submissions', offlineUuid)
    await get().loadPendingCount()
  },
}))

export default useEdcStore
