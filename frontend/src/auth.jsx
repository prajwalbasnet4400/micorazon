import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, getToken, setToken } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getToken()))

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    if (getToken()) {
      api('/auth/me')
        .then(setUser)
        .catch(logout)
        .finally(() => setLoading(false))
    }
    window.addEventListener('hfp:unauthorized', logout)
    return () => window.removeEventListener('hfp:unauthorized', logout)
  }, [logout])

  const authenticate = async (path, body) => {
    const { token, user } = await api(path, { method: 'POST', body })
    setToken(token)
    setUser(user)
    return user
  }

  const value = {
    user,
    loading,
    login: (body) => authenticate('/auth/login', body),
    signup: (body) => authenticate('/auth/signup', body),
    logout,
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
