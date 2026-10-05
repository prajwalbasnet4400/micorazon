import { useState } from 'react'

export default function PasswordInput(props) {
  const [visible, setVisible] = useState(false)
  return (
    <div className="password-input">
      <input {...props} type={visible ? 'text' : 'password'} />
      <button
        type="button"
        className="password-toggle"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? 'Hide password' : 'Show password'}
      >
        {visible ? '🙈' : '👁'}
      </button>
    </div>
  )
}
