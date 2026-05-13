import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// Response interceptor — centralised error handling.
// Any 4xx/5xx response comes here before reaching your component.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "Something went wrong";
    return Promise.reject(new Error(message));
  },
);

export const taskApi = {
  // GET /tasks?status=todo&page=1&size=20
  getAll: (params = {}) =>
    client.get("/tasks/", { params }).then((r) => r.data),

  // GET /tasks/5
  getOne: (id) => client.get(`/tasks/${id}`).then((r) => r.data),

  // POST /tasks  { title, description, priority }
  create: (data) => client.post("/tasks/", data).then((r) => r.data),

  // PATCH /tasks/5  { status: "done" }
  update: (id, data) => client.patch(`/tasks/${id}`, data).then((r) => r.data),

  // DELETE /tasks/5
  remove: (id) => client.delete(`/tasks/${id}`),

  // PATCH /tasks/5/archive
  archive: (id) => client.patch(`/tasks/${id}/archive`).then((r) => r.data),
};
