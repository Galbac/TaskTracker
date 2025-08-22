from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.api.auth import auth_router
from app.api.tasks import task_router
from app.services.kafka_producer import producer
from app.tasks import check_deadlines
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await producer.start()
    """Print("✅ Kafka Producer запущен")"""
    yield
    await producer.stop()
    """Print("✅ Kafka Producer остановлен")"""


app = FastAPI(lifespan=lifespan)


templates = Jinja2Templates(directory="app/templates")
app.templates = templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Task Tracker"}
    )


@app.get("/run-task")
async def run_task():
    check_deadlines.delay()
    return {"message": "Task запущена"}
