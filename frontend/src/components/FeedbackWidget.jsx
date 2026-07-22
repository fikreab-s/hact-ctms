/**
 * FeedbackWidget — In-app UAT feedback (TEMPORARY).
 * ==================================================
 * A floating "Feedback" button available on every authenticated page. Users can
 * report a Bug / Question / Suggestion, optionally attaching a screenshot of the
 * current page (captured client-side with html2canvas). Everything is posted to
 * the HACT backend (/api/v1/feedback/items/) — no third-party service.
 *
 * REMOVAL: this whole feature is temporary for User Acceptance Testing.
 *  - Disable instantly: set VITE_UAT_FEEDBACK="false" (frontend) and
 *    UAT_FEEDBACK_ENABLED=false (backend), then rebuild/redeploy.
 *  - Full teardown: see backend/feedback/README.md.
 */
import { useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import toast from 'react-hot-toast'
import {
  FiMessageSquare, FiX, FiCamera, FiTrash2, FiSend, FiLoader,
} from 'react-icons/fi'
import apiClient from '../api/client'
import { API } from '../api/endpoints'
import useAuthStore from '../store/authStore'

// Master switch — default ON during UAT; set VITE_UAT_FEEDBACK="false" to hide.
const FEEDBACK_ENABLED = import.meta.env.VITE_UAT_FEEDBACK !== 'false'

const CATEGORIES = [
  { value: 'bug', label: '🐞 Bug' },
  { value: 'question', label: '❓ Question' },
  { value: 'suggestion', label: '💡 Suggestion' },
  { value: 'other', label: '💬 Other' },
]
const SEVERITIES = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
]

function dataUrlToBlob(dataUrl) {
  const [head, body] = dataUrl.split(',')
  const mime = /:(.*?);/.exec(head)?.[1] || 'image/jpeg'
  const bin = atob(body)
  const arr = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i)
  return new Blob([arr], { type: mime })
}

export default function FeedbackWidget() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [shot, setShot] = useState(null) // data URL or null
  const [form, setForm] = useState({ category: 'bug', severity: 'medium', message: '' })

  const captureAndOpen = useCallback(async () => {
    setBusy(true)
    try {
      const { default: html2canvas } = await import('html2canvas')
      const canvas = await html2canvas(document.body, {
        logging: false,
        useCORS: true,
        backgroundColor: '#ffffff',
        scale: Math.min(1, window.devicePixelRatio || 1),
        ignoreElements: (el) => el.hasAttribute?.('data-feedback-ignore'),
      })
      // Compress to keep the upload small.
      setShot(canvas.toDataURL('image/jpeg', 0.8))
    } catch (e) {
      // Screenshot is best-effort — still let the user send text feedback.
      setShot(null)
      toast('Couldn\u2019t capture a screenshot — you can still send text feedback.')
    } finally {
      setBusy(false)
      setOpen(true)
    }
  }, [])

  const reset = () => {
    setForm({ category: 'bug', severity: 'medium', message: '' })
    setShot(null)
    setOpen(false)
  }

  const submit = async () => {
    if (!form.message.trim()) {
      toast.error('Please describe the issue or suggestion.')
      return
    }
    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('category', form.category)
      fd.append('severity', form.severity)
      fd.append('message', form.message.trim())
      fd.append('page_url', window.location.href)
      if (shot) fd.append('screenshot', dataUrlToBlob(shot), 'screenshot.jpg')
      await apiClient.post(API.FEEDBACK, fd, { headers: { 'Content-Type': undefined } })
      toast.success('Thanks! Your feedback was sent.')
      reset()
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Could not send feedback. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (!FEEDBACK_ENABLED || !isAuthenticated) return null

  return (
    <div data-feedback-ignore>
      {/* Floating launcher */}
      {!open && (
        <button
          type="button"
          onClick={captureAndOpen}
          disabled={busy}
          title="Send UAT feedback"
          className="fixed bottom-5 right-5 z-[9998] flex items-center gap-2 rounded-full
                     bg-indigo-600 px-4 py-3 text-white shadow-lg hover:bg-indigo-700
                     disabled:opacity-70 transition-colors"
        >
          {busy ? <FiLoader className="animate-spin" /> : <FiMessageSquare />}
          <span className="text-sm font-medium">{busy ? 'Capturing…' : 'Feedback'}</span>
        </button>
      )}

      {/* Modal */}
      {open && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 p-4"
             data-feedback-ignore>
          <div className="w-full max-w-lg rounded-xl bg-white shadow-2xl max-h-[90vh] overflow-auto">
            <div className="flex items-center justify-between border-b px-5 py-3">
              <h2 className="text-base font-semibold text-gray-800">Send feedback</h2>
              <button onClick={reset} className="text-gray-400 hover:text-gray-600" title="Close">
                <FiX size={20} />
              </button>
            </div>

            <div className="space-y-4 px-5 py-4">
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-gray-600">Type</span>
                  <select
                    value={form.category}
                    onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                    className="w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
                  >
                    {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1 block text-xs font-medium text-gray-600">Severity</span>
                  <select
                    value={form.severity}
                    onChange={(e) => setForm((f) => ({ ...f, severity: e.target.value }))}
                    className="w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
                  >
                    {SEVERITIES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </label>
              </div>

              <label className="block">
                <span className="mb-1 block text-xs font-medium text-gray-600">
                  What happened / what would you change?
                </span>
                <textarea
                  value={form.message}
                  onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
                  rows={4}
                  autoFocus
                  placeholder="Describe the issue, question, or suggestion…"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                />
              </label>

              {/* Screenshot preview + controls */}
              <div className="rounded-md border border-gray-200 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600">Screenshot</span>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={captureAndOpen}
                      disabled={busy}
                      className="flex items-center gap-1 rounded border border-gray-300 px-2 py-1 text-xs text-gray-700 hover:bg-gray-50"
                    >
                      <FiCamera size={13} /> Recapture
                    </button>
                    {shot && (
                      <button
                        type="button"
                        onClick={() => setShot(null)}
                        className="flex items-center gap-1 rounded border border-gray-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50"
                      >
                        <FiTrash2 size={13} /> Remove
                      </button>
                    )}
                  </div>
                </div>
                {shot ? (
                  <img src={shot} alt="screenshot preview"
                       className="max-h-40 w-full rounded border border-gray-200 object-contain" />
                ) : (
                  <p className="text-xs text-gray-400">No screenshot attached.</p>
                )}
              </div>

              <p className="text-[11px] text-gray-400">
                We also attach the page URL, your username/role, and browser info to help triage.
              </p>
            </div>

            <div className="flex justify-end gap-2 border-t px-5 py-3">
              <button onClick={reset}
                      className="rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-100">
                Cancel
              </button>
              <button
                onClick={submit}
                disabled={submitting}
                className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-70"
              >
                {submitting ? <FiLoader className="animate-spin" /> : <FiSend />}
                {submitting ? 'Sending…' : 'Send feedback'}
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </div>
  )
}
