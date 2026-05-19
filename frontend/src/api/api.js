import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// Intercept every response — clean up errors before components see them
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message || "Something went wrong";
    return Promise.reject(new Error(message));
  }
);

/*
 * getAuthHeaders(token) attaches the token to individual requests.
 * We pass the token explicitly rather than storing it in Axios defaults
 * because the token lives in React state — reading it from a closure
 * is safer than a module-level variable that could go stale.
 */
const getAuthHeaders = (token) => ({
  headers: { Authorization: `Bearer ${token}` },
});

export const taskApi = {
  // ── Auth endpoints (no token needed) ──────────────────────────────
  register: (data)          => client.post("/auth/register", data).then(r => r.data),
  login:    (data)          => client.post("/auth/login",    data).then(r => r.data),
  getMe:    (token)         => client.get("/auth/me", getAuthHeaders(token)).then(r => r.data),

  // ── Task endpoints (token required) ───────────────────────────────
  getAll:   (token, params) => client.get("/tasks/",        { ...getAuthHeaders(token), params }).then(r => r.data),
  getOne:   (token, id)     => client.get(`/tasks/${id}`,    getAuthHeaders(token)).then(r => r.data),
  create:   (token, data)   => client.post("/tasks/",  data, getAuthHeaders(token)).then(r => r.data),
  update:   (token, id, data) => client.patch(`/tasks/${id}`, data, getAuthHeaders(token)).then(r => r.data),
  remove:   (token, id)     => client.delete(`/tasks/${id}`, getAuthHeaders(token)),
  archive:  (token, id)     => client.patch(`/tasks/${id}/archive`, {}, getAuthHeaders(token)).then(r => r.data),
};