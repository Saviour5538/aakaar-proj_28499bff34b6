from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from database.models import Task
from database.config import get_db
from backend.services.auth import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks")

# Pydantic schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1000)
    completed: bool = Field(default=False)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    completed: bool | None = None

class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    created_at: str

# Route handlers
@router.post("/", response_model=TaskResponse, operation_id="create_task")
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = Task(
        user_id=current_user["id"],
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/", response_model=List[TaskResponse], operation_id="list_tasks")
async def list_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    tasks = db.query(Task).filter(Task.user_id == current_user["id"]).all()
    return tasks

@router.put("/{id}", response_model=TaskResponse, operation_id="update_task")
async def update_task(
    id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user["id"]).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="delete_task")
async def delete_task(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == id, Task.user_id == current_user["id"]).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return None