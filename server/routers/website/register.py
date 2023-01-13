import re

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from util.database import connection

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, tags=['website'])
async def web_register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse, tags=['Website'])
def web_register_post(request: Request, username: str = Form(), email: str = Form(), password: str = Form()):
    errors = []
    print(username)
    if not bool(re.match("^[A-Za-z0-9_-]*$", username)):
        errors.append("Username contains illegal characters, only letters digits, dashes and underscores are allowed")
    if len(username) > 32:
        errors.append("Username too long, maximum 32 characters allowed")
    if len(email) > 128:
        errors.append("Address email too long, maximum 128 characters allowed")
    if len(password) < 12:
        errors.append("Password too short, you can do better than that")
    if len(errors) > 0:
        print(errors)
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

    with connection.cursor() as curr:
        # Get all users with the same username or email
        curr.execute("""
            select a.username, a.email from account a
            where a.username = %s or a.email = %s;
        """, (username, email))
        response = curr.fetchall()
        if len(response) > 0:
            errors.append("User this username and/or email already exists.")
            return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

        # Create user
        curr.execute("""
            call account_register(
                username := %s, 
                password := %s, 
                email := %s);
        """, (username, password, email))
        # catch error: account with this username or email already exists
    return {"msg": "account created successfully"}
