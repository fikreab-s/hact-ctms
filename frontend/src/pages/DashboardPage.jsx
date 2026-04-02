import { FiFolder, FiUsers, FiMessageSquare, FiAlertTriangle, FiActivity, FiTrendingUp } from 'react-icons/fi'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { useStudies, useSubjects, useQueries, useAdverseEvents } from '../api/queries'
import StatCard from '../components/StatCard'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import { Link } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const COLORS = ['#10B981', '#0EA5E9', '#6366F1', '#F43F5E', '#F59E0B']

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data: studiesData, isLoading: loadingStudies } = useStudies()
  const { data: subjectsData, isLoading: loadingSubjects } = useSubjects()
  const { data: queriesData, isLoading: loadingQueries } = useQueries()
  const { data: aeData, isLoading: loadingAE } = useAdverseEvents()

  if (loadingStudies || loadingSubjects || loadingQueries || loadingAE) {
    return <LoadingSpinner text="Loading dashboard..." />
  }

  const studies = studiesData?.results || []
  const subjects = subjectsData?.results || []
  const queries = queriesData?.results || []
  const adverseEvents = aeData?.results || []

  // Computed stats
  const totalStudies = studiesData?.count || 0
  const totalSubjects = subjectsData?.count || 0
  const enrolledCount = subjects.filter(s => s.status === 'enrolled').length
  const openQueries = queries.filter(q => q.status === 'open').length
  const saeCount = adverseEvents.filter(ae => ae.serious).length

  // Enrollment by status for pie chart
  const statusCounts = subjects.reduce((acc, s) => {
    acc[s.status] = (acc[s.status] || 0) + 1
    return acc
  }, {})
  const pieData = Object.entries(statusCounts).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }))

  // Studies bar chart data
  const studyBarData = studies.map(s => ({
    name: s.protocol_number?.split('-').pop() || s.name.substring(0, 10),
    enrolled: s.enrolled_count || 0,
    total: s.subject_count || 0,
  }))

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
          Welcome back, {user?.first_name || user?.username}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Here's your clinical trial overview.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <StatCard title="Active Studies" value={totalStudies} icon={FiFolder} variant="primary" subtitle="Total registered" />
        <StatCard title="Subjects" value={totalSubjects} icon={FiUsers} variant="info" subtitle={`${enrolledCount} enrolled`} />
        <StatCard title="Open Queries" value={openQueries} icon={FiMessageSquare} variant={openQueries > 0 ? 'danger' : 'success'} subtitle="Requiring attention" />
        <StatCard title="Adverse Events" value={adverseEvents.length} icon={FiAlertTriangle} variant="warning" subtitle={`${saeCount} serious (SAE)`} />
        <StatCard title="Enrollment Rate" value={totalSubjects > 0 ? `${Math.round((enrolledCount / totalSubjects) * 100)}%` : '—'} icon={FiTrendingUp} variant="success" subtitle="Of screened subjects" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Enrollment Bar Chart */}
        <div className="bg-card rounded-xl border border-border p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Enrollment by Study</h3>
          {studyBarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={studyBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                <Bar dataKey="enrolled" fill="#4F46E5" radius={[4, 4, 0, 0]} name="Enrolled" />
                <Bar dataKey="total" fill="#E0E7FF" radius={[4, 4, 0, 0]} name="Total" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-400 text-center py-10">No study data available</p>
          )}
        </div>

        {/* Subject Status Pie */}
        <div className="bg-card rounded-xl border border-border p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 mb-4">Subject Status Distribution</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-400 text-center py-10">No subject data available</p>
          )}
        </div>
      </div>

      {/* Recent Studies Table */}
      <div className="bg-card rounded-xl border border-border shadow-sm">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">Recent Studies</h3>
          <Link to="/studies" className="text-xs text-primary-600 hover:text-primary-700 font-medium">View all →</Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider border-b border-border">
                <th className="px-5 py-3">Protocol</th>
                <th className="px-5 py-3">Name</th>
                <th className="px-5 py-3">Phase</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Sites</th>
                <th className="px-5 py-3 text-right">Enrolled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {studies.slice(0, 5).map(study => (
                <tr key={study.id} className="hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3">
                    <Link to={`/studies/${study.id}`} className="text-primary-600 hover:text-primary-700 font-medium">
                      {study.protocol_number}
                    </Link>
                  </td>
                  <td className="px-5 py-3 text-slate-700">{study.name}</td>
                  <td className="px-5 py-3 text-slate-600">{study.phase}</td>
                  <td className="px-5 py-3"><StatusBadge status={study.status} /></td>
                  <td className="px-5 py-3 text-right text-slate-600">{study.site_count}</td>
                  <td className="px-5 py-3 text-right font-medium text-slate-700">{study.enrolled_count}</td>
                </tr>
              ))}
              {studies.length === 0 && (
                <tr><td colSpan="6" className="px-5 py-8 text-center text-slate-400">No studies yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
