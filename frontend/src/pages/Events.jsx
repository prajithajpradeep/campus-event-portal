import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Events() {
  const { isAdmin } = useAuth()
  const [data, setData] = useState({ items: [], total: 0, page: 1, size: 9, pages: 0 })
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  // Re-fetch whenever the search text or page changes.
  useEffect(() => {
    setLoading(true)
    client
      .get('/events', { params: { q: q || undefined, page, size: 9 } })
      .then((res) => setData(res.data))
      .finally(() => setLoading(false))
  }, [q, page])

  return (
    <div>
      <div className="page-head">
        <h1>Events</h1>
        {isAdmin && (
          <Link to="/admin/events/new" className="btn">
            + New event
          </Link>
        )}
      </div>

      <input
        className="search"
        placeholder="Search events by name…"
        value={q}
        onChange={(e) => {
          setPage(1)
          setQ(e.target.value)
        }}
      />

      {loading ? (
        <p className="muted">Loading…</p>
      ) : data.items.length === 0 ? (
        <div className="empty">
          No events found. {isAdmin && 'Use “+ New event” to create the first one.'}
        </div>
      ) : (
        <div className="grid">
          {data.items.map((ev) => (
            <Link to={`/events/${ev.id}`} key={ev.id} className="card event-card">
              {ev.banner_url ? (
                <img src={ev.banner_url} alt="" className="event-banner" />
              ) : (
                <div className="event-banner placeholder">{ev.title[0]}</div>
              )}
              <div className="event-body">
                <h3>{ev.title}</h3>
                <p className="muted">{new Date(ev.start_time).toLocaleString()}</p>
                <p className="muted">{ev.location || 'Location TBA'}</p>
                <span className="pill">{ev.registered_count} registered</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {data.pages > 1 && (
        <div className="pagination">
          <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Prev
          </button>
          <span>
            Page {data.page} of {data.pages}
          </span>
          <button
            className="btn btn-ghost"
            disabled={page >= data.pages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
