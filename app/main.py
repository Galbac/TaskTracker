from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.mount('/static', StaticFiles(directory="app/static"), name="static")

@app.get('/')
async def  home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'title': "Task Tracker"})
