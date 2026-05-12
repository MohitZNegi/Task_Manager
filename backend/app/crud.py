from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models import Task, Status, Priority
from app.schemas import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(
    db:       Session,
    status:   Optional[Status]   = None,
    priority: Optional[Priority] = None,
    skip:     int = 0,
    limit:    int = 20,
) -> tuple[list[Task], int]:
    """
    Returns (tasks, total_count) so the response can include pagination info.
    Filters are applied only when provided — optional query params.
    """
    query = db.query(Task).filter(Task.is_archived == False)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    # Count before pagination for the total field
    total = query.with_entities(func.count()).scalar()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    return tasks, total


def create_task(db: Session, task_in: TaskCreate) -> Task:
    """
    model_dump() converts the Pydantic schema to a plain dict.
    ** unpacks it as keyword arguments to the Task constructor.
    This is the standard FastAPI pattern for creating ORM objects from schemas.
    """
    task = Task(**task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)  # refresh loads the DB-generated id and created_at
    return task


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    """
    exclude_unset=True means only fields the client actually sent are updated.
    If the client sends {"status": "done"}, only status changes.
    title, priority etc. are untouched — true PATCH behaviour.
    """
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def archive_task(db: Session, task: Task) -> Task:
    """Soft delete — mark as archived instead of removing from DB."""
    task.is_archived = True
    db.commit()
    db.refresh(task)
    return task