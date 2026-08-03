import { useEffect, useState } from 'react'
import client from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Announcements() {
  const { isAdmin } = useAuth()
  const [items, setItems] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')

  function load() {
    client.get('/announcements').then((res) => setItems(res.data))
  }
  useEffect(load, [])

  async function create(e) {
    e.preventDefault()
    await client.post('/announcements', { title, body })
    setTitle('')
    setBody('')
    load()
  }

  async function remove(id) {
    await client.delete(`/announcements/${id}`)
    load()
  }

  return (
    <div>
      <h1>Announcements</h1>

      {isAdmin && (
        <form className="card inline-form" onSubmit={create}>
          <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <textarea placeholder="Message" value={body} onChange={(e) => setBody(e.target.value)} />
          <button className="btn">Post announcement</button>
        </form>
      )}

      {items.length === 0 ? (
        <div className="empty">No announcements yet.</div>
      ) : (
        items.map((a) => (
          <div className="card announcement" key={a.id}>
            <div>
              <h3>{a.title}</h3>
              <p className="muted">{new Date(a.created_at).toLocaleString()}</p>
              {a.body && <p>{a.body}</p>}
            </div>
            {isAdmin && (
              <button className="btn btn-ghost" onClick={() => remove(a.id)}>
                Delete
              </button>
            )}
          </div>
        ))
      )}
    </div>
  )
}
