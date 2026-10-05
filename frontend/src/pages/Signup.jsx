import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import PasswordInput from '../components/PasswordInput'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', phone: '', address: '', password: '' })
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setFieldErrors({})
    setLoading(true)
    try {
      await signup({ ...form, phone: form.phone.replace(/[\s-]/g, '') })
      navigate('/predict')
    } catch (err) {
      setError(err.message)
      setFieldErrors(err.fieldErrors || {})
    } finally {
      setLoading(false)
    }
  }

  const fieldError = (name) => fieldErrors[name] && <span className="field-error">{fieldErrors[name]}</span>

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Sign Up</h1>
        {error && <div className="alert alert-error">{error}</div>}
        <label>
          Name
          <input name="name" placeholder="John Doe" value={form.name} onChange={handleChange} required />
          {fieldError('name')}
        </label>
        <label>
          Email
          <input name="email" type="email" placeholder="you@example.com" value={form.email} onChange={handleChange} required />
          {fieldError('email')}
        </label>
        <label>
          Phone Number
          <input name="phone" type="tel" placeholder="e.g. 9876543210" value={form.phone} onChange={handleChange} required />
          {fieldError('phone')}
        </label>
        <label>
          Address
          <textarea name="address" placeholder="House/Street, City" rows={2} value={form.address} onChange={handleChange} required />
          {fieldError('address')}
        </label>
        <label>
          Password
          <PasswordInput
            name="password"
            placeholder="Minimum 8 characters"
            minLength={8}
            value={form.password}
            onChange={handleChange}
            required
          />
          {fieldError('password')}
        </label>
        <button className="btn btn-light" disabled={loading}>
          {loading ? 'Creating account…' : 'Sign Up'}
        </button>
        <Link to="/login" className="auth-switch auth-back">
          Back to Login
        </Link>
      </form>
    </div>
  )
}
