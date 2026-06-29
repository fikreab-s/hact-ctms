/**
 * MonitoringPage — Risk-Based Monitoring Dashboard + SAE Expedited Reporting
 *
 * ICH E6(R3) compliant centralized monitoring dashboard showing:
 * 1. Study risk overview (summary cards)
 * 2. Per-site risk heatmap with KPI indicators
 * 3. SAE expedited reporting timeline with countdown timers
 */

import { useState } from 'react'
import {
  FiShield, FiAlertTriangle, FiClock, FiCheckCircle,
  FiTrendingUp, FiMapPin, FiActivity, FiChevronDown, FiChevronUp,
} from 'react-icons/fi'
import {
  useSiteRiskScores, useStudyOverview, useSaeTimeline,
  useMarkSaeReported, useStudies,
} from '../api/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

// ── Risk level colors & labels ──
const RISK_CONFIG = {
  low: { color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200', dot: 'bg-emerald-500', label: 'Low Risk' },
  medium: { color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200', dot: 'bg-amber-500', label: 'Medium Risk' },
  high: { color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200', dot: 'bg-rose-500', label: 'High Risk' },
}

const INDICATOR_LABELS = {
  enrollment_rate: { label: 'Enrollment Rate', icon: FiTrendingUp },
  query_rate: { label: 'Query Rate', icon: FiActivity },
  ae_reporting_rate: { label: 'AE Reporting', icon: FiAlertTriangle },
  crf_completion: { label: 'CRF Completion', icon: FiCheckCircle },
  overdue_saes: { label: 'Overdue SAEs', icon: FiClock },
}

export default function MonitoringPage() {
  const [selectedStudy, setSelectedStudy] = useState(null)
  const [expandedSite, setExpandedSite] = useState(null)
  const [saeTab, setSaeTab] = useState('all') // all | pending | overdue

  const { data: studiesData } = useStudies()
  const studies = studiesData?.results || []

  const { data: overview, isLoading: loadingOverview } = useStudyOverview(selectedStudy)
  const { data: riskData, isLoading: loadingRisk } = useSiteRiskScores(selectedStudy)
  const { data: saeData, isLoading: loadingSae } = useSaeTimeline(
    saeTab !== 'all' ? { status: saeTab } : {}
  )
  const markReported = useMarkSaeReported()

  const sites = riskData?.results || []
  const saes = saeData?.results || []
  const saeSummary = saeData?.summary || {}

  if (loadingOverview && loadingRisk) {
    return <LoadingSpinner text="Loading monitoring dashboard..." />
  }

  const handleMarkReported = async (saeId) => {
    try {
      await markReported.mutateAsync(saeId)
      toast.success('SAE marked as reported to authority')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to mark SAE as reported')
    }
  }

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <FiShield className="w-6 h-6 text-indigo-600" />
            Risk-Based Monitoring
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            ICH E6(R3) centralized monitoring dashboard
          </p>
        </div>

        {/* Study Selector */}
        {studies.length > 0 && (
          <select
            value={selectedStudy || ''}
            onChange={(e) => setSelectedStudy(e.target.value || null)}
            className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30 min-w-[220px]"
            id="study-selector"
          >
            <option value="">All Studies (default)</option>
            {studies.map(s => (
              <option key={s.id} value={s.id}>
                {s.protocol_number} — {s.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* ── Section 1: Study Risk Overview Cards ── */}
      {overview && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <OverviewCard
            label="Total Sites"
            value={overview.total_sites}
            icon={FiMapPin}
            variant="slate"
          />
          <OverviewCard
            label="High Risk"
            value={overview.high_risk_sites}
            icon={FiAlertTriangle}
            variant={overview.high_risk_sites > 0 ? 'rose' : 'slate'}
          />
          <OverviewCard
            label="Medium Risk"
            value={overview.medium_risk_sites}
            icon={FiActivity}
            variant={overview.medium_risk_sites > 0 ? 'amber' : 'slate'}
          />
          <OverviewCard
            label="Low Risk"
            value={overview.low_risk_sites}
            icon={FiCheckCircle}
            variant="emerald"
          />
          <OverviewCard
            label="Overdue SAEs"
            value={overview.overdue_saes}
            icon={FiClock}
            variant={overview.overdue_saes > 0 ? 'rose' : 'emerald'}
          />
          <OverviewCard
            label="Open Queries"
            value={overview.open_queries}
            icon={FiActivity}
            variant={overview.open_queries > 5 ? 'amber' : 'slate'}
          />
        </div>
      )}

      {/* ── Overall Risk Level Banner ── */}
      {overview && (
        <div className={`rounded-xl border p-4 flex items-center gap-4 ${RISK_CONFIG[overview.overall_risk_level]?.bg || 'bg-slate-50'} ${RISK_CONFIG[overview.overall_risk_level]?.border || 'border-slate-200'}`}>
          <div className={`w-3 h-3 rounded-full ${RISK_CONFIG[overview.overall_risk_level]?.dot || 'bg-slate-400'} animate-pulse`} />
          <div>
            <span className={`text-sm font-semibold ${RISK_CONFIG[overview.overall_risk_level]?.color || 'text-slate-700'}`}>
              Overall Study Risk: {RISK_CONFIG[overview.overall_risk_level]?.label || 'Unknown'}
            </span>
            <span className="text-xs text-slate-500 ml-3">
              Enrollment: {overview.enrolled_subjects}/{overview.total_subjects} subjects
              ({overview.enrollment_vs_target?.percent || 0}% of target)
            </span>
          </div>
        </div>
      )}

      {/* ── Section 2: Site Risk Heatmap ── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="px-5 py-4 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <FiMapPin className="w-4 h-4 text-indigo-500" />
            Site Risk Heatmap
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Click a site row to expand KPI details</p>
        </div>

        {loadingRisk ? (
          <div className="p-8 text-center">
            <LoadingSpinner text="Computing risk scores..." />
          </div>
        ) : sites.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-400">
            No sites found for the selected study.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100 bg-slate-50/50">
                  <th className="px-5 py-3">Site</th>
                  <th className="px-5 py-3 text-center">Risk Level</th>
                  <th className="px-5 py-3 text-center">Score</th>
                  <th className="px-5 py-3 text-center">Enrollment</th>
                  <th className="px-5 py-3 text-center">Queries</th>
                  <th className="px-5 py-3 text-center">AE Rate</th>
                  <th className="px-5 py-3 text-center">CRF %</th>
                  <th className="px-5 py-3 text-center">SAEs</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {sites.map(site => {
                  const risk = RISK_CONFIG[site.risk_level] || RISK_CONFIG.medium
                  const isExpanded = expandedSite === site.site_id
                  const ind = site.indicators || {}

                  return (
                    <>
                      <tr
                        key={site.site_id}
                        onClick={() => setExpandedSite(isExpanded ? null : site.site_id)}
                        className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                      >
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2">
                            {isExpanded ? <FiChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <FiChevronDown className="w-3.5 h-3.5 text-slate-400" />}
                            <div>
                              <span className="font-medium text-slate-800">{site.site_code}</span>
                              <span className="text-xs text-slate-400 block">{site.site_name}</span>
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-3 text-center">
                          <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${risk.bg} ${risk.color} ${risk.border} border`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${risk.dot}`} />
                            {risk.label}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-center">
                          <ScoreBadge score={site.overall_score} />
                        </td>
                        <td className="px-5 py-3 text-center">
                          <KpiCell indicator={ind.enrollment_rate} />
                        </td>
                        <td className="px-5 py-3 text-center">
                          <KpiCell indicator={ind.query_rate} invert />
                        </td>
                        <td className="px-5 py-3 text-center">
                          <KpiCell indicator={ind.ae_reporting_rate} />
                        </td>
                        <td className="px-5 py-3 text-center">
                          <KpiCell indicator={ind.crf_completion} suffix="%" />
                        </td>
                        <td className="px-5 py-3 text-center">
                          <KpiCell indicator={ind.overdue_saes} invert />
                        </td>
                      </tr>

                      {/* Expanded KPI detail row */}
                      {isExpanded && (
                        <tr key={`${site.site_id}-detail`}>
                          <td colSpan="8" className="px-5 py-4 bg-slate-50/50">
                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                              {Object.entries(ind).map(([key, val]) => {
                                const meta = INDICATOR_LABELS[key] || { label: key, icon: FiActivity }
                                const Icon = meta.icon
                                const indRisk = RISK_CONFIG[val.risk] || RISK_CONFIG.medium

                                return (
                                  <div key={key} className={`rounded-lg border p-3 ${indRisk.bg} ${indRisk.border}`}>
                                    <div className="flex items-center gap-1.5 mb-1">
                                      <Icon className={`w-3.5 h-3.5 ${indRisk.color}`} />
                                      <span className="text-xs font-medium text-slate-600">{meta.label}</span>
                                    </div>
                                    <div className="text-lg font-bold text-slate-800">
                                      {val.value}{val.unit === '%' ? '%' : ''}
                                    </div>
                                    <div className="text-[10px] text-slate-500">
                                      {val.unit !== '%' ? `${val.unit} ` : ''}
                                      (target: {val.target || val.benchmark || val.threshold})
                                    </div>
                                    {/* Score bar */}
                                    <div className="mt-2 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                      <div
                                        className={`h-full rounded-full transition-all ${val.score >= 80 ? 'bg-emerald-500' : val.score >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                                        style={{ width: `${Math.min(val.score, 100)}%` }}
                                      />
                                    </div>
                                    <div className="text-[10px] text-slate-500 mt-0.5 text-right">
                                      Score: {val.score}/100
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Section 3: SAE Expedited Reporting Timeline ── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="px-5 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <FiClock className="w-4 h-4 text-rose-500" />
              SAE Expedited Reporting Timeline
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              ICH-GCP E6(R2): Fatal/life-threatening → 7 days · Other SAE → 15 days
            </p>
          </div>

          {/* Summary badges */}
          <div className="flex items-center gap-2">
            <SaeSummaryBadge
              label="Pending"
              count={saeSummary.pending || 0}
              variant="amber"
              active={saeTab === 'pending'}
              onClick={() => setSaeTab(saeTab === 'pending' ? 'all' : 'pending')}
            />
            <SaeSummaryBadge
              label="Overdue"
              count={saeSummary.overdue || 0}
              variant="rose"
              active={saeTab === 'overdue'}
              onClick={() => setSaeTab(saeTab === 'overdue' ? 'all' : 'overdue')}
            />
            <SaeSummaryBadge
              label="On Time"
              count={saeSummary.on_time || 0}
              variant="emerald"
              active={saeTab === 'on_time'}
              onClick={() => setSaeTab(saeTab === 'on_time' ? 'all' : 'on_time')}
            />
          </div>
        </div>

        {loadingSae ? (
          <div className="p-8 text-center">
            <LoadingSpinner text="Loading SAE timeline..." />
          </div>
        ) : saes.length === 0 ? (
          <div className="p-8 text-center">
            <FiCheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-sm text-slate-500">
              {saeTab !== 'all'
                ? `No ${saeTab} SAEs found.`
                : 'No SAEs with reporting deadlines. All clear!'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100 bg-slate-50/50">
                  <th className="px-5 py-3">SAE</th>
                  <th className="px-5 py-3">Subject</th>
                  <th className="px-5 py-3">Criteria</th>
                  <th className="px-5 py-3 text-center">Deadline</th>
                  <th className="px-5 py-3 text-center">Time Remaining</th>
                  <th className="px-5 py-3 text-center">Status</th>
                  <th className="px-5 py-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {saes.map(sae => (
                  <tr key={sae.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-5 py-3">
                      <div className="font-medium text-slate-800">AE-{sae.id}</div>
                      <div className="text-xs text-slate-500 truncate max-w-[200px]">{sae.ae_term}</div>
                    </td>
                    <td className="px-5 py-3">
                      <div className="text-slate-700">{sae.subject_identifier}</div>
                      <div className="text-xs text-slate-400">{sae.site_code}</div>
                    </td>
                    <td className="px-5 py-3">
                      <span className="text-xs text-slate-600 capitalize">
                        {(sae.serious_criteria || '').replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-center">
                      <div className="text-xs text-slate-600">
                        {sae.reporting_deadline
                          ? new Date(sae.reporting_deadline).toLocaleDateString()
                          : '—'}
                      </div>
                    </td>
                    <td className="px-5 py-3 text-center">
                      <CountdownBadge
                        daysRemaining={sae.deadline_days_remaining}
                        percentElapsed={sae.deadline_percent_elapsed}
                      />
                    </td>
                    <td className="px-5 py-3 text-center">
                      <ReportingStatusBadge status={sae.reporting_status} />
                    </td>
                    <td className="px-5 py-3 text-center">
                      {sae.reporting_status === 'pending' || sae.reporting_status === 'overdue' ? (
                        <button
                          onClick={() => handleMarkReported(sae.id)}
                          disabled={markReported.isPending}
                          className="text-xs font-medium px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50"
                          id={`mark-reported-${sae.id}`}
                        >
                          Mark Reported
                        </button>
                      ) : (
                        <span className="text-xs text-slate-400">
                          {sae.reported_to_authority_at
                            ? new Date(sae.reported_to_authority_at).toLocaleDateString()
                            : '—'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}


// ── Sub-components ──

function OverviewCard({ label, value, icon: Icon, variant = 'slate' }) {
  const variants = {
    slate: 'bg-white border-slate-200 text-slate-700',
    rose: 'bg-rose-50 border-rose-200 text-rose-700',
    amber: 'bg-amber-50 border-amber-200 text-amber-700',
    emerald: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
  }

  return (
    <div className={`rounded-xl border p-4 shadow-sm ${variants[variant] || variants.slate}`}>
      <div className="flex items-center gap-2 mb-1">
        <Icon className="w-4 h-4 opacity-60" />
        <span className="text-xs font-medium opacity-80">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value ?? '—'}</div>
    </div>
  )
}

function ScoreBadge({ score }) {
  const color = score >= 80 ? 'text-emerald-700 bg-emerald-50' :
    score >= 50 ? 'text-amber-700 bg-amber-50' : 'text-rose-700 bg-rose-50'

  return (
    <span className={`inline-block text-xs font-bold px-2.5 py-1 rounded-full ${color}`}>
      {score}
    </span>
  )
}

function KpiCell({ indicator, invert = false, suffix = '' }) {
  if (!indicator) return <span className="text-xs text-slate-300">—</span>

  const risk = RISK_CONFIG[indicator.risk] || RISK_CONFIG.medium

  return (
    <span className={`text-xs font-medium ${risk.color}`}>
      {indicator.value}{suffix}
    </span>
  )
}

function CountdownBadge({ daysRemaining, percentElapsed }) {
  if (daysRemaining === null || daysRemaining === undefined) {
    return <span className="text-xs text-slate-400">—</span>
  }

  let color, label
  if (daysRemaining < 0) {
    color = 'text-rose-700 bg-rose-50 border-rose-200'
    label = `${Math.abs(daysRemaining).toFixed(1)}d overdue`
  } else if (percentElapsed >= 90) {
    color = 'text-rose-700 bg-rose-50 border-rose-200'
    label = `${daysRemaining.toFixed(1)}d left`
  } else if (percentElapsed >= 50) {
    color = 'text-amber-700 bg-amber-50 border-amber-200'
    label = `${daysRemaining.toFixed(1)}d left`
  } else {
    color = 'text-emerald-700 bg-emerald-50 border-emerald-200'
    label = `${daysRemaining.toFixed(1)}d left`
  }

  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border ${color}`}>
        <FiClock className="w-3 h-3" />
        {label}
      </span>
      {/* Mini progress bar */}
      <div className="w-16 h-1 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${percentElapsed >= 90 ? 'bg-rose-500' : percentElapsed >= 50 ? 'bg-amber-500' : 'bg-emerald-500'}`}
          style={{ width: `${Math.min(percentElapsed || 0, 100)}%` }}
        />
      </div>
    </div>
  )
}

function ReportingStatusBadge({ status }) {
  const config = {
    pending: { color: 'text-amber-700 bg-amber-50', label: 'Pending' },
    overdue: { color: 'text-rose-700 bg-rose-50', label: 'Overdue' },
    on_time: { color: 'text-emerald-700 bg-emerald-50', label: 'On Time' },
    not_applicable: { color: 'text-slate-500 bg-slate-50', label: 'N/A' },
  }

  const c = config[status] || config.not_applicable

  return (
    <span className={`inline-flex text-xs font-semibold px-2 py-0.5 rounded-full ${c.color}`}>
      {c.label}
    </span>
  )
}

function SaeSummaryBadge({ label, count, variant, active, onClick }) {
  const variants = {
    amber: active ? 'bg-amber-600 text-white border-amber-600' : 'bg-amber-50 text-amber-700 border-amber-200',
    rose: active ? 'bg-rose-600 text-white border-rose-600' : 'bg-rose-50 text-rose-700 border-rose-200',
    emerald: active ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-emerald-50 text-emerald-700 border-emerald-200',
  }

  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border transition-colors cursor-pointer ${variants[variant] || ''}`}
    >
      {label}: {count}
    </button>
  )
}
