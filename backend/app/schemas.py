from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from app.models import Status, Priority


class TaskBase(BaseModel):
    """
    Shared fields between create and update.
    Field() adds validation rules AND generates documentation
    in Swagger UI automatically — no extra work needed.
    """
    title: str = Field(..., min_length=1, max_length=200,
                       description="Task title")
    description: Optional[str] = Field(None, max_length=1000)
    status: Status   = Status.todo
    priority: Priority = Priority.medium

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank or whitespace only")
        return v.strip()


class TaskCreate(TaskBase):
    """
    What the client sends in the POST /tasks request body.
    Only the fields the user provides — id and timestamps are set by the DB.
    """
    pass   # inherits everything from TaskBase


class TaskUpdate(BaseModel):
    """
    All fields optional — PATCH semantics.
    The client only sends what they want to change.
    """
    title:       Optional[str]     = Field(None, min_length=1, max_length=200)
    description: Optional[str]     = Field(None, max_length=1000)
    status:      Optional[Status]   = None
    priority:    Optional[Priority] = None


class TaskResponse(TaskBase):
    """
    What the API sends back. Includes DB-generated fields.
    model_config with from_attributes=True lets Pydantic read
    SQLAlchemy ORM objects directly (e.g. TaskResponse.model_validate(task)).
    """
    id:          int
    is_archived: bool
    created_at:  datetime
    updated_at:  Optional[datetime] = None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Paginated list wrapper — best practice for list endpoints."""
    items: list[TaskResponse]
    total: int
    page:  int
    size:  int