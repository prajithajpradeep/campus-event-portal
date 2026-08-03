import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'

export default function MyEvents() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client
      .get('/me/registrations')
      .then((res) => setEvents(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="muted">Loading…</p>

  return (
    <div>
      <h1>My events</h1>
      {events.length === 0 ? (
        <div className="empty">
          You haven’t registered for any events yet. Head to <Link to="/events">Events</Link> to find some.
        </div>
      ) : (
        <div className="grid">
          {events.map((ev) => (
            <Link to={`/events/${ev.id}`} key={ev.id} className="card event-card">
              <div className="event-body">
                <h3>{ev.title}</h3>
                <p className="muted">{new Date(ev.start_time).toLocaleString()}</p>
                <p className="muted">{ev.location || 'Location TBA'}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
