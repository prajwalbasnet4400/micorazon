// Field definitions for the prediction form. Ranges mirror backend validation (schemas.py).

export const FIELDS = {
  age: { label: 'Age', unit: 'years', min: 1, max: 120, step: 1, default: 60 },
  sex: { label: 'Sex', type: 'select', options: [[1, 'Male'], [0, 'Female']], default: 1 },
  serum_sodium: { label: 'Serum Sodium', unit: 'mEq/L', min: 100, max: 160, step: 1, default: 135 },
  serum_creatinine: { label: 'Serum Creatinine', unit: 'mg/dL', min: 0.1, max: 15, step: 0.1, default: 1 },
  platelets: { label: 'Platelets', unit: 'kiloplatelets/mL', min: 10000, max: 1000000, step: 1000, default: 250000 },
  high_blood_pressure: { label: 'High Blood Pressure', type: 'yesno', default: 0 },
  ejection_fraction: { label: 'Ejection Fraction', unit: '%', min: 5, max: 90, step: 1, default: 38 },
  diabetes: { label: 'Diabetes', type: 'yesno', default: 0 },
  creatinine_phosphokinase: {
    label: 'Creatinine Phosphokinase',
    unit: 'mcg/L',
    min: 1,
    max: 10000,
    step: 1,
    default: 250,
  },
  anaemia: { label: 'Anaemia', type: 'yesno', default: 0 },
  smoking: { label: 'Smoking', type: 'yesno', default: 0 },
  time: { label: 'Follow-up Time', unit: 'days', min: 0, max: 365, step: 1, default: 120 },
}

export const SECTIONS = [
  { key: 'general', title: 'General Info', icon: '👤', color: 'blue', fields: ['age', 'sex'] },
  {
    key: 'medical',
    title: 'Medical Info',
    icon: '🩺',
    color: 'purple',
    fields: [
      'serum_sodium',
      'serum_creatinine',
      'platelets',
      'high_blood_pressure',
      'ejection_fraction',
      'diabetes',
      'creatinine_phosphokinase',
      'anaemia',
    ],
  },
  { key: 'habit', title: 'Habit Info', icon: '🚭', color: 'pink', fields: ['smoking', 'time'] },
]

export const MEDICAL_INFO_DESCRIPTIONS = {
  age: 'Age of the patient in years. Risk of heart failure increases with age.',
  sex: 'Biological sex of the patient.',
  serum_sodium: 'Level of sodium in the blood. Normal range is 135-145 mEq/L; low sodium is linked to worse outcomes.',
  serum_creatinine:
    'Level of creatinine in the blood, a marker of kidney function. Normal is roughly 0.6-1.3 mg/dL.',
  platelets: 'Number of platelets in the blood. Normal range is 150,000-450,000 per mL.',
  high_blood_pressure: 'Whether the patient has been diagnosed with hypertension.',
  ejection_fraction:
    'Percentage of blood leaving the heart at each contraction. Normal is 50-70%; below 40% indicates reduced function.',
  diabetes: 'Whether the patient has diabetes.',
  creatinine_phosphokinase:
    'Level of the CPK enzyme in the blood. Normal is about 10-120 mcg/L; high values can indicate heart or muscle damage.',
  anaemia: 'Decrease of red blood cells or hemoglobin.',
  smoking: 'Whether the patient smokes.',
  time: 'Follow-up period in days since the patient was first assessed.',
}

export const defaultFormData = () =>
  Object.fromEntries(Object.entries(FIELDS).map(([key, field]) => [key, String(field.default)]))

export function formatValue(key, value) {
  const field = FIELDS[key]
  if (field.type === 'yesno') return Number(value) ? 'Yes' : 'No'
  if (field.type === 'select') return field.options.find(([v]) => v === Number(value))?.[1] ?? value
  const num = Number(value)
  const text = key === 'platelets' ? num.toLocaleString() : String(num)
  return field.unit ? `${text} ${field.unit}` : text
}

export function validate(formData) {
  const errors = {}
  for (const [key, field] of Object.entries(FIELDS)) {
    if (field.type) continue
    const raw = formData[key]
    const num = Number(raw)
    if (raw === '' || Number.isNaN(num)) errors[key] = 'Required'
    else if (num < field.min || num > field.max) errors[key] = `Must be between ${field.min} and ${field.max}`
    else if (field.step === 1 && !Number.isInteger(num)) errors[key] = 'Must be a whole number'
  }
  return errors
}
