export default function StatCard({ title, value, subtitle, icon: Icon, variant = 'primary' }) {
  const variants = {
    primary: 'bg-gradient-to-br from-primary-500 to-primary-700',
    success: 'bg-gradient-to-br from-emerald-500 to-emerald-700',
    warning: 'bg-gradient-to-br from-amber-500 to-amber-700',
    danger: 'bg-gradient-to-br from-rose-500 to-rose-700',
    info: 'bg-gradient-to-br from-sky-500 to-sky-700',
  }

  return (
    <div className={`${variants[variant]} rounded-xl p-5 text-white shadow-lg relative overflow-hidden`}>
      {/* Decorative circle */}
      <div className="absolute -right-4 -top-4 w-24 h-24 rounded-full bg-white/10" />
      <div className="absolute -right-2 -bottom-6 w-16 h-16 rounded-full bg-white/5" />

      <div className="relative">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-white/80">{title}</p>
          {Icon && <Icon className="w-5 h-5 text-white/60" />}
        </div>
        <p className="text-3xl font-bold tracking-tight">{value}</p>
        {subtitle && (
          <p className="text-xs text-white/70 mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  )
}
