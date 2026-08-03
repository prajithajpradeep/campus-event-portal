import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function EventDetail() {
  const { id } = useParams()
  const { isAdmin } = useAuth()
  const navigate = useNavigate()
  const [event, setEvent] = useState(null)
  const [registered, setRegistered] = useState(false)
  const [msg, setMsg] = useState('')

  function load() {
    client.get(`/events/${id}`).then((res) => setEvent(res.data))
    client
      .get('/me/registrations')
      .then((res) => setRegistered(res.data.some((e) => e.id === id)))
      .catch(() => {})
  }
  useEffect(load, [id])

  async function doRegister() {
    setMsg('')
    try {
      await client.post(`/events/${id}/registrations`)
      setMsg('You are registered!')
      load()
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Could not register.')
    }
  }

  async function doCancel() {
    setMsg('')
    try {
      await client.delete(`/events/${id}/registrations`)
      setMsg('Registration cancelled.')
      load()
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Could not cancel.')
    }
  }

  async function doDelete() {
    if (!confirm('Delete this event? This cannot be undone.')) return
    await client.delete(`/events/${id}`)
    navigate('/events')
  }

  async function uploadBanner(e) {
    const file = e.target.files[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    await client.post(`/events/${id}/banner`, form)
    load()
  }

  if (!event) return <p className="muted">Loading…</p>

  return (
    <div className="detail">
      {event.banner_url ? (
        <img src={event.banner_url} alt="" className="detail-banner" />
      ) : (
        <div className="detail-banner placeholder">{event.title[0]}</div>
      )}

      <h1>{event.title}</h1>
      <p className="muted">
        {new Date(event.start_time).toLocaleString()} – {new Date(event.end_time).toLocaleString()}
      </p>
      <p className="muted">
        {event.location || 'Location TBA'} · {event.registered_count} registered
        {event.capacity ? ` / ${event.capacity} spots` : ''}
      </p>
      {event.description && <p className="description">{event.description}</p>}

      {msg && <div className="alert info">{msg}</div>}

      {!isAdmin &&
        (registered ? (
          <button className="btn btn-danger" onClick={doCancel}>
            Cancel registration
          </button>
        ) : (
          <button className="btn" onClick={doRegister}>
            Register for this event
          </button>
        ))}

      {isAdmin && (
        <div className="admin-actions">
          <Link className="btn btn-ghost" to={`/admin/events/${id}/edit`}>
            Edit
          </Link>
          <Link className="btn btn-ghost" to={`/admin/events/${id}/participants`}>
            View participants
          </Link>
          <label className="btn btn-ghost file-btn">
            Upload banner
            <input type="file" accept="image/*" onChange={uploadBanner} hidden />
          </label>
          <button className="btn btn-danger" onClick={doDelete}>
            Delete
          </button>
        </div>
      )}
    </div>
  )
}
