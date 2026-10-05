import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import PasswordInput from '../components/PasswordInput'

// Prefilled in development only; matches the account seeded by the backend with HFP_SEED_DEMO=1.
const DEMO_CREDENTIALS = import.meta.env.DEV
  ? { email: 'demo@hfp.com', password: 'demo12345' }
  : { email: '', password: '' }

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const notice = useLocation().state?.notice
  const [form, setForm] = useState(DEMO_CREDENTIALS)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form)
      navigate('/predict')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Login</h1>
        {notice && <div className="alert alert-success">{notice}</div>}
        {error && <div className="alert alert-error">{error}</div>}
        <label>
          Email
          <input name="email" type="email" placeholder="you@example.com" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Password
          <PasswordInput name="password" placeholder="••••••••" value={form.password} onChange={handleChange} required />
        </label>
        <button className="btn btn-light" disabled={loading}>
          {loading ? 'Logging in…' : 'Login'}
        </button>
        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
        <Link to="/forgot-password" className="auth-forgot">
          Forgot password?
        </Link>
      </form>
    </div>
  )
}
