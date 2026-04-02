const STATUS_STYLES = {
  // Study
  planning: 'bg-sky-100 text-sky-700',
  active: 'bg-emerald-100 text-emerald-700',
  locked: 'bg-amber-100 text-amber-700',
  archived: 'bg-slate-200 text-slate-600',
  // Subject
  screened: 'bg-sky-100 text-sky-700',
  enrolled: 'bg-emerald-100 text-emerald-700',
  completed: 'bg-indigo-100 text-indigo-700',
  discontinued: 'bg-rose-100 text-rose-700',
  screen_failed: 'bg-rose-100 text-rose-700',
  // Query
  open: 'bg-rose-100 text-rose-700',
  answered: 'bg-amber-100 text-amber-700',
  closed: 'bg-slate-200 text-slate-600',
  // Form instance
  draft: 'bg-slate-200 text-slate-600',
  submitted: 'bg-sky-100 text-sky-700',
  signed: 'bg-indigo-100 text-indigo-700',
  // Lab flag
  N: 'bg-emerald-100 text-emerald-700',
  H: 'bg-rose-100 text-rose-700',
  L: 'bg-amber-100 text-amber-700',
  // AE severity
  mild: 'bg-emerald-100 text-emerald-700',
  moderate: 'bg-amber-100 text-amber-700',
  severe: 'bg-rose-100 text-rose-700',
}

export default function StatusBadge({ status, className = '' }) {
  if (!status) return null

  const style = STATUS_STYLES[status] || 'bg-slate-100 text-slate-600'
  const label = String(status).replace(/_/g, ' ')

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${style} ${className}`}
    >
      {label}
    </span>
  )
}
