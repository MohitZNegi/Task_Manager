import { useState, useEffect } from "react";

const EMPTY = { title: "", description: "", priority: "medium" };

export default function TaskForm({ onSubmit, initialData, onCancel }) {
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  // When editing starts, populate the form with existing task data
  useEffect(() => {
    setForm(
      initialData
        ? {
            title: initialData.title,
            description: initialData.description || "",
            priority: initialData.priority,
          }
        : EMPTY,
    );
  }, [initialData]);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) {
      setErr("Title is required");
      return;
    }
    setBusy(true);
    setErr("");
    try {
      await onSubmit(form);
      setForm(EMPTY);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <h2>{initialData ? "Edit task" : "New task"}</h2>

      {err && <p className="form-error">{err}</p>}

      <input
        type="text"
        name="title"
        placeholder="Task title *"
        value={form.title}
        onChange={handleChange}
        required
      />
      <textarea
        name="description"
        placeholder="Description (optional)"
        value={form.description}
        onChange={handleChange}
        rows={2}
      />
      <select name="priority" value={form.priority} onChange={handleChange}>
        <option value="low">Low priority</option>
        <option value="medium">Medium priority</option>
        <option value="high">High priority</option>
      </select>

      <div className="form-actions">
        {initialData && (
          <button type="button" onClick={onCancel} className="btn-outline">
            Cancel
          </button>
        )}
        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Saving…" : initialData ? "Update" : "Add task"}
        </button>
      </div>
    </form>
  );
}
