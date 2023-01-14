from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor

from util.database import connection
from util.auth import AuthHandler

auth_handler = AuthHandler()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, tags=['Website'])
def web_login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=RedirectResponse, tags=['Website'])
def web_login_post(request: Request, username: str = Form(), password: str = Form()):
    db_account = None
    errors = []
    with connection.cursor(cursor_factory=RealDictCursor) as curr:
        curr.execute("""
            select a.uid, a.password from account a
             where a.username = %s;
        """, (username,))
        db_account = curr.fetchall()
    if not db_account or not auth_handler.password_verify(password, db_account[0]['password']):
        errors.append("Invalid username and/or password.")
        return templates.TemplateResponse("login.html", {"request": request, "errors": errors})
#    if not errors:
#        response = RedirectResponse("/", status_code=303)
#        jwt_token = auth_handler.token_encode(db_account[0]['uid'])
#        response.set_cookie(key="access_token", value=f"{jwt_token}", httponly=True)
#        return response
