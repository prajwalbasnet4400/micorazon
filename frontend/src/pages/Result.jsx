import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import { formatValue } from '../medicalInfo'

const pct = (p) => `${(p * 100).toFixed(2)}%`

export default function Result() {
  const { id } = useParams()
  const { user } = useAuth()
  const passed = useLocation().state?.result
  const [result, setResult] = useState(passed?.id === Number(id) ? passed : null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (result?.id !== Number(id)) {
      setError('')
      api(`/predictions/${id}`)
        .then(setResult)
        .catch((err) => setError(err.message))
    }
  }, [id, result])

  if (error) return <div className="alert alert-error">{error}</div>
  if (result?.id !== Number(id)) return <div className="page-loading">Loading result…</div>

  const atRisk = result.status === 'At Risk'
  const downloadReport = async () => {
    const { generateReport } = await import('../pdfReport')
    generateReport(user, result)
  }
  const maxContribution = Math.max(...result.top_factors.map((f) => Math.abs(f.contribution)), 1e-6)

  return (
    <div className="result-page">
      <h1 className="page-title">
        <img src="/heart.svg" alt="" /> Prediction Result
      </h1>

      <div className={`result-card ${atRisk ? 'is-risk' : 'is-healthy'}`}>
        <div className="patient-details">
          <h3>Patient Details</h3>
          <p><b>Name:</b> {user.name}</p>
          <p><b>Email:</b> {user.email}</p>
          <p><b>Phone:</b> {user.phone}</p>
          <p><b>Address:</b> {user.address}</p>
        </div>

        <div className="result-status">
          <p className="status-line">
            {atRisk ? '⚠️' : '✅'} <b>Status:</b> {result.status}
            <span className={`risk-badge risk-${result.risk_level.replace(' ', '-').toLowerCase()}`}>
              {result.risk_level} risk
            </span>
          </p>
          <div className="prob-bar" aria-hidden="true">
            <div className="prob-bar-fill" style={{ width: pct(result.probability_at_risk) }} />
          </div>
          <p><b>Healthy Probability:</b> {pct(result.probability_healthy)}</p>
          <p><b>Risk Probability:</b> {pct(result.probability_at_risk)}</p>
        </div>
      </div>

      <div className="result-grid">
        <section className="panel">
          <h2>Key Contributing Factors</h2>
          <p className="panel-hint">How each input pushed this patient's predicted risk up or down (SHAP values).</p>
          <ul className="factor-list">
            {result.top_factors.map((f) => (
              <li key={f.feature}>
                <div className="factor-head">
                  <span>{f.label}: <b>{formatValue(f.feature, f.value)}</b></span>
                  <span className={f.direction === 'increases' ? 'text-risk' : 'text-healthy'}>
                    {f.direction === 'increases' ? '▲ increases risk' : '▼ decreases risk'}
                  </span>
                </div>
                <div className="factor-bar">
                  <div
                    className={f.direction === 'increases' ? 'bar-risk' : 'bar-healthy'}
                    style={{ width: `${(Math.abs(f.contribution) / maxContribution) * 100}%` }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel">
          <h2>Suggestions</h2>
          <ul className="suggestion-list">
            {result.suggestions.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
          <p className="disclaimer">
            This prediction supports, but does not replace, professional medical judgement.
          </p>
        </section>
      </div>

      <div className="form-actions">
        <button className="btn btn-primary" onClick={downloadReport}>
          Download PDF Report
        </button>
        <Link to="/predict" className="btn btn-ghost">
          Predict Again
        </Link>
      </div>
    </div>
  )
}
