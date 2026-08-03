import { useEffect, useState } from 'react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user } = useAuth()
  const [name, setName] = useState('')
  const [msg, setMsg] = useState('')

  useEffect(() => {
    if (user) setName(user.name)
  }, [user])

  async function save(e) {
    e.preventDefault()
    setMsg('')
    await client.patch('/users/me', { name })
    setMsg('Profile updated.')
  }

  if (!user) return null

  return (
    <div className="auth-card">
      <h1>Profile</h1>
      {msg && <div className="alert info">{msg}</div>}
      <form onSubmit={save}>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Email
          <input value={user.email} disabled />
        </label>
        <label>
          Role
          <input value={user.role} disabled />
        </label>
        <button className="btn">Save changes</button>
      </form>
    </div>
  )
}
