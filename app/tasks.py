import asyncio
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.celery_config import celery_app
from app.config import DATABASE_URL
from app.models.task import Task


engine = create_async_engine(DATABASE_URL, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task
def check_deadlines():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_check_deadlines_async())


async def _check_deadlines_async():
    async with async_session() as session:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        upcoming = now + timedelta(days=1)

        result = await session.execute(
            select(Task).where(
                Task.deadline != None,
                Task.is_completed == False,
                Task.deadline <= upcoming,
                Task.deadline > now)
        )

        tasks = result.scalars().all()
        for task in tasks:
            print(f"[🔔] Напоминание: '{task.title}' у пользователя {task.user_id}, дедлайн — {task.deadline}")




