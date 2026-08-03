import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        Campus<span>Events</span>
      </Link>

      <nav className="nav-links">
        {user && <Link to="/events">Events</Link>}
        {user && !isAdmin && <Link to="/my-events">My events</Link>}
        {user && <Link to="/announcements">Announcements</Link>}
        {isAdmin && <Link to="/admin">Dashboard</Link>}
        {user && <Link to="/profile">Profile</Link>}
      </nav>

      <div className="nav-right">
        {user ? (
          <>
            <span className="user-chip">
              {user.name}
              {isAdmin && <em> · admin</em>}
            </span>
            <button className="btn btn-ghost" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <Link to="/login" className="btn">
            Log in
          </Link>
        )}
      </div>
    </header>
  )
}
