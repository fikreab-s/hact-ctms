import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout'
import ProtectedRoute from './auth/ProtectedRoute'
import LoginPage from './auth/LoginPage'
import DashboardPage from './pages/DashboardPage'
import StudiesPage from './pages/StudiesPage'
import StudyDetailPage from './pages/StudyDetailPage'
import SubjectsPage from './pages/SubjectsPage'
import QueriesPage from './pages/QueriesPage'
import SafetyPage from './pages/SafetyPage'
import LabPage from './pages/LabPage'
import AuditPage from './pages/AuditPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* All dashboard routes are protected */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/studies" element={<StudiesPage />} />
            <Route path="/studies/:id" element={<StudyDetailPage />} />
            <Route path="/subjects" element={<SubjectsPage />} />
            <Route path="/queries" element={<QueriesPage />} />
            <Route path="/safety" element={<SafetyPage />} />
            <Route path="/lab" element={<LabPage />} />
            <Route path="/audit" element={<AuditPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
