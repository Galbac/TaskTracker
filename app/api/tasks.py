from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, redirect_if_not_authenticated
from app.database import get_db
from app.models.task import Task
from app.schema.task import TaskSchema

task_router = APIRouter()


@task_router.get("/tasks")
async def list_task(request: Request, db: AsyncSession = Depends(get_db)):
    user = await  get_current_user(request, db)
    redirect_if_not_authenticated(user)
    result = await db.execute(select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc()))
    tasks = result.scalars().all()
    return request.app.templates.TemplateResponse(name='task.html',
                                                  context={'request': request, 'tasks': tasks, 'user': user})


@task_router.post("/tasks/add")
async def add_task(request: Request, task: TaskSchema, db: AsyncSession = Depends(get_db)):
    user = await  get_current_user(request, db)
    redirect_if_not_authenticated(user)
    new_task = Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    return RedirectResponse('/tasks', status_code=303)


@task_router.post('/tasks/{task_id}/complete')
async def complete_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    user = await  get_current_user(request, db)
    redirect_if_not_authenticated(user)
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar()
    if task:
        task.is_completed = True
        await db.commit()
    return RedirectResponse('/tasks', status_code=303)


@task_router.post('/tasks/{task_id}/delete')
async def delete_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    redirect_if_not_authenticated(user)
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar()
    if task:
        await db.delete(task)
        await db.commit()
    return RedirectResponse('/tasks', status_code=303)
