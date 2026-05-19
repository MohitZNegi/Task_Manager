from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from app.models import Status, Priority


# ── Auth schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """What the client sends to register."""
    email:    EmailStr             # Pydantic validates email format automatically
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8,
                          description="At least 8 characters")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, _ and -")
        return v.lower()


class UserLogin(BaseModel):
    """What the client sends to log in."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="At least 8 characters")


class UserResponse(BaseModel):
    """What the API returns — never includes the password hash."""
    id:         int
    email:      str
    username:   str
    is_active:  bool
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace(" ", "T"))
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """
    The response body for a successful login.
    access_token is the signed JWT string.
    token_type is always "bearer" — this is the OAuth2 convention.
    """
    access_token: str
    token_type:   str = "bearer"


class TokenData(BaseModel):
    """
    The decoded contents of a JWT payload.
    sub (subject) is the standard JWT claim for the user identifier.
    Used internally by get_current_user() — never sent to the client.
    """
    user_id: Optional[int] = None


# ── Task schemas (unchanged from Project 2) ───────────────────────────────────

class TaskBase(BaseModel):
    title:       str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status:      Status   = Status.todo
    priority:    Priority = Priority.medium

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title:       Optional[str]      = Field(None, min_length=1, max_length=200)
    description: Optional[str]      = Field(None, max_length=1000)
    status:      Optional[Status]   = None
    priority:    Optional[Priority] = None

class TaskResponse(TaskBase):
    id:          int
    is_archived: bool
    created_at:  datetime
    updated_at:  Optional[datetime] = None
    user_id:     int

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_task_created_at(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace(" ", "T"))
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    @field_validator("updated_at", mode="before")
    @classmethod
    def parse_task_updated_at(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace(" ", "T"))
            except ValueError:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page:  int
    size:  int
