/**
 * EdcCrfForm — Industry-standard dynamic CRF form renderer.
 *
 * Implements all 6 gaps:
 *  1. Skip logic / conditional display
 *  2. Edit existing CRFs (pre-fill from server)
 *  3. E-signature PIN on submit (password modal)
 *  4. Audit trail (server-side — changes tracked per field)
 *  5. Cross-field validation
 *  6. Form-visit mapping (handled in EdcVisitForms)
 */

import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  HiOutlineArrowLeft, HiOutlineCheck, HiOutlineSave,
  HiOutlineCamera, HiOutlineExclamation, HiOutlineCloudUpload,
  HiOutlineLockClosed, HiOutlinePencilAlt, HiOutlineShieldCheck,
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import apiClient from '../../api/client'
import { API } from '../../api/endpoints'
import useEdcStore from '../../store/edcOfflineStore'

// ═══════════════════════════════════════════════════════════════
// Field Renderers
// ═══════════════════════════════════════════════════════════════

function TextField({ item, value, onChange, error, disabled }) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={item.field_label}
      disabled={disabled}
      className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                  focus:outline-none focus:ring-2 focus:ring-primary-400
                  disabled:bg-slate-100 disabled:text-slate-500
                  ${error ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
    />
  )
}

function NumberField({ item, value, onChange, error, disabled }) {
  return (
    <input
      type="number"
      inputMode="decimal"
      step="any"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={item.field_label}
      disabled={disabled}
      className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                  focus:outline-none focus:ring-2 focus:ring-primary-400
                  disabled:bg-slate-100 disabled:text-slate-500
                  ${error ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
    />
  )
}

function DateField({ item, value, onChange, error, disabled }) {
  return (
    <input
      type="date"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                  focus:outline-none focus:ring-2 focus:ring-primary-400
                  disabled:bg-slate-100 disabled:text-slate-500
                  ${error ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
    />
  )
}

function RadioField({ item, value, onChange, error, disabled }) {
  const options = item.options || []
  return (
    <div className={`flex flex-wrap gap-2 ${error ? 'ring-1 ring-rose-400 rounded-xl p-2' : ''}`}>
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => !disabled && onChange(String(opt.value))}
          disabled={disabled}
          className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all border
            ${String(value) === String(opt.value)
              ? 'bg-primary-600 text-white border-primary-600 shadow-sm'
              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 active:scale-95'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

function DropdownField({ item, value, onChange, error, disabled }) {
  const options = item.options || []
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                  focus:outline-none focus:ring-2 focus:ring-primary-400
                  disabled:bg-slate-100 disabled:text-slate-500
                  ${error ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
    >
      <option value="">Select...</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  )
}

function TextareaField({ item, value, onChange, error, disabled }) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={item.field_label}
      rows={3}
      disabled={disabled}
      className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm resize-none
                  focus:outline-none focus:ring-2 focus:ring-primary-400
                  disabled:bg-slate-100 disabled:text-slate-500
                  ${error ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
    />
  )
}

function CheckboxField({ item, value, onChange, disabled }) {
  return (
    <label className="flex items-center gap-3 py-2 cursor-pointer">
      <input
        type="checkbox"
        checked={value === '1' || value === 'true'}
        onChange={(e) => onChange(e.target.checked ? '1' : '0')}
        disabled={disabled}
        className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-400"
      />
      <span className="text-sm text-slate-700">{item.field_label}</span>
    </label>
  )
}

function PhotoField({ item, value, onChange, disabled }) {
  const inputRef = useRef(null)
  const [preview, setPreview] = useState(value || null)

  const handleCapture = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setPreview(reader.result)
      onChange(reader.result)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div>
      <input ref={inputRef} type="file" accept="image/*" capture="environment" onChange={handleCapture} className="hidden" />
      {preview ? (
        <div className="relative">
          <img src={preview} alt="Captured" className="w-full h-40 object-cover rounded-xl border border-slate-200" />
          {!disabled && (
            <button type="button" onClick={() => inputRef.current?.click()}
              className="absolute bottom-2 right-2 px-3 py-1.5 bg-white/90 rounded-lg text-xs font-medium text-slate-700 shadow-sm border border-slate-200">
              Retake
            </button>
          )}
        </div>
      ) : (
        <button type="button" onClick={() => !disabled && inputRef.current?.click()} disabled={disabled}
          className="w-full flex items-center justify-center gap-2 py-8 border-2 border-dashed border-slate-300 rounded-xl text-slate-500 hover:bg-slate-50 transition disabled:opacity-50">
          <HiOutlineCamera className="w-6 h-6" />
          <span className="text-sm font-medium">Take Photo</span>
        </button>
      )}
    </div>
  )
}

const FIELD_COMPONENTS = {
  text: TextField, number: NumberField, date: DateField, datetime: DateField,
  radio: RadioField, dropdown: DropdownField, checkbox: CheckboxField,
  textarea: TextareaField, file: PhotoField,
}

// ═══════════════════════════════════════════════════════════════
// GAP 1: Skip Logic — evaluate display conditions
// ═══════════════════════════════════════════════════════════════

function evaluateDisplayCondition(condition, values, items) {
  if (!condition) return true

  // Find the controlling field's current value
  const controlField = items.find((i) => i.field_name === condition.field)
  if (!controlField) return true

  const controlValue = values[controlField.id] || ''
  const targetValue = String(condition.value || '')

  switch (condition.operator) {
    case 'eq':
      return String(controlValue) === targetValue
    case 'neq':
      return String(controlValue) !== targetValue
    case 'in':
      return (condition.values || []).map(String).includes(String(controlValue))
    case 'gt':
      return parseFloat(controlValue) > parseFloat(targetValue)
    case 'lt':
      return parseFloat(controlValue) < parseFloat(targetValue)
    case 'gte':
      return parseFloat(controlValue) >= parseFloat(targetValue)
    case 'lte':
      return parseFloat(controlValue) <= parseFloat(targetValue)
    case 'not_empty':
      return controlValue !== '' && controlValue !== null && controlValue !== undefined
    default:
      return true
  }
}

// ═══════════════════════════════════════════════════════════════
// GAP 5: Cross-Field Validation
// ═══════════════════════════════════════════════════════════════

function validateCrossField(item, value, values, items) {
  if (!item.cross_field_validation || !value) return null

  const rule = item.cross_field_validation
  const refField = items.find((i) => i.field_name === rule.gte || i.field_name === rule.lte || i.field_name === rule.eq)
  if (!refField) return null

  const refValue = values[refField.id] || ''
  if (!refValue) return null

  if (rule.gte && value < refValue) {
    return rule.message || `Must be on or after ${refField.field_label}`
  }
  if (rule.lte && value > refValue) {
    return rule.message || `Must be on or before ${refField.field_label}`
  }
  if (rule.eq && value !== refValue) {
    return rule.message || `Must equal ${refField.field_label}`
  }

  return null
}

// ═══════════════════════════════════════════════════════════════
// Per-Field Validation (range checks)
// ═══════════════════════════════════════════════════════════════

function validateItem(item, value) {
  if (item.required && (!value || !String(value).trim())) {
    return 'This field is required'
  }

  if (value && item.validation_rule) {
    const rangeMatch = item.validation_rule.match(/range\((\S+),\s*(\S+)\)/)
    if (rangeMatch) {
      const min = parseFloat(rangeMatch[1])
      const max = parseFloat(rangeMatch[2])
      const num = parseFloat(value)
      if (isNaN(num) || num < min || num > max) {
        return `Must be between ${min} and ${max}`
      }
    }
  }

  return null
}

// ═══════════════════════════════════════════════════════════════
// GAP 3: E-Signature Modal
// ═══════════════════════════════════════════════════════════════

function ESignatureModal({ isOpen, onConfirm, onCancel, isVerifying }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!password.trim()) {
      setError('Password is required')
      return
    }
    setError('')
    onConfirm(password)
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <HiOutlineShieldCheck className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-800">E-Signature</h3>
            <p className="text-xs text-slate-500">21 CFR Part 11 Compliance</p>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-4">
          By entering your password, you are electronically signing this CRF and certifying
          that the data entered is accurate and complete.
        </p>

        <form onSubmit={handleSubmit}>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError('') }}
            autoFocus
            className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm mb-2
                        focus:outline-none focus:ring-2 focus:ring-primary-400
                        ${error ? 'border-rose-400' : 'border-slate-200'}`}
          />
          {error && <p className="text-xs text-rose-500 mb-3">{error}</p>}

          <div className="flex gap-3 mt-4">
            <button type="button" onClick={onCancel}
              className="flex-1 py-2.5 border border-slate-300 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50">
              Cancel
            </button>
            <button type="submit" disabled={isVerifying}
              className="flex-[2] py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 disabled:opacity-60 flex items-center justify-center gap-2">
              {isVerifying ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <HiOutlineLockClosed className="w-4 h-4" />
                  Sign & Submit
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// GAP 2 helper: Reason for Change Modal
// ═══════════════════════════════════════════════════════════════

function ReasonForChangeModal({ isOpen, onConfirm, onCancel }) {
  const [reason, setReason] = useState('')

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
            <HiOutlinePencilAlt className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-800">Reason for Change</h3>
            <p className="text-xs text-slate-500">Required for audit compliance</p>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-3">
          You are editing a previously submitted CRF. Please provide a reason for the change.
        </p>

        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="e.g. Data entry error, updated lab results..."
          rows={3}
          autoFocus
          className="w-full px-3.5 py-3 bg-white border border-slate-200 rounded-xl text-sm resize-none
                     focus:outline-none focus:ring-2 focus:ring-primary-400 mb-4"
        />

        <div className="flex gap-3">
          <button type="button" onClick={onCancel}
            className="flex-1 py-2.5 border border-slate-300 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50">
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onConfirm(reason)}
            disabled={!reason.trim()}
            className="flex-[2] py-2.5 bg-amber-600 text-white rounded-xl text-sm font-medium hover:bg-amber-700 disabled:opacity-50">
            Continue
          </button>
        </div>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// Main Component
// ═══════════════════════════════════════════════════════════════

export default function EdcCrfForm() {
  const { subjectId, visitId, formId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { submitCrf, isOnline } = useEdcStore()

  const [values, setValues] = useState({})
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const [existingInstanceId, setExistingInstanceId] = useState(null)
  const [existingStatus, setExistingStatus] = useState(null)

  // E-signature modal state
  const [showSignatureModal, setShowSignatureModal] = useState(false)
  const [isVerifyingSig, setIsVerifyingSig] = useState(false)

  // Reason for change modal state
  const [showReasonModal, setShowReasonModal] = useState(false)
  const [reasonForChange, setReasonForChange] = useState('')

  // Fetch form schema
  const { data: formSchema, isLoading } = useQuery({
    queryKey: ['edc-form-schema', formId],
    queryFn: async () => {
      const res = await apiClient.get(`${API.EDC_FORMS}${formId}/schema/`)
      return res.data
    },
  })

  // Cache form schema for offline
  const { cacheFormSchema } = useEdcStore()
  useEffect(() => {
    if (formSchema) cacheFormSchema(formId, formSchema)
  }, [formSchema, formId, cacheFormSchema])

  // GAP 2: Load existing form instance for edit mode
  useEffect(() => {
    if (!formSchema || !subjectId || !visitId) return

    const loadExisting = async () => {
      try {
        const res = await apiClient.get(
          `edc/subjects/${subjectId}/visits/${visitId}/forms/`
        )
        const visitData = res.data
        const matchingForm = visitData.forms?.find(f => String(f.id) === String(formId))

        if (matchingForm?.instance_id) {
          // Load existing responses
          const instRes = await apiClient.get(`edc/form-instances/${matchingForm.instance_id}/`)
          const instance = instRes.data

          setIsEditMode(true)
          setExistingInstanceId(instance.id)
          setExistingStatus(instance.status)

          // Pre-fill values
          const prefilled = {}
          for (const resp of instance.responses) {
            prefilled[resp.item_id] = resp.value
          }
          setValues(prefilled)
        }
      } catch {
        // No existing instance — new form
      }
    }

    if (isOnline) loadExisting()
  }, [formSchema, subjectId, visitId, formId, isOnline])

  const items = formSchema?.items || []

  const handleChange = (itemId, value) => {
    setValues((prev) => ({ ...prev, [itemId]: value }))
    setErrors((prev) => ({ ...prev, [itemId]: undefined }))
  }

  // ── Submit flow ──

  const startSubmit = (saveAsDraft = false) => {
    if (saveAsDraft) {
      doSubmit(false, '', '')
      return
    }

    // Validate all visible items
    const newErrors = {}
    items.forEach((item) => {
      const isVisible = evaluateDisplayCondition(item.display_condition, values, items)
      if (!isVisible) return

      const err = validateItem(item, values[item.id] || '')
      if (err) newErrors[item.id] = err

      // GAP 5: Cross-field validation
      const crossErr = validateCrossField(item, values[item.id] || '', values, items)
      if (crossErr) newErrors[item.id] = crossErr
    })

    if (Object.keys(newErrors).length) {
      setErrors(newErrors)
      toast.error(`${Object.keys(newErrors).length} field(s) need attention`)
      // Scroll to first error
      const firstErrorId = Object.keys(newErrors)[0]
      document.getElementById(`field-${firstErrorId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      return
    }

    // If editing a submitted CRF → ask for reason
    if (isEditMode && existingStatus === 'submitted') {
      setShowReasonModal(true)
      return
    }

    // Show e-signature modal
    setShowSignatureModal(true)
  }

  const handleReasonConfirm = (reason) => {
    setReasonForChange(reason)
    setShowReasonModal(false)
    // Now show e-signature
    setShowSignatureModal(true)
  }

  const handleSignatureConfirm = async (password) => {
    setIsVerifyingSig(true)

    // ── 21 CFR Part 11: Re-authenticate via Keycloak ROPC grant ──
    try {
      // Extract username from existing JWT token
      const existingToken = localStorage.getItem('hact_access_token')
      let username = ''
      if (existingToken) {
        try {
          const payload = JSON.parse(atob(existingToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
          username = payload.preferred_username || payload.sub || ''
        } catch { /* fallback below */ }
      }

      console.log('[EDC E-Sig] Username from token:', username)

      if (!username) {
        toast.error('Could not determine username — please re-login')
        setIsVerifyingSig(false)
        return
      }

      const tokenUrl = '/auth/realms/hact/protocol/openid-connect/token'
      const params = new URLSearchParams({
        grant_type: 'password',
        client_id: 'hact-ctms-frontend',
        username,
        password: password,
      })

      console.log('[EDC E-Sig] Calling Keycloak:', tokenUrl)

      const kcResponse = await fetch(tokenUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString(),
      })

      console.log('[EDC E-Sig] Keycloak response status:', kcResponse.status)

      if (!kcResponse.ok) {
        const errorBody = await kcResponse.json().catch(() => ({}))
        console.error('[EDC E-Sig] Keycloak error:', errorBody)
        toast.error(`E-signature failed: ${errorBody.error_description || errorBody.error || 'incorrect password'}`)
        setIsVerifyingSig(false)
        return
      }

      // Keycloak verified the password — extract the fresh token as proof
      const tokenData = await kcResponse.json()
      const signatureToken = tokenData.access_token

      console.log('[EDC E-Sig] Success — got fresh token')

      setIsVerifyingSig(false)
      setShowSignatureModal(false)
      doSubmit(true, signatureToken, reasonForChange)
    } catch (err) {
      console.error('[EDC E-Sig] Exception:', err)
      toast.error('Could not verify signature — check connection')
      setIsVerifyingSig(false)
    }
  }

  const doSubmit = async (isSubmit, signatureToken, reason) => {
    setIsSubmitting(true)

    const payload = {
      form_id: parseInt(formId),
      subject_id: parseInt(subjectId),
      subject_visit_id: visitId ? parseInt(visitId) : null,
      status: isSubmit ? 'submitted' : 'draft',
      reason_for_change: reason,
      e_signature_token: signatureToken,
      responses: items
        .filter((item) => evaluateDisplayCondition(item.display_condition, values, items))
        .map((item) => ({
          item_id: item.id,
          value: values[item.id] || '',
        }))
        .filter((r) => r.value !== ''),
    }

    const result = await submitCrf(payload)

    setIsSubmitting(false)

    if (result.success) {
      setSubmitted(true)
      // Invalidate cached subject/visit data so visit status refreshes
      queryClient.invalidateQueries({ queryKey: ['edc-subject', subjectId] })
      queryClient.invalidateQueries({ queryKey: ['edc-visit-forms'] })
      queryClient.invalidateQueries({ queryKey: ['edc-subjects'] })
      if (result.offline) {
        toast.success('Saved offline — will sync when online', { icon: '📱' })
      } else {
        toast.success(isEditMode ? 'CRF updated successfully!' : 'CRF submitted successfully!')
      }
    } else {
      if (result.queued) {
        // Show the actual error — don't silently swallow it
        console.error('[EDC Submit] Queued due to error:', result.error)
        toast.error(`Submit failed: ${result.error || 'Unknown error'} — queued for retry`, {
          duration: 6000,
        })
        setSubmitted(true)
      } else {
        toast.error(result.error || 'Submission failed')
      }
    }
  }

  // ── Loading state ──
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  // ── Success state ──
  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center h-full px-6 text-center">
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
          <HiOutlineCheck className="w-8 h-8 text-emerald-600" />
        </div>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">
          {isEditMode ? 'CRF Updated' : 'CRF Submitted'}
        </h2>
        <p className="text-sm text-slate-500 mb-6">
          {formSchema?.name} has been {isOnline ? (isEditMode ? 'updated' : 'submitted') : 'queued for sync'}.
        </p>
        <button
          onClick={() => navigate(`/edc/subject/${subjectId}`)}
          className="px-6 py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition"
        >
          Back to Visits
        </button>
      </div>
    )
  }

  // ── Locked state ──
  const isLocked = existingStatus === 'locked' || existingStatus === 'signed'

  // Count visible + filled
  const visibleItems = items.filter(item => evaluateDisplayCondition(item.display_condition, values, items))
  const filledCount = visibleItems.filter(item => values[item.id]).length

  // Track sections for grouping
  let currentSection = ''

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="px-4 py-3 bg-white border-b border-slate-200 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-1 -ml-1">
            <HiOutlineArrowLeft className="w-5 h-5 text-slate-600" />
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="text-base font-semibold text-slate-800 truncate">
              {formSchema?.name}
            </h1>
            <p className="text-xs text-slate-500">
              v{formSchema?.version} · {visibleItems.length} fields
              {isEditMode && <span className="text-amber-500 ml-1">· Editing</span>}
              {isLocked && <span className="text-slate-400 ml-1">· Locked</span>}
              {!isOnline && <span className="text-amber-500 ml-1">· Offline</span>}
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-2.5 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 rounded-full transition-all duration-300"
            style={{ width: `${visibleItems.length ? (filledCount / visibleItems.length) * 100 : 0}%` }}
          />
        </div>
        <p className="text-[10px] text-slate-400 mt-1">
          {filledCount} of {visibleItems.length} fields completed
        </p>
      </div>

      {/* ── Form Fields ── */}
      <form className="flex-1 overflow-y-auto px-4 py-4 space-y-4 pb-32"
        onSubmit={(e) => { e.preventDefault(); startSubmit(false) }}>
        {items.map((item, idx) => {
          // GAP 1: Skip logic
          const isVisible = evaluateDisplayCondition(item.display_condition, values, items)
          if (!isVisible) return null

          const FieldComponent = FIELD_COMPONENTS[item.field_type] || TextField
          const error = errors[item.id]

          // Section grouping
          let sectionHeader = null
          if (item.section && item.section !== currentSection) {
            currentSection = item.section
            sectionHeader = (
              <div className="pt-3 pb-1 border-b border-slate-200 mb-1">
                <h3 className="text-xs font-bold text-primary-700 uppercase tracking-wider">
                  {item.section}
                </h3>
              </div>
            )
          }

          return (
            <div key={item.id} id={`field-${item.id}`}>
              {sectionHeader}

              {/* Label */}
              <label className="block text-xs font-medium text-slate-600 mb-1.5">
                <span className="text-slate-400 mr-1.5">{idx + 1}.</span>
                {item.field_label}
                {item.required && <span className="text-rose-500 ml-0.5">*</span>}
              </label>

              {/* Field */}
              <FieldComponent
                item={item}
                value={values[item.id] || ''}
                onChange={(val) => handleChange(item.id, val)}
                error={error}
                disabled={isLocked}
              />

              {/* Error */}
              {error && (
                <p className="flex items-center gap-1 text-xs text-rose-500 mt-1">
                  <HiOutlineExclamation className="w-3.5 h-3.5" />
                  {error}
                </p>
              )}

              {/* Validation hint */}
              {item.validation_rule && !error && (
                <p className="text-[10px] text-slate-400 mt-0.5">{item.validation_rule}</p>
              )}
            </div>
          )
        })}
      </form>

      {/* ── Fixed Bottom Buttons (hidden when locked) ── */}
      {!isLocked && (
        <div className="fixed bottom-10 left-0 right-0 px-4 pb-4 pt-2 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent">
          <div className="flex gap-3">
            <button type="button" onClick={() => startSubmit(true)} disabled={isSubmitting}
              className="flex-1 flex items-center justify-center gap-2 py-3 bg-white text-slate-700 border border-slate-300 rounded-xl text-sm font-medium shadow-sm hover:bg-slate-50 active:scale-[0.98] transition-all disabled:opacity-60">
              <HiOutlineSave className="w-4 h-4" />
              <span>Draft</span>
            </button>

            <button type="button" onClick={() => startSubmit(false)} disabled={isSubmitting}
              className="flex-[2] flex items-center justify-center gap-2 py-3 bg-primary-600 text-white rounded-xl text-sm font-medium shadow-sm hover:bg-primary-700 active:scale-[0.98] transition-all disabled:opacity-60">
              {isSubmitting ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <HiOutlineCloudUpload className="w-5 h-5" />
                  <span>{isEditMode ? 'Update CRF' : 'Submit CRF'}</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ── E-Signature Modal (GAP 3) ── */}
      <ESignatureModal
        isOpen={showSignatureModal}
        onConfirm={handleSignatureConfirm}
        onCancel={() => setShowSignatureModal(false)}
        isVerifying={isVerifyingSig}
      />

      {/* ── Reason for Change Modal (GAP 4 audit compliance) ── */}
      <ReasonForChangeModal
        isOpen={showReasonModal}
        onConfirm={handleReasonConfirm}
        onCancel={() => setShowReasonModal(false)}
      />
    </div>
  )
}
