import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../client'
import { API } from '../endpoints'

// ── Studies ──
export function useStudies(params = {}) {
  return useQuery({
    queryKey: ['studies', params],
    queryFn: () => apiClient.get(API.STUDIES, { params }).then(r => r.data),
  })
}

export function useStudy(id) {
  return useQuery({
    queryKey: ['studies', id],
    queryFn: () => apiClient.get(`${API.STUDIES}${id}/`).then(r => r.data),
    enabled: !!id,
  })
}

export function useCreateStudy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => apiClient.post(API.STUDIES, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['studies'] }),
  })
}

export function useUpdateStudy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...data }) => apiClient.patch(`${API.STUDIES}${id}/`, data).then(r => r.data),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['studies'] })
      qc.invalidateQueries({ queryKey: ['studies', vars.id] })
    },
  })
}

export function useTransitionStudy() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status, reason }) =>
      apiClient.post(`${API.STUDIES}${id}/transition/`, { status, reason }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['studies'] }),
  })
}

// ── Sites ──
export function useSites(params = {}) {
  return useQuery({
    queryKey: ['sites', params],
    queryFn: () => apiClient.get(API.SITES, { params }).then(r => r.data),
  })
}

export function useCreateSite() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => apiClient.post(API.SITES, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sites'] })
      qc.invalidateQueries({ queryKey: ['studies'] })
    },
  })
}

// ── Subjects ──
export function useSubjects(params = {}) {
  return useQuery({
    queryKey: ['subjects', params],
    queryFn: () => apiClient.get(API.SUBJECTS, { params }).then(r => r.data),
  })
}

export function useSubject(id) {
  return useQuery({
    queryKey: ['subjects', id],
    queryFn: () => apiClient.get(`${API.SUBJECTS}${id}/`).then(r => r.data),
    enabled: !!id,
  })
}

export function useCreateSubject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data) => apiClient.post(API.SUBJECTS, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['subjects'] }),
  })
}

export function useEnrollSubject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...data }) =>
      apiClient.post(`${API.SUBJECTS}${id}/enroll/`, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['subjects'] })
      qc.invalidateQueries({ queryKey: ['studies'] })
    },
  })
}

export function useWithdrawSubject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...data }) =>
      apiClient.post(`${API.SUBJECTS}${id}/withdraw/`, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['subjects'] }),
  })
}

// ── Queries ──
export function useQueries(params = {}) {
  return useQuery({
    queryKey: ['queries', params],
    queryFn: () => apiClient.get(API.QUERIES, { params }).then(r => r.data),
  })
}

export function useAnswerQuery() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, response_text }) =>
      apiClient.post(`${API.QUERIES}${id}/answer/`, { response_text }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['queries'] }),
  })
}

export function useCloseQuery() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }) =>
      apiClient.post(`${API.QUERIES}${id}/close/`, { reason }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['queries'] }),
  })
}

// ── Adverse Events ──
export function useAdverseEvents(params = {}) {
  return useQuery({
    queryKey: ['adverse-events', params],
    queryFn: () => apiClient.get(API.ADVERSE_EVENTS, { params }).then(r => r.data),
  })
}

// ── Lab Results ──
export function useLabResults(params = {}) {
  return useQuery({
    queryKey: ['lab-results', params],
    queryFn: () => apiClient.get(API.LAB_RESULTS, { params }).then(r => r.data),
  })
}

export function useImportLabCSV() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (formData) =>
      apiClient.post(`${API.LAB_RESULTS}import-csv/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['lab-results'] }),
  })
}

// ── Audit Logs ──
export function useAuditLogs(params = {}) {
  return useQuery({
    queryKey: ['audit-logs', params],
    queryFn: () => apiClient.get(API.AUDIT_LOGS, { params }).then(r => r.data),
  })
}

// ── Quality Reports ──
export function useQualityReports(params = {}) {
  return useQuery({
    queryKey: ['quality-reports', params],
    queryFn: () => apiClient.get(API.QUALITY_REPORTS, { params }).then(r => r.data),
  })
}
