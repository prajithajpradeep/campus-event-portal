import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import client from '../../api/client'

const emptyForm = {
  title: '',
  description: '',
  location: '',
  start_time: '',
  end_time: '',
  capacity: 0,
}

export default function EventForm() {
  const { id } = useParams()
  const editing = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')

  // When editing, load the existing event into the form.
  useEffect(() => {
    if (!editing) return
    client.get(`/events/${id}`).then((res) => {
      const e = res.data
      setForm({
        title: e.title,
        description: e.description,
        location: e.location,
        // trim the ISO string to what a datetime-local input expects
        start_time: e.start_time.slice(0, 16),
        end_time: e.end_time.slice(0, 16),
        capacity: e.capacity,
      })
    })
  }, [id])

  function update(field, value) {
    setForm({ ...form, [field]: value })
  }

  async function submit(e) {
    e.preventDefault()
    setError('')
    const payload = {
      ...form,
      capacity: Number(form.capacity),
      start_time: new Date(form.start_time).toISOString(),
      end_time: new Date(form.end_time).toISOString(),
    }
    try {
      if (editing) await client.put(`/events/${id}`, payload)
      else await client.post('/events', payload)
      navigate('/events')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Please check the fields and try again.')
    }
  }

  return (
    <div className="auth-card wide">
      <h1>{editing ? 'Edit event' : 'New event'}</h1>
      <form onSubmit={submit}>
        {error && <div className="alert">{error}</div>}
        <label>
          Title
          <input value={form.title} onChange={(e) => update('title', e.target.value)} required />
        </label>
        <label>
          Description
          <textarea value={form.description} onChange={(e) => update('description', e.target.value)} />
        </label>
        <label>
          Location
          <input value={form.location} onChange={(e) => update('location', e.target.value)} />
        </label>
        <div className="row">
          <label>
            Starts
            <input
              type="datetime-local"
              value={form.start_time}
              onChange={(e) => update('start_time', e.target.value)}
              required
            />
          </label>
          <label>
            Ends
            <input
              type="datetime-local"
              value={form.end_time}
              onChange={(e) => update('end_time', e.target.value)}
              required
            />
          </label>
        </div>
        <label>
          Capacity (0 = unlimited)
          <input
            type="number"
            min="0"
            value={form.capacity}
            onChange={(e) => update('capacity', e.target.value)}
          />
        </label>
        <button className="btn">{editing ? 'Save changes' : 'Create event'}</button>
      </form>
    </div>
  )
}
