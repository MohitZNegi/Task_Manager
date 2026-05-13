import { useState, useEffect, useCallback } from "react";
import { taskApi } from "./api/api";
import TaskList from "./components/TaskList";
import TaskForm from "./components/TaskForm";
import FilterBar from "./components/FilterBar";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ status: "", priority: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(null); // task being edited, or null

  // useCallback memoises fetchTasks so it's stable across renders.
  // Without this, passing fetchTasks as a prop would cause infinite re-fetches.
  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      const data = await taskApi.getAll(params);
      setTasks(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Re-fetch whenever filters change
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleCreate = async (formData) => {
    await taskApi.create(formData);
    fetchTasks(); // refresh the list
  };

  const handleUpdate = async (id, formData) => {
    await taskApi.update(id, formData);
    setEditing(null);
    fetchTasks();
  };

  const handleStatusToggle = async (task) => {
    const next = task.status === "done" ? "todo" : "done";
    await taskApi.update(task.id, { status: next });
    fetchTasks();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this task?")) return;
    await taskApi.remove(id);
    fetchTasks();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Task Manager</h1>
        <span className="total-badge">{total} tasks</span>
      </header>

      <TaskForm
        onSubmit={editing ? (d) => handleUpdate(editing.id, d) : handleCreate}
        initialData={editing}
        onCancel={() => setEditing(null)}
      />

      <FilterBar filters={filters} onChange={setFilters} />

      {error && <p className="error-msg">{error}</p>}
      {loading && <p className="loading-msg">Loading…</p>}

      {!loading && !error && (
        <TaskList
          tasks={tasks}
          onEdit={setEditing}
          onDelete={handleDelete}
          onToggleStatus={handleStatusToggle}
        />
      )}
    </div>
  );
}
