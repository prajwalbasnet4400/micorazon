import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function History() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api('/predictions')
      .then(setItems)
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="alert alert-error">{error}</div>
  if (!items) return <div className="page-loading">Loading history…</div>

  return (
    <div className="history-page">
      <h1 className="page-title">Prediction History</h1>
      {items.length === 0 ? (
        <div className="panel empty">
          No predictions yet. <Link to="/predict">Make your first prediction</Link>.
        </div>
      ) : (
        <div className="panel table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Status</th>
                <th>Risk Level</th>
                <th>Risk Probability</th>
                <th>Age</th>
                <th>Ejection Fraction</th>
                <th>Serum Creatinine</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(`${item.created_at.replace(' ', 'T')}Z`).toLocaleString()}</td>
                  <td className={item.status === 'At Risk' ? 'text-risk' : 'text-healthy'}>{item.status}</td>
                  <td>{item.risk_level}</td>
                  <td>{(item.probability_at_risk * 100).toFixed(1)}%</td>
                  <td>{item.inputs.age}</td>
                  <td>{item.inputs.ejection_fraction}%</td>
                  <td>{item.inputs.serum_creatinine}</td>
                  <td>
                    <Link to={`/result/${item.id}`}>View</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
