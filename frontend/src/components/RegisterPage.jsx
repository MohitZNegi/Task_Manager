import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage({ onSwitch }) {
  const { register, error } = useAuth();
  const [form, setForm] = useState({ email: "", username: "", password: "" });
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    await register(form.email, form.username, form.password);
    setBusy(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create account</h1>
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
            type="text"
            placeholder="Username"
            required
            value={form.username}
            onChange={(e) =>
              setForm((f) => ({ ...f, username: e.target.value }))
            }
          />
          <input
            type="password"
            placeholder="Password (8+ chars)"
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
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <p className="auth-switch">
          Have an account?{" "}
          <button onClick={onSwitch} className="btn-link">
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
