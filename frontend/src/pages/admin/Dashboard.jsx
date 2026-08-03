import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState({ items: [] })

  useEffect(() => {
    client.get('/admin/stats').then((res) => setStats(res.data))
    client.get('/users', { params: { size: 5 } }).then((res) => setUsers(res.data))
  }, [])

  if (!stats) return <p className="muted">Loading…</p>

  const cards = [
    { label: 'Users', value: stats.total_users },
    { label: 'Events', value: stats.total_events },
    { label: 'Upcoming', value: stats.upcoming_events },
    { label: 'Registrations', value: stats.total_registrations },
    { label: 'Active now', value: stats.active_registrations },
  ]

  return (
    <div>
      <div className="page-head">
        <h1>Dashboard</h1>
        <Link to="/admin/events/new" className="btn">
          + New event
        </Link>
      </div>

      <div className="stats">
        {cards.map((c) => (
          <div className="stat" key={c.label}>
            <div className="stat-value">{c.value}</div>
            <div className="stat-label">{c.label}</div>
          </div>
        ))}
      </div>

      <h2 className="section-title">Recent users</h2>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.items.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>
                  <span className={`role role-${u.role}`}>{u.role}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
