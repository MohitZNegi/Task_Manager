const PRIORITY_COLOURS = { low: "#10b981", medium: "#f59e0b", high: "#ef4444" };

export default function TaskCard({ task, onEdit, onDelete, onToggleStatus }) {
  return (
    <div className={`task-card task-card--${task.status}`}>
      <div className="task-card__left">
        {/* Checkbox toggles status between todo and done */}
        <input
          type="checkbox"
          checked={task.status === "done"}
          onChange={() => onToggleStatus(task)}
          aria-label={`Mark ${task.title} as ${task.status === "done" ? "incomplete" : "done"}`}
        />
        <div>
          <p className={`task-title ${task.status === "done" ? "done" : ""}`}>
            {task.title}
          </p>
          {task.description && <p className="task-desc">{task.description}</p>}
        </div>
      </div>

      <div className="task-card__right">
        <span
          className="priority-badge"
          style={{ color: PRIORITY_COLOURS[task.priority] }}
        >
          {task.priority}
        </span>
        <span className={`status-badge status-badge--${task.status}`}>
          {task.status.replace("_", " ")}
        </span>
        <button onClick={() => onEdit(task)} className="btn-icon" title="Edit">
          ✏️
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="btn-icon btn-icon--danger"
          title="Delete"
        >
          🗑️
        </button>
      </div>
    </div>
  );
}
