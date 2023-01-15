import re

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routers.api.v0.account import account_register
from util.database import connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, tags=['Website'])
def web_register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse, tags=['Website'])
def web_register_post(request: Request, username: str = Form(), email: str = Form(), password: str = Form()):
    errors = account_register(username, email, password)
    if not errors:
        success_msg = "account created successfully"
        return templates.TemplateResponse("register.html", {"request": request, "success": success_msg})
    else:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})
