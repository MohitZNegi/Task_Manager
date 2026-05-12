# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import tasks

# Create all tables on startup (use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Full-stack task manager — Project 2",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI — visit this to test all endpoints
    redoc_url="/redoc",
)

# CORS — allows the React dev server (port 5173) to call this API.
# Without this, the browser blocks cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)


@app.get("/health")
def health_check():
    """Quick check that the API is running."""
    return {"status": "ok", "app": settings.app_name}