import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import api from "../services/api";

function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const loadUnreadCount = async () => {
      if (!isAuthenticated) {
        setUnreadCount(0);
        return;
      }

      try {
        const response = await api.get(
          "auth/notifications/unread-count/"
        );

        setUnreadCount(response.data.unread_count);
      } catch (err) {
        console.error(err);
      }
    };

    loadUnreadCount();
  }, [isAuthenticated, location.pathname]);



  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate("/login");
  };

  return (
    <nav>
      <Link to="/" className="navbar-brand">
        RedNote
      </Link>

      <button
        className="navbar-menu-button"
        onClick={() => setMenuOpen((current) => !current)}
        aria-label="Toggle navigation menu"
        aria-expanded={menuOpen}
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <div
        className={`navbar-links ${menuOpen ? "open" : ""}`}
        onClick={(e) => {
          if (e.target.closest("a")) {
            setMenuOpen(false);
          }
        }}
      >
        <NavLink to="/search">Search</NavLink>

        <NavLink to="/create">Create Post</NavLink>

        <NavLink to="/saved">Saved</NavLink>

        <NavLink to="/profile">Profile</NavLink>

        <NavLink to="/notifications">
          Notifications
          {unreadCount > 0 && ` (${unreadCount})`}
        </NavLink>

        {isAuthenticated ? (
          <button
            className="navbar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>

            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;