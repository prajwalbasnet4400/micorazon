import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { FIELDS, MEDICAL_INFO_DESCRIPTIONS, SECTIONS, defaultFormData, validate } from '../medicalInfo'

export default function PredictionForm() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState(defaultFormData)
  const [errors, setErrors] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [focusedField, setFocusedField] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const found = validate(formData)
    setErrors(found)
    if (Object.keys(found).length) {
      setError('Please correct the highlighted fields.')
      return
    }
    setLoading(true)
    try {
      const body = Object.fromEntries(Object.entries(formData).map(([k, v]) => [k, Number(v)]))
      const result = await api('/predict', { method: 'POST', body })
      navigate(`/result/${result.id}`, { state: { result } })
    } catch (err) {
      setError(err.message)
      setErrors(err.fieldErrors || {})
    } finally {
      setLoading(false)
    }
  }

  const renderField = (key) => {
    const field = FIELDS[key]
    const common = {
      id: key,
      name: key,
      value: formData[key],
      onChange: handleChange,
      onFocus: () => setFocusedField(key),
      onBlur: () => setFocusedField(null),
      'aria-invalid': Boolean(errors[key]),
    }
    let input
    if (field.type === 'select' || field.type === 'yesno') {
      const options = field.type === 'yesno' ? [[0, 'No'], [1, 'Yes']] : field.options
      input = (
        <select {...common}>
          {options.map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      )
    } else {
      input = <input {...common} type="number" min={field.min} max={field.max} step={field.step} />
    }
    return (
      <div key={key} className={`form-field ${errors[key] ? 'has-error' : ''}`}>
        <label htmlFor={key}>
          {field.label}
          {field.unit && <span className="unit"> ({field.unit})</span>}
          <span className="info" title={MEDICAL_INFO_DESCRIPTIONS[key]}>
            ⓘ
          </span>
        </label>
        {input}
        {errors[key] && <span className="field-error">{errors[key]}</span>}
        {focusedField === key && <p className="field-help">{MEDICAL_INFO_DESCRIPTIONS[key]}</p>}
      </div>
    )
  }

  return (
    <form className="predict-page" onSubmit={handleSubmit} noValidate>
      <h1 className="page-title">
        <img src="/heart.svg" alt="" /> Heart Failure Risk Prediction
      </h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="section-grid">
        {SECTIONS.map((section) => (
          <section key={section.key} className={`section-card section-${section.color}`}>
            <div className="section-icon">{section.icon}</div>
            <h2>{section.title}</h2>
            {section.fields.map(renderField)}
          </section>
        ))}
      </div>
      <div className="form-actions">
        <button type="button" className="btn btn-ghost" onClick={() => setFormData(defaultFormData())}>
          Reset
        </button>
        <button className="btn btn-gradient" disabled={loading}>
          {loading ? 'Predicting…' : '● Predict Risk'}
        </button>
      </div>
    </form>
  )
}
