import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout'
import ProtectedRoute from './auth/ProtectedRoute'
import LoginPage from './auth/LoginPage'
import CallbackPage from './auth/CallbackPage'
import DashboardPage from './pages/DashboardPage'
import StudiesPage from './pages/StudiesPage'
import StudyDetailPage from './pages/StudyDetailPage'
import SubjectsPage from './pages/SubjectsPage'
import SubjectDetailPage from './pages/SubjectDetailPage'
import QueriesPage from './pages/QueriesPage'
import SafetyPage from './pages/SafetyPage'
import LabPage from './pages/LabPage'
import AuditPage from './pages/AuditPage'
import IntegrationStatusPage from './pages/IntegrationStatusPage'
import ExternalSystemPage from './pages/ExternalSystemPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<CallbackPage />} />

        {/* All dashboard routes are protected */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/studies" element={<StudiesPage />} />
            <Route path="/studies/:id" element={<StudyDetailPage />} />
            <Route path="/subjects" element={<SubjectsPage />} />
            <Route path="/subjects/:id" element={<SubjectDetailPage />} />
            <Route path="/queries" element={<QueriesPage />} />
            <Route path="/safety" element={<SafetyPage />} />
            <Route path="/lab" element={<LabPage />} />
            <Route path="/audit" element={<AuditPage />} />
            <Route path="/integrations" element={<IntegrationStatusPage />} />
            <Route path="/integrations/openclinica" element={<ExternalSystemPage systemKey="openclinica" />} />
            <Route path="/integrations/senaite" element={<ExternalSystemPage systemKey="senaite" />} />
            <Route path="/integrations/nextcloud" element={<ExternalSystemPage systemKey="nextcloud" />} />
            <Route path="/integrations/erpnext" element={<ExternalSystemPage systemKey="erpnext" />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
