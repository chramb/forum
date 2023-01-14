from typing import Optional
import jwt
from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor

from util.database import connection
from util.auth import AuthHandler

router = APIRouter()
templates = Jinja2Templates(directory="templates")
auth_handler = AuthHandler()


@router.get("/", response_class=HTMLResponse, tags=['Website'])
def web_get(request: Request, access_token: Optional[str] | None = Cookie(None)):
    if access_token:
        account_uid = None
        try:
            token = jwt.decode(access_token, AuthHandler.secret, AuthHandler.jwt_algorithm)

            # Get UID from cookie
            account_uid = token['sub']

            # Get username from DB
            with connection.cursor() as crsr:
                crsr.execute("""
                    select a.username, a.uid
                    from account a
                    where a.uid = %s
                """, (account_uid,))
                db_user = crsr.fetchall()
                if len(db_user) < 0:
                    print("User doesn't exist")
                else:
                    user = {"username": db_user[0][0], "uid": db_user[0][1]}
                    return templates.TemplateResponse("index.html", {"request": request, "user": user})
                    user = db_user[0]

        except jwt.ExpiredSignatureError:
            return RedirectResponse("/login", 303)
            pass
        except jwt.InvalidTokenError:
            print("Invalid cookie")
            pass

    # print("user logged in"), "username:" username
    return templates.TemplateResponse("index.html", {"request": request})
