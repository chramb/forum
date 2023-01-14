import re

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor

from models.account import AccountRegister, AccountLogin
from util.auth import AuthHandler
from util.database import connection

router = APIRouter()
auth_handler = AuthHandler()


@router.get("/api/v0/account/@{username}", tags=['API'])
def account_get_by_username(username: str):
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
def account_get_by_uid(uid: str):
    # TODO: switch to with connection syntax
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


@router.post("/api/v0/account/register", tags=['API'])
def account_register_post(user: AccountRegister):
    errors = account_register(user.username, user.email, user.password)
    if not errors:
        return {"detail": "user created"}
    else:
        raise HTTPException(status_code=400, detail=errors)
    # TODO: return the new user json in the future


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
            select a.username, a.email,a.password from account a
            where a.username = %s or a.email = %s;
        """, (username, email))  # TODO: improve query to just return bool
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
        """, (username, auth_handler.password_hash(password), email))
        connection.commit()
    print(f"user {username}, should be in DB")
    return


@router.post("/api/v0/account/login", tags=['TODO'])
def account_login_post(account: AccountLogin):
    # TODO:
    # 1. check if user with that username exists and get his password
    # 2. check if password matches
    # 3. return token
    with connection.cursor(cursor_factory=RealDictCursor) as curr:
        curr.execute("""
            select a.uid, a.password from account a
             where a.username = %s;
        """, (account.username,))
        db_account = curr.fetchall()
        if not db_account or not auth_handler.password_verify(account.password, db_account[0]['password']):
            raise HTTPException(status_code=401, detail="Invalid username and/or password")

        token = auth_handler.token_encode(db_account[0]['uid'])
        return {"token": token}


@router.get("/protected", tags=['TODO'])
def test_auth(uuid=Depends(auth_handler.auth_wrapper)):
    return {"uuid": uuid}
