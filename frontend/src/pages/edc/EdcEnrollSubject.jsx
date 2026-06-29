/**
 * EdcEnrollSubject — Mobile enrollment form for new subjects.
 *
 * Fields: Subject ID, Screening #, Consent Date, Enrollment Date, Site, Study.
 * On submit, creates subject + auto-generates visit schedule.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { HiOutlineArrowLeft, HiOutlineUserAdd, HiOutlineCheck } from 'react-icons/hi'
import toast from 'react-hot-toast'
import apiClient from '../../api/client'
import { API } from '../../api/endpoints'

export default function EdcEnrollSubject() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [form, setForm] = useState({
    subject_identifier: '',
    screening_number: '',
    consent_signed_date: new Date().toISOString().slice(0, 10),
    enrollment_date: new Date().toISOString().slice(0, 10),
    study_id: '',
    site_id: '',
  })

  const [errors, setErrors] = useState({})

  // Fetch studies and sites for dropdowns
  const { data: studies } = useQuery({
    queryKey: ['edc-studies'],
    queryFn: async () => {
      const res = await apiClient.get(API.STUDIES)
      return res.data.results || res.data
    },
  })

  const { data: sites } = useQuery({
    queryKey: ['edc-sites', form.study_id],
    queryFn: async () => {
      const res = await apiClient.get(API.SITES, {
        params: form.study_id ? { study: form.study_id } : {},
      })
      return res.data.results || res.data
    },
    enabled: !!form.study_id,
  })

  const enrollMutation = useMutation({
    mutationFn: (data) => apiClient.post(API.EDC_ENROLL, data),
    onSuccess: (res) => {
      toast.success('Subject enrolled successfully!')
      queryClient.invalidateQueries({ queryKey: ['edc-subjects'] })
      navigate(`/edc/subject/${res.data.id}`)
    },
    onError: (err) => {
      const data = err.response?.data
      if (typeof data === 'object') {
        setErrors(data)
      } else {
        toast.error(data?.detail || 'Enrollment failed.')
      }
    },
  })

  const handleChange = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value })
    setErrors({ ...errors, [field]: undefined })
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    // Basic validation
    const newErrors = {}
    if (!form.subject_identifier.trim()) newErrors.subject_identifier = 'Required'
    if (!form.consent_signed_date) newErrors.consent_signed_date = 'Required'
    if (!form.study_id) newErrors.study_id = 'Select a study'
    if (!form.site_id) newErrors.site_id = 'Select a site'

    if (Object.keys(newErrors).length) {
      setErrors(newErrors)
      return
    }

    enrollMutation.mutate({
      ...form,
      study_id: parseInt(form.study_id),
      site_id: parseInt(form.site_id),
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="flex items-center gap-3 px-4 py-3 bg-white border-b border-slate-200">
        <button onClick={() => navigate('/edc')} className="p-1 -ml-1">
          <HiOutlineArrowLeft className="w-5 h-5 text-slate-600" />
        </button>
        <div>
          <h1 className="text-base font-semibold text-slate-800">Enroll New Subject</h1>
          <p className="text-xs text-slate-500">Register a new participant</p>
        </div>
      </div>

      {/* ── Form ── */}
      <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-4 py-5 space-y-4">
        {/* Study */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Study <span className="text-rose-500">*</span>
          </label>
          <select
            value={form.study_id}
            onChange={handleChange('study_id')}
            className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                        focus:outline-none focus:ring-2 focus:ring-primary-400
                        ${errors.study_id ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
          >
            <option value="">Select study...</option>
            {studies?.map((s) => (
              <option key={s.id} value={s.id}>{s.protocol_number} — {s.name}</option>
            ))}
          </select>
          {errors.study_id && <p className="text-xs text-rose-500 mt-1">{errors.study_id}</p>}
        </div>

        {/* Site */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Site <span className="text-rose-500">*</span>
          </label>
          <select
            value={form.site_id}
            onChange={handleChange('site_id')}
            disabled={!form.study_id}
            className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                        focus:outline-none focus:ring-2 focus:ring-primary-400 disabled:bg-slate-50 disabled:text-slate-400
                        ${errors.site_id ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
          >
            <option value="">Select site...</option>
            {sites?.map((s) => (
              <option key={s.id} value={s.id}>{s.site_code} — {s.name}</option>
            ))}
          </select>
          {errors.site_id && <p className="text-xs text-rose-500 mt-1">{errors.site_id}</p>}
        </div>

        {/* Subject ID */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Subject Identifier <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            placeholder="e.g. ETH-ADM-001-0005"
            value={form.subject_identifier}
            onChange={handleChange('subject_identifier')}
            className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                        focus:outline-none focus:ring-2 focus:ring-primary-400
                        ${errors.subject_identifier ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
          />
          {errors.subject_identifier && (
            <p className="text-xs text-rose-500 mt-1">
              {Array.isArray(errors.subject_identifier) ? errors.subject_identifier[0] : errors.subject_identifier}
            </p>
          )}
        </div>

        {/* Screening Number */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Screening Number
          </label>
          <input
            type="text"
            placeholder="e.g. SCR-0005"
            value={form.screening_number}
            onChange={handleChange('screening_number')}
            className="w-full px-3.5 py-3 bg-white border border-slate-200 rounded-xl text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </div>

        {/* Consent Date */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Consent Signed Date <span className="text-rose-500">*</span>
          </label>
          <input
            type="date"
            value={form.consent_signed_date}
            onChange={handleChange('consent_signed_date')}
            className={`w-full px-3.5 py-3 bg-white border rounded-xl text-sm
                        focus:outline-none focus:ring-2 focus:ring-primary-400
                        ${errors.consent_signed_date ? 'border-rose-400 ring-1 ring-rose-400' : 'border-slate-200'}`}
          />
          {errors.consent_signed_date && <p className="text-xs text-rose-500 mt-1">{errors.consent_signed_date}</p>}
        </div>

        {/* Enrollment Date */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1.5">
            Enrollment Date
          </label>
          <input
            type="date"
            value={form.enrollment_date}
            onChange={handleChange('enrollment_date')}
            className="w-full px-3.5 py-3 bg-white border border-slate-200 rounded-xl text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-400"
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={enrollMutation.isPending}
          className="w-full flex items-center justify-center gap-2 py-3.5 bg-primary-600 text-white
                     rounded-xl font-medium text-sm shadow-sm hover:bg-primary-700 active:scale-[0.98]
                     transition-all disabled:opacity-60 disabled:cursor-not-allowed mt-6"
        >
          {enrollMutation.isPending ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <HiOutlineUserAdd className="w-5 h-5" />
              <span>Enroll Subject</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}
