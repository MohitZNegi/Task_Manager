import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage({ onSwitch }) {
  const { login, error } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    await login(form.email, form.password);
    setBusy(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Welcome back</h1>
        {error && <p className="form-error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={form.password}
            onChange={(e) =>
              setForm((f) => ({ ...f, password: e.target.value }))
            }
          />
          <button
            type="submit"
            className="btn-primary btn-full"
            disabled={busy}
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="auth-switch">
          No account?{" "}
          <button onClick={onSwitch} className="btn-link">
            Register
          </button>
        </p>
      </div>
    </div>
  );
}
