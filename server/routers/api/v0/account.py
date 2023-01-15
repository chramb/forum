import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor

from models.account import AccountRegister, AccountLogin
from util.auth import AuthHandler
from util.database import connection

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/account/token")


@router.get("/api/v0/account/@{username}", tags=['Account'])
def account_get_by_username(username: str):
    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select a.username, a.email, a.uid,
                a.time_created::date as date_registered,
                array_agg(r.title) as roles
            from account a
            left join account_role ar on a.uid = ar.account_uid
            left join role r on r.id = ar.role_id
            where a.username = %s
            group by a.username, a.email, a.uid, a.time_created::date
            """, (username,))
        result = crsr.fetchall()

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


@router.get("/api/v0/account/{uid}", tags=['Account'])
def account_get_by_uid(uid: str):
    # TODO: switch to with connection syntax
    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select a.username, a.email, a.uid,
                a.time_created::date as date_registered,
                array_agg(r.title) as roles
            from account a
            left join account_role ar on a.uid = ar.account_uid
            left join role r on r.id = ar.role_id
            where a.uid = %s
            group by a.username, a.email, a.uid, a.time_created::date
            """, (uid,))
        result = crsr.fetchall()

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


@router.post("/api/v0/account/register", status_code=201, tags=['Account'])
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

    with connection.cursor() as crsr:
        # Get all users with the same username or email
        # TODO put both in a procedure (exec multiple from psycopg2 )
        crsr.execute("""
            select a.username, a.email,a.password from account a
            where a.username = %s or a.email = %s;
        """, (username, email))  # TODO: improve query to just return bool
        response = crsr.fetchall()
        if len(response) > 0:
            errors.append("User this username and/or email already exists.")
            return errors

        # Create user
        crsr.execute("""
            call account_register(
                username := %s, 
                password := %s, 
                email := %s);
        """, (username, auth_handler.password_hash(password), email))
        connection.commit()
    return


@router.post("/api/v0/account/token", tags=['Account'])
def account_oauth_login(form_data: OAuth2PasswordRequestForm = Depends()):
    with connection.cursor(cursor_factory=RealDictCursor) as curr:
        curr.execute("""
            select a.uid, a.password from account a
             where a.username = %s;
        """, (form_data.username,))
        db_account = curr.fetchall()
        if not db_account or not auth_handler.password_verify(form_data.password, db_account[0]['password']):
            raise HTTPException(status_code=401, detail="Invalid username and/or password.")

        jwt_token = auth_handler.token_encode(db_account[0]['uid'])
        return {"access_token": jwt_token, "token_type": "bearer"}


@router.put("/api/v0/account/", tags=['Account'])
def account_update(uid: str, account: AccountRegister, jwt=Depends(oauth2_scheme)):
    """
    Note: you can't create users with this request
    """
    # TODO: validate password, email, external function pulled from register ^^
    account_uid = auth_handler.token_decode(jwt)
    if True:
        with connection.cursor(cursor_factory=RealDictCursor) as crsr:
            crsr.execute("""
            select a.uid, a.username, a.email
            from account a 
            where a.username = %s or a.email = %s;
            """, (account.username, account.email))
            existing_accounts = crsr.fetchall()
            if len(existing_accounts) > 0:
                for acc in existing_accounts:
                    if acc['uid'] != account_uid:
                        return HTTPException(status_code=409, detail="username or password already taken")

            hashed_password = auth_handler.password_hash(account.password)
            crsr.execute("""
            update account
                set 
                 email = %s,
                 username = %s,
                 password = %s
                where uid = %s;
            """, (account.email, account.username, hashed_password, account_uid))
            connection.commit()

            return {"detail": "account updated successfully"}

    return HTTPException(status_code=401, detail="account uid doesn't mach authenticated user")


@router.delete("/api/v0/account/{uid}", tags=['Account'])
def account_delete(uid: str, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    if account_uid == uid:
        # TODO: allow role moderator+ to remove users
        with connection.cursor() as crsr:
            crsr.execute("""
            delete from account a where a.uid = %s
            """, (uid,))
            connection.commit()
        return {"detail": "account removed successfully"}
    else:
        return HTTPException(status_code=401, detail="account uid doesn't mach authenticated user")
