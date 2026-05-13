# Task Manager

Full-stack task management app. FastAPI REST API backend, React frontend, SQLite database.

---

## Architecture

```
frontend (React, port 5173)
    │
    │  HTTP/JSON via Axios
    ▼
backend (FastAPI, port 8000)
    │  ├── Pydantic schemas  — validate every request & response
    │  ├── CRUD layer        — all database logic in one place
    │  └── SQLAlchemy ORM    — Python classes mapped to SQL tables
    │
    │  SQLAlchemy session
    ▼
database (SQLite)
    └── tasks table
```

The frontend and backend are **completely separate processes**. They share no code and communicate only through a documented REST API. This is the separation of concerns that every production web app uses.

---

## Tech stack

| Layer              | Technology        | Why                                                      |
| ------------------ | ----------------- | -------------------------------------------------------- |
| Frontend framework | React 18          | Component model, hooks, fast dev cycle                   |
| HTTP client        | Axios             | Interceptors, base URL config, cleaner than fetch        |
| Backend framework  | FastAPI           | Async, auto-generates Swagger docs, Pydantic-native      |
| Data validation    | Pydantic v2       | Request/response schemas with type enforcement           |
| ORM                | SQLAlchemy 2.x    | Python classes mapped to SQL tables, no raw SQL for CRUD |
| Database           | SQLite            | Production-grade relational DB                           |
| Config             | pydantic-settings | Typed, validated environment variables                   |

---

## What was applied

**Backend**

- `config.py` — pydantic-settings reads `.env` and validates every variable as a typed Python object. Missing variable = crash at startup, not mid-request.
- `database.py` — `get_db()` yields a session per request and always closes it in `finally`. No manual session management in routes.
- `models.py` — Task ORM class with Python enum types for status and priority. `server_default=func.now()` sets timestamps in the database, not Python.
- `schemas.py` — four Pydantic schemas: TaskCreate (what comes in), TaskUpdate (all fields optional for PATCH), TaskResponse (what goes out), TaskListResponse (paginated wrapper).
- `crud.py` — every database operation lives here. Routes never write SQLAlchemy queries directly. `exclude_unset=True` enables true PATCH behaviour.
- `routers/tasks.py` — thin route handlers. `Depends(get_db)` injects the session automatically.
- `main.py` — CORS middleware explicitly allows localhost:5173. Without this the browser blocks all cross-origin requests.

**Frontend**

- `api/api.js` — one Axios instance, one file. All API calls go through here. Response interceptor centralises error handling.
- `App.jsx` — owns all state. `useCallback` memoises fetchTasks so filter changes do not cause infinite re-fetch loops.
- `TaskForm.jsx` — handles both create and edit via a single `onSubmit` prop.
- Controlled components — every form input is driven by useState, not the DOM.

---

## Key routes

| Method | Route                 | Description                                      |
| ------ | --------------------- | ------------------------------------------------ |
| GET    | `/tasks/`             | List tasks, optional status and priority filters |
| POST   | `/tasks/`             | Create a task — returns 201                      |
| GET    | `/tasks/{id}`         | Get one task                                     |
| PATCH  | `/tasks/{id}`         | Partial update — only sent fields change         |
| DELETE | `/tasks/{id}`         | Delete — returns 204 No Content                  |
| PATCH  | `/tasks/{id}/archive` | Soft delete                                      |
| GET    | `/docs`               | Interactive Swagger UI                           |

---

## Quick start

```bash
# SQLite
createdb taskdb

# Backend
cd backend && python -m venv venv  venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```
