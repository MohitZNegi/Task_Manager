from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Status, Priority, Task, User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.auth import get_current_user
import app.crud as crud

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    status:   Optional[Status]   = Query(None),
    priority: Optional[Priority] = Query(None),
    page:     int = Query(1, ge=1),
    size:     int = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),  # ← added
):
    """
    current_user is injected by FastAPI before this function runs.
    If the token is missing or invalid, FastAPI returns 401 and
    this function is never called.
    We pass current_user.id to CRUD so tasks are scoped to this user.
    """
    skip = (page - 1) * size
    tasks, total = crud.get_tasks(
        db, user_id=current_user.id,   # ← scoped to user
        status=status, priority=priority,
        skip=skip, limit=size,
    )
    return TaskListResponse(items=tasks, total=total, page=page, size=size)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    return crud.create_task(db, task_in, user_id=current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    task = crud.get_task(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    task = crud.get_task(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, task, task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    task = crud.get_task(db, task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task)


@router.get("/auth/me", response_model=None, include_in_schema=False)
def _placeholder(): pass  