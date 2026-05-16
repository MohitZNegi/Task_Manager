from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class Priority(str, enum.Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

class Status(str, enum.Enum):
    todo        = "todo"
    in_progress = "in_progress"
    done        = "done"


class User(Base):
    """
    Each User owns Tasks. The relationship is one-to-many:
    one user can have many tasks, each task belongs to one user.
    cascade="all, delete-orphan" means deleting a user also
    deletes all their tasks — no orphaned rows.
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    username      = Column(String(80),  unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("Task", back_populates="owner",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status      = Column(Enum(Status),   default=Status.todo,    nullable=False)
    priority    = Column(Enum(Priority), default=Priority.medium, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # FK — every task belongs to one user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner   = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r}>"