import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import client from '../../api/client'

export default function Participants() {
  const { id } = useParams()
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get(`/events/${id}/registrations`)
      .then((res) => setRows(res.data))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="muted">Loading…</p>

  return (
    <div>
      <div className="page-head">
        <h1>Participants ({rows.length})</h1>
        <Link className="btn btn-ghost" to={`/events/${id}`}>
          Back to event
        </Link>
      </div>
      {rows.length === 0 ? (
        <div className="empty">No one has registered yet.</div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Registered at</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.registration_id}>
                  <td>{r.name}</td>
                  <td>{r.email}</td>
                  <td>{new Date(r.registered_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
