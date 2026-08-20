"""Python-only ManPro dashboard entry point for Render and local use."""
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.main import app

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")
