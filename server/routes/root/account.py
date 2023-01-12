from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor

from util.database import connection

account_router = APIRouter()


@account_router.get("/account/{uid}")
async def account_get_by_uid(uid: str):
    curr = connection.cursor(cursor_factory=RealDictCursor)
    curr.execute("""
    select a.username, a.email, a.uid,
        a.time_created::date as date_created,
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


async def account_get_by_username(username: str):
    curr = connection.cursor(cursor_factory=RealDictCursor)
    curr.execute("""
    select a.username, a.email, a.uid,
        a.time_created::date as date_created,
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
