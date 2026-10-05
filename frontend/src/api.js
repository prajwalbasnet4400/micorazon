const TOKEN_KEY = 'hfp_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) =>
  token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY)

export class ApiError extends Error {
  constructor(message, status, fieldErrors = {}) {
    super(message)
    this.status = status
    this.fieldErrors = fieldErrors
  }
}

// FastAPI returns validation errors as a list; flatten them to { field: message }.
function parseError(status, body) {
  if (Array.isArray(body?.detail)) {
    const fieldErrors = {}
    for (const err of body.detail) {
      fieldErrors[err.loc[err.loc.length - 1]] = err.msg.replace(/^Value error, /, '')
    }
    return new ApiError('Please correct the highlighted fields.', status, fieldErrors)
  }
  return new ApiError(body?.detail || `Request failed (${status})`, status)
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new ApiError('Cannot reach the server. Is the backend running?', 0)
  }
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    if (res.status === 401 && token) window.dispatchEvent(new Event('hfp:unauthorized'))
    throw parseError(res.status, data)
  }
  return data
}
