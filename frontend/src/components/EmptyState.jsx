import { FiInbox } from 'react-icons/fi'

export default function EmptyState({ title = 'No data found', message = 'There are no records to display.', icon: Icon = FiInbox }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mb-4">
        <Icon className="w-7 h-7 text-slate-400" />
      </div>
      <h3 className="text-sm font-medium text-slate-700">{title}</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{message}</p>
    </div>
  )
}
