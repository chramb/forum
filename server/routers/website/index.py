from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, tags=['Website'])
async def web_get(request: Request):
    return templates.TemplateResponse("index.html",  {"request": request})

@router.get("/login", response_class=HTMLResponse, tags=['Website'])
async def web_get(request: Request):
    return templates.TemplateResponse("login.html",  {"request": request})
