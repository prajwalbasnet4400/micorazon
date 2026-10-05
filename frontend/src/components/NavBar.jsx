import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="navbar">
      <NavLink to="/predict" className="brand">
        <img src="/heart.svg" alt="" /> HFP
      </NavLink>
      <nav>
        <NavLink to="/predict">Predict</NavLink>
        <NavLink to="/history">History</NavLink>
      </nav>
      <div className="navbar-user">
        <span className="navbar-name">{user.name}</span>
        <button className="btn btn-danger btn-sm" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  )
}
