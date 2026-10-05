import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import NavBar from './components/NavBar'
import ForgotPassword from './pages/ForgotPassword'
import History from './pages/History'
import Login from './pages/Login'
import PredictionForm from './pages/PredictionForm'
import Result from './pages/Result'
import Signup from './pages/Signup'

function ProtectedLayout() {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-loading">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return (
    <div className="app-shell">
      <NavBar />
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}

function PublicOnly({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-loading">Loading…</div>
  return user ? <Navigate to="/predict" replace /> : children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
      <Route path="/signup" element={<PublicOnly><Signup /></PublicOnly>} />
      <Route path="/forgot-password" element={<PublicOnly><ForgotPassword /></PublicOnly>} />
      <Route element={<ProtectedLayout />}>
        <Route path="/predict" element={<PredictionForm />} />
        <Route path="/result/:id" element={<Result />} />
        <Route path="/history" element={<History />} />
      </Route>
      <Route path="*" element={<Navigate to="/predict" replace />} />
    </Routes>
  )
}
