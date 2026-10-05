import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import PasswordInput from '../components/PasswordInput'

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', phone: '', new_password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.new_password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      const { message } = await api('/auth/reset-password', {
        method: 'POST',
        body: { email: form.email, phone: form.phone.replace(/[\s-]/g, ''), new_password: form.new_password },
      })
      navigate('/login', { state: { notice: message } })
    } catch (err) {
      setError(err.fieldErrors?.new_password ? `Password: ${err.fieldErrors.new_password}` : err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Reset Password</h1>
        <p className="auth-hint">Confirm the email and phone number registered with your account.</p>
        {error && <div className="alert alert-error">{error}</div>}
        <label>
          Email
          <input name="email" type="email" placeholder="you@example.com" value={form.email} onChange={handleChange} required />
        </label>
        <label>
          Phone Number
          <input name="phone" type="tel" placeholder="e.g. 9876543210" value={form.phone} onChange={handleChange} required />
        </label>
        <label>
          New Password
          <PasswordInput name="new_password" placeholder="Minimum 8 characters" minLength={8} value={form.new_password} onChange={handleChange} required />
        </label>
        <label>
          Confirm Password
          <PasswordInput name="confirm" placeholder="Repeat new password" minLength={8} value={form.confirm} onChange={handleChange} required />
        </label>
        <button className="btn btn-light" disabled={loading}>
          {loading ? 'Updating…' : 'Reset Password'}
        </button>
        <Link to="/login" className="auth-switch auth-back">
          Back to Login
        </Link>
      </form>
    </div>
  )
}
