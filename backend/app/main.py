from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
from app.config import settings
from app.database import engine, Base
from app.routers import tasks, auth  

def _migrate_sqlite_if_needed() -> None:
    """
    Dev-only migration helper.
    SQLAlchemy's create_all() does NOT alter existing tables, so if the DB file
    was created before adding auth/user scoping, the schema will be missing
    tasks.user_id and task routes will 500.
    """
    url = settings.database_url or ""
    if not url.startswith("sqlite:///"):
        return

    # Example: sqlite:///./taskdb.db
    path = url.replace("sqlite:///", "", 1)
    if path.startswith("./"):
        path = path[2:]

    try:
        con = sqlite3.connect(path)
    except sqlite3.Error:
        return

    try:
        cur = con.cursor()
        cols = [r[1] for r in cur.execute("PRAGMA table_info(tasks)").fetchall()]
        if not cols:
            return
        if "user_id" in cols:
            return

        has_old_rows = cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] > 0
        user_row = cur.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
        default_user_id = user_row[0] if user_row else None

        cur.execute("ALTER TABLE tasks RENAME TO tasks_old")
        cur.execute(
            """
            CREATE TABLE tasks (
              id INTEGER NOT NULL PRIMARY KEY,
              title VARCHAR(200) NOT NULL,
              description VARCHAR(1000),
              status VARCHAR(11) NOT NULL,
              priority VARCHAR(6) NOT NULL,
              is_archived BOOLEAN NOT NULL,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME,
              user_id INTEGER NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users (id)
            )
            """
        )

        if has_old_rows:
            if default_user_id is None:
                # Can't safely attach tasks to a user; drop old rows.
                cur.execute("DROP TABLE tasks_old")
                con.commit()
                return

            cur.execute(
                """
                INSERT INTO tasks(id,title,description,status,priority,is_archived,created_at,updated_at,user_id)
                SELECT id,title,description,status,priority,is_archived,created_at,updated_at,?
                FROM tasks_old
                """,
                (default_user_id,),
            )

        cur.execute("DROP TABLE tasks_old")
        con.commit()
    finally:
        con.close()


_migrate_sqlite_if_needed()

# Create all tables on startup (use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Full-stack task manager — Project 2",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI — visit this to test all endpoints
    redoc_url="/redoc",
    debug=settings.debug,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if settings.debug:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# CORS — allows the React dev server (port 5173) to call this API.
# Without this, the browser blocks cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    # Allow Vite/React dev server origins (localhost/127.0.0.1; any dev port).
    # With allow_credentials=True we cannot use "*" for allow_origins.
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex=r"^http://(localhost|127\\.0\\.0\\.1):\\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router) 
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    """Quick check that the API is running."""
    return {"status": "ok", "app": settings.app_name}
