import { NavLink } from 'react-router-dom'
import {
  FiHome, FiFolder, FiUsers, FiMessageSquare,
  FiAlertTriangle, FiActivity, FiFileText,
  FiShield, FiSettings,
} from 'react-icons/fi'
import useAuthStore from '../store/authStore'

const navSections = [
  {
    title: 'Overview',
    items: [
      { to: '/', icon: FiHome, label: 'Dashboard' },
    ],
  },
  {
    title: 'Clinical',
    items: [
      { to: '/studies', icon: FiFolder, label: 'Studies' },
      { to: '/subjects', icon: FiUsers, label: 'Subjects' },
      { to: '/queries', icon: FiMessageSquare, label: 'Queries' },
    ],
  },
  {
    title: 'Safety & Lab',
    items: [
      { to: '/safety', icon: FiAlertTriangle, label: 'Safety' },
      { to: '/lab', icon: FiActivity, label: 'Laboratory' },
    ],
  },
  {
    title: 'Admin',
    items: [
      { to: '/audit', icon: FiFileText, label: 'Audit Trail' },
    ],
  },
]

export default function Sidebar() {
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

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {navSections.map((section) => (
          <div key={section.title}>
            <p className="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-sidebar-text/60">
              {section.title}
            </p>
            <ul className="space-y-0.5">
              {section.items.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    end={item.to === '/'}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                        isActive
                          ? 'bg-sidebar-active text-sidebar-text-active font-medium shadow-lg shadow-primary-600/20'
                          : 'text-sidebar-text hover:bg-sidebar-hover hover:text-white'
                      }`
                    }
                  >
                    <item.icon className="w-[18px] h-[18px] shrink-0" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {/* Bottom: version */}
      <div className="p-4 border-t border-white/10">
        <p className="text-[11px] text-sidebar-text/50 text-center">v0.1.0 — Day 5 Build</p>
      </div>
    </aside>
  )
}
