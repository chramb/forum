from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, tags=['Website'])
def web_get(request: Request):
    return templates.TemplateResponse("login.html",  {"request": request})
