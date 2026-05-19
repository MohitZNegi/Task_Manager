from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models import Task, Status, Priority, User
from app.schemas import TaskCreate, TaskUpdate


# ── User helpers ──────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


# ── Task CRUD — all scoped to user_id ─────────────────────────────────────────

def get_task(db: Session, task_id: int, user_id: int) -> Task | None:
    """
    Always filter by both task_id AND user_id.
    This prevents user A from accessing user B's tasks
    even if they guess the correct task ID.
    """
    return db.query(Task).filter(
        Task.id      == task_id,
        Task.user_id == user_id,
    ).first()


def get_tasks(
    db:       Session,
    user_id:  int,
    status:   Optional[Status]   = None,
    priority: Optional[Priority] = None,
    skip:     int = 0,
    limit:    int = 20,
) -> tuple[list[Task], int]:
    query = db.query(Task).filter(
        Task.user_id    == user_id,  
        Task.is_archived == False,
    )
    if status:   query = query.filter(Task.status   == status)
    if priority: query = query.filter(Task.priority == priority)

    total = query.with_entities(func.count()).scalar()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks, total


def create_task(db: Session, task_in: TaskCreate, user_id: int) -> Task:
    task = Task(**task_in.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def archive_task(db: Session, task: Task) -> Task:
    task.is_archived = True
    db.commit()
    db.refresh(task)
    return task