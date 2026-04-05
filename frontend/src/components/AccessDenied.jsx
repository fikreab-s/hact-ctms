import { Link } from 'react-router-dom'
import { FiShieldOff } from 'react-icons/fi'

export default function AccessDenied({ requiredRole }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 rounded-full bg-rose-100 flex items-center justify-center mb-5">
        <FiShieldOff className="w-8 h-8 text-rose-500" />
      </div>
      <h2 className="text-xl font-bold text-slate-800 mb-2">Access Denied</h2>
      <p className="text-sm text-slate-500 max-w-md mb-6">
        You don't have permission to access this page.
        {requiredRole && (
          <span className="block mt-1">
            Required role: <span className="font-medium text-slate-700">{requiredRole}</span>
          </span>
        )}
      </p>
      <Link
        to="/"
        className="px-5 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-colors"
      >
        Go to Dashboard
      </Link>
    </div>
  )
}
