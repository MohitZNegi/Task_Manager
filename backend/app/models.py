from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base


class Priority(str, enum.Enum):
    """
    Using Python enums for constrained columns.
    str mixin means FastAPI serialises these as plain strings in JSON,
    not as {"_value_": "high"} objects.
    """
    low    = "low"
    medium = "medium"
    high   = "high"


class Status(str, enum.Enum):
    todo       = "todo"
    in_progress = "in_progress"
    done       = "done"


class Task(Base):
    """
    Each attribute = one database column.
    SQLAlchemy maps SELECT/INSERT/UPDATE/DELETE to Python method calls.
    You never write raw SQL for basic operations.
    """
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status      = Column(Enum(Status),   default=Status.todo,    nullable=False)
    priority    = Column(Enum(Priority), default=Priority.medium, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    # server_default=func.now() sets the default IN the database, not in Python.
    # This is more reliable — the DB clock is always consistent.
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"