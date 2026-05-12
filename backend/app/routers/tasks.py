from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Status, Priority
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
import app.crud as crud

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    status:   Optional[Status]   = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    page:     int = Query(1, ge=1),
    size:     int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Depends(get_db) is dependency injection.
    FastAPI calls get_db(), gives this route a live DB session,
    and closes it automatically when the response is sent.
    No manual session management in route handlers.
    """
    skip = (page - 1) * size
    tasks, total = crud.get_tasks(db, status=status, priority=priority,
                                  skip=skip, limit=size)
    return TaskListResponse(items=tasks, total=total, page=page, size=size)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """
    FastAPI automatically reads the request body and validates it
    against TaskCreate. If title is missing or blank, it returns
    422 Unprocessable Entity with a clear error message — no manual
    validation code needed.
    """
    return crud.create_task(db, task_in)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return crud.update_task(db, task, task_in)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    crud.delete_task(db, task)
    # 204 returns no body — don't return anything here


@router.patch("/{task_id}/archive", response_model=TaskResponse)
def archive_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return crud.archive_task(db, task)