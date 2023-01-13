import re

from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor

from models.account import AccountRegister, AccountLogin
from util.database import connection

router = APIRouter()


@router.get("/api/v0/account/@{username}", tags=['API'])
async def account_get_by_username(username: str):
    curr = connection.cursor(cursor_factory=RealDictCursor)
    curr.execute("""
    select a.username, a.email, a.uid,
        a.time_created::date as date_registered,
        array_agg(r.title) as roles
    from account a
    left join account_role ar on a.uid = ar.account_uid
    left join role r on r.id = ar.role_id
    where a.username = %s
    group by a.username, a.email, a.uid, a.time_created::date
    """, (username,))
    # noinspection DuplicatedCode
    result = curr.fetchall()

    len_result = len(result)
    if len_result < 1:
        raise HTTPException(
            status_code=404,
            detail=f"user with username: {username} not found."
        )
    elif len_result == 1:
        return result[0]
    elif len_result > 1:
        raise HTTPException(
            status_code=500,
            detail="Database error, more than one user with that username."
        )


@router.get("/api/v0/account/{uid}", tags=['API'])
async def account_get_by_uid(uid: str):
    curr = connection.cursor(cursor_factory=RealDictCursor)
    curr.execute("""
    select a.username, a.email, a.uid,
        a.time_created::date as date_registered,
        array_agg(r.title) as roles
    from account a
    left join account_role ar on a.uid = ar.account_uid
    left join role r on r.id = ar.role_id
    where a.uid = %s
    group by a.username, a.email, a.uid, a.time_created::date
    """, (uid,))
    # noinspection DuplicatedCode
    result = curr.fetchall()

    len_result = len(result)
    if len_result < 1:
        raise HTTPException(
            status_code=404,
            detail=f"user with id: {uid} not found."
        )
    elif len_result == 1:
        return result[0]
    elif len_result > 1:
        raise HTTPException(
            status_code=500,
            detail="Database error, more than one user with that username."
        )


@router.post("/api/v0/account/register", tags=['TODO'])
async def account_register_post(user: AccountRegister):
    return user


@router.post("/api/v0/account/login", tags=['TODO'])
async def account_login_post(user: AccountLogin):
    return AccountLogin


def account_register(username: str, email: str, password: str):
    errors = []
    if not bool(re.match("^[A-Za-z0-9_-]*$", username)):
        errors.append("Username contains illegal characters, only letters digits, dashes and underscores are allowed")
    if len(username) > 32:
        errors.append("Username too long, maximum 32 characters allowed")
    if len(email) > 128:
        errors.append("Address email too long, maximum 128 characters allowed")
    if len(password) < 12:
        errors.append("Password too short, you can do better than that (at least 12 characters)")
    if len(errors) > 0:
        print(errors)
        return errors

    with connection.cursor() as curr:
        # Get all users with the same username or email
        curr.execute("""
            select a.username, a.email from account a
            where a.username = %s or a.email = %s;
        """, (username, email))
        response = curr.fetchall()
        if len(response) > 0:
            errors.append("User this username and/or email already exists.")
            return errors

        # Create user
        curr.execute("""
            call account_register(
                username := %s, 
                password := %s, 
                email := %s);
        """, (username, password, email))
        # catch error: account with this username or email already exists
    return None
