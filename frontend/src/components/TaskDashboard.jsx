import { useCallback, useEffect, useMemo, useState } from "react";
import { taskApi } from "../api/api";
import { useAuth } from "../context/AuthContext";
import TaskForm from "./TaskForm";
import TaskList from "./TaskList";
import FilterBar from "./FilterBar";

export default function TaskDashboard({ user, onLogout }) {
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [filters, setFilters] = useState({ status: "", priority: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null);

  const stats = useMemo(() => {
    const counts = { todo: 0, in_progress: 0, done: 0 };
    for (const t of tasks) counts[t.status] = (counts[t.status] || 0) + 1;
    return counts;
  }, [tasks]);

  const fetchTasks = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const data = await taskApi.getAll(token, {
        status: filters.status || undefined,
        priority: filters.priority || undefined,
      });
      setTasks(Array.isArray(data.items) ? data.items : data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token, filters.status, filters.priority]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleSubmit = async (form) => {
    if (!token) return;
    if (editing) {
      await taskApi.update(token, editing.id, form);
      setEditing(null);
    } else {
      await taskApi.create(token, form);
    }
    await fetchTasks();
  };

  const handleDelete = async (id) => {
    if (!token) return;
    await taskApi.remove(token, id);
    await fetchTasks();
  };

  const handleToggleStatus = async (task) => {
    if (!token) return;
    const nextStatus = task.status === "done" ? "todo" : "done";
    await taskApi.update(token, task.id, { status: nextStatus });
    await fetchTasks();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>
            Task <span>Manager</span>
          </h1>
          {user?.username && (
            <p style={{ color: "var(--gray-500)", fontSize: "0.875rem" }}>
              Signed in as {user.username}
            </p>
          )}
        </div>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <span className="total-badge">{tasks.length} total</span>
          <button className="btn-outline" onClick={onLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="stats-row">
        <div className="stat-chip stat-chip--todo">
          <span className="stat-chip__dot" />
          To do: {stats.todo}
        </div>
        <div className="stat-chip stat-chip--in_progress">
          <span className="stat-chip__dot" />
          In progress: {stats.in_progress}
        </div>
        <div className="stat-chip stat-chip--done">
          <span className="stat-chip__dot" />
          Done: {stats.done}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <TaskForm
        onSubmit={handleSubmit}
        initialData={editing}
        onCancel={() => setEditing(null)}
      />

      <FilterBar filters={filters} onChange={setFilters} />

      {loading ? (
        <p className="loading-msg">Loading tasksâ€¦</p>
      ) : (
        <TaskList
          tasks={tasks}
          onEdit={setEditing}
          onDelete={handleDelete}
          onToggleStatus={handleToggleStatus}
        />
      )}
    </div>
  );
}

