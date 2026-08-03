import { createContext, useContext, useEffect, useState } from 'react'
import client from '../api/client'

// This "context" holds the current user so any page can ask "who's logged in?"
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // On first load: if a token is saved, fetch the matching user.
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }
    client
      .get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem('token')) // bad/expired token
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const res = await client.post('/auth/login', { email, password })
    localStorage.setItem('token', res.data.access_token)
    const me = await client.get('/auth/me')
    setUser(me.data)
    return me.data
  }

  async function register(name, email, password) {
    await client.post('/auth/register', { name, email, password })
    return login(email, password) // log them straight in after signup
  }

  function logout() {
    localStorage.removeItem('token')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin: user?.role === 'admin',
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Shortcut hook so pages can write: const { user } = useAuth()
export function useAuth() {
  return useContext(AuthContext)
}
