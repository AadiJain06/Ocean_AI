import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { email, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="top-bar">
        <Link to="/" className="logo">
          Ocean AI
        </Link>
        <div className="top-actions">
          {email && <span className="user-pill">{email}</span>}
          <button className="ghost" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>
      <main className="main-content">{children}</main>
    </div>
  );
}

