export default function FilterBar({ filters, onChange }) {
  const set = (key) => (e) =>
    onChange((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="filter-bar">
      <select value={filters.status} onChange={set("status")}>
        <option value="">All statuses</option>
        <option value="todo">To do</option>
        <option value="in_progress">In progress</option>
        <option value="done">Done</option>
      </select>
      <select value={filters.priority} onChange={set("priority")}>
        <option value="">All priorities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <button
        onClick={() => onChange({ status: "", priority: "" })}
        className="btn-outline"
      >
        Clear
      </button>
    </div>
  );
}
