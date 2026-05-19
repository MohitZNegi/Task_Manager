const PRIORITY_COLOURS = { low: "#10b981", medium: "#f59e0b", high: "#ef4444" };

function EditIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M13.586 2.586a2 2 0 0 1 2.828 2.828l-9.5 9.5a1 1 0 0 1-.464.263l-3.5 1a1 1 0 0 1-1.237-1.237l1-3.5a1 1 0 0 1 .263-.464l9.5-9.5ZM12.172 4 4.2 11.972l-.57 1.996 1.996-.57L13.586 5.414 12.172 4Z" />
    </svg>
  );
}

function TrashIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M7 2a1 1 0 0 0-1 1v1H3.75a.75.75 0 0 0 0 1.5h.594l.78 10.14A2 2 0 0 0 7.12 18h5.76a2 2 0 0 0 1.996-1.86l.78-10.14h.594a.75.75 0 0 0 0-1.5H14V3a1 1 0 0 0-1-1H7Zm1 3.5a.75.75 0 0 1 .75.75v8a.75.75 0 0 1-1.5 0v-8A.75.75 0 0 1 8 5.5Zm4 .75a.75.75 0 0 0-1.5 0v8a.75.75 0 0 0 1.5 0v-8Z" />
    </svg>
  );
}

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
          <EditIcon width="18" height="18" />
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="btn-icon btn-icon--danger"
          title="Delete"
        >
          <TrashIcon width="18" height="18" />
        </button>
      </div>
    </div>
  );
}
