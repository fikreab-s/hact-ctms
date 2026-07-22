import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopBar from '../components/TopBar'
import FeedbackWidget from '../components/FeedbackWidget'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-surface">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="lg:ml-64 transition-[margin] duration-300">
        <TopBar onMenuToggle={() => setSidebarOpen(prev => !prev)} />
        <main className="p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
      <FeedbackWidget />
    </div>
  )
}
