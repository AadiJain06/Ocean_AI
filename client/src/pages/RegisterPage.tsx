import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";

export function RegisterPage() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/auth/register", {
        email,
        full_name: fullName,
        password,
      });
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-card">
      <h1>Create account</h1>
      <p>Start new Word and PowerPoint projects.</p>
      <form onSubmit={handleSubmit}>
        <label>Full name</label>
        <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create account"}
        </button>
      </form>
      <p>
        Have an account? <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}

