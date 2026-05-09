import { NavLink, useLocation } from 'react-router-dom'
import {
  FiHome, FiFolder, FiUsers, FiMessageSquare,
  FiAlertTriangle, FiActivity, FiFileText,
  FiShield, FiServer, FiChevronDown,
} from 'react-icons/fi'
import useAuthStore from '../store/authStore'
import { getSidebarRoutes } from '../auth/roleConfig'

// Full nav definition — entries will be filtered per role
const ALL_NAV_ITEMS = [
  { to: '/', icon: FiHome, label: 'Dashboard', section: 'Overview' },
  { to: '/studies', icon: FiFolder, label: 'Studies', section: 'Clinical' },
  { to: '/subjects', icon: FiUsers, label: 'Subjects', section: 'Clinical' },
  { to: '/queries', icon: FiMessageSquare, label: 'Queries', section: 'Clinical' },
  { to: '/safety', icon: FiAlertTriangle, label: 'Safety', section: 'Safety & Lab' },
  { to: '/lab', icon: FiActivity, label: 'Laboratory', section: 'Safety & Lab' },
  { to: '/audit', icon: FiFileText, label: 'Audit Trail', section: 'Admin' },
  { to: '/integrations', icon: FiServer, label: 'Integrations', section: 'Admin',
    children: [
      { to: '/integrations/openclinica', label: '📋 OpenClinica' },
      { to: '/integrations/senaite', label: '🔬 SENAITE LIMS' },
      { to: '/integrations/nextcloud', label: '📁 Nextcloud eTMF' },
      { to: '/integrations/erpnext', label: '📊 ERPNext' },
    ],
  },
]

export default function Sidebar() {
  const { user, roles } = useAuthStore()
  const isSuperuser = user?.is_superuser || false
  const location = useLocation()

  // Get routes this user can access
  const allowedRoutes = getSidebarRoutes(roles, isSuperuser)

  // Filter nav items to only show allowed routes
  const visibleItems = ALL_NAV_ITEMS.filter(item => allowedRoutes.includes(item.to))

  // Group by section
  const sections = []
  const sectionMap = {}
  for (const item of visibleItems) {
    if (!sectionMap[item.section]) {
      sectionMap[item.section] = []
      sections.push(item.section)
    }
    sectionMap[item.section].push(item)
  }

  // Role display label
  const primaryRole = roles[0] || 'user'
  const roleLabel = primaryRole.replace(/_/g, ' ')

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-sidebar flex flex-col z-40">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
          <FiShield className="w-4 h-4 text-white" />
        </div>
        <div>
          <span className="text-white font-semibold text-sm tracking-tight">HACT CTMS</span>
          <span className="block text-[10px] text-sidebar-text leading-tight">Clinical Trials</span>
        </div>
      </div>

      {/* Navigation — dynamically filtered by role */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {sections.map((sectionTitle) => (
          <div key={sectionTitle}>
            <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-sidebar-text/60">
              {sectionTitle}
            </p>
            <ul className="space-y-0.5">
              {sectionMap[sectionTitle].map((item) => {
                const isParentActive = location.pathname === item.to || location.pathname.startsWith(item.to + '/')
                const showChildren = item.children && isParentActive

                return (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      end={!!item.children || item.to === '/'}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                          isActive || (item.children && isParentActive)
                            ? 'bg-sidebar-active text-sidebar-text-active font-medium shadow-lg shadow-primary-600/20'
                            : 'text-sidebar-text hover:bg-sidebar-hover hover:text-white'
                        }`
                      }
                    >
                      <item.icon className="w-[18px] h-[18px] shrink-0" />
                      <span className="flex-1">{item.label}</span>
                      {item.children && (
                        <FiChevronDown className={`w-3.5 h-3.5 transition-transform ${showChildren ? 'rotate-180' : ''}`} />
                      )}
                    </NavLink>
                    {showChildren && (
                      <ul className="ml-6 mt-1 space-y-0.5 border-l border-white/10 pl-3">
                        {item.children.map((child) => (
                          <li key={child.to}>
                            <NavLink
                              to={child.to}
                              className={({ isActive }) =>
                                `block px-3 py-1.5 rounded-md text-xs transition-all duration-150 ${
                                  isActive
                                    ? 'text-white bg-white/10 font-medium'
                                    : 'text-sidebar-text/70 hover:text-white hover:bg-white/5'
                                }`
                              }
                            >
                              {child.label}
                            </NavLink>
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Bottom: role badge + version */}
      <div className="p-4 border-t border-white/10 space-y-2">
        <div className="flex items-center gap-2 px-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] text-sidebar-text capitalize">{roleLabel}</span>
        </div>
        <p className="text-[11px] text-sidebar-text/50 text-center">v0.1.0 — Day 5 Build</p>
      </div>
    </aside>
  )
}
