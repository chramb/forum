from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor

from models.comment import Comment
from util.database import connection
from util.auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/account/token")


@router.get("/api/v0/comment/{comment_id}", tags=['Comment'])
def comment_get(comment_id: int):
    with connection.cursor() as crsr:
        crsr.execute("""
        select comment_get(%s)
        """, (comment_id,))
        comment = crsr.fetchone()[0]
        if not comment:
            raise HTTPException(status_code=404, detail="comment with given id not found.")
        else:
            return comment



@router.post("/api/v0/post/{post_id}/comment", tags=['Comment'])
def comment_post(post_id: int, comment: Comment, jwt=Depends(oauth2_scheme)):
    account_id = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        crsr.execute("""
            select count(*) > 0
            from post p where p.id = %s;
        """, (post_id,))
        if crsr.fetchone()[0]:
            crsr.execute("""
            select * from account;
                call comment_post(
                    creator_uid := %s,
                    post_id := %s,
                    msg := %s)
            """, (account_id, post_id, comment.content))
            connection.commit()
            return {"detail": "comment successfully created."}
        else:
            raise HTTPException(status_code=404, detail="post with given id not found")


@router.post("/api/v0/post/{post_id}/comment/{comment_id}", tags=['Comment'])
def comment_post(post_id: int, comment_id: int, comment: Comment, jwt=Depends(oauth2_scheme)):
    account_id = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        crsr.execute("""
            select count(*) > 0
            from comment c where c.post_id = %s and c.id = %s;
        """, (post_id, comment_id))
        if crsr.fetchone()[0]:
            with connection.cursor() as crsr:
                crsr.execute("""
                select * from account;
                    call comment_post(
                        creator_uid := %s,
                        post_id := %s,
                        msg := %s,
                        respond_to := %s)
                """, (account_id, post_id, comment.content, comment_id))
                connection.commit()
                return {"detail": "comment successfully created."}
        else:
            raise HTTPException(status_code=404, detail="post with given id or comment with given id not found")


@router.put("/api/v0/comment/{comment_id}", tags=['Comment'])
def comment_update(comment_id: int, comment: Comment, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        crsr.execute("select c.creator_uid from comment c where id = %s;", (comment_id,))
        comment_creator_uid = crsr.fetchone()
        if not comment_creator_uid:
            raise HTTPException(status_code=404, detail="comment with given id not found.")
        if comment_creator_uid[0] != account_uid:
            raise HTTPException(status_code=403, detail="this user isn't the author of the comment.")

        crsr.execute("""
            update comment
            set 
              msg = %s,
              last_update = now();
        """, (comment.content,))
        connection.commit()
        return {"detail": "comment updated successfully"}


@router.delete("/api/v0/comment/{comment_id}", tags=['Comment'])
def comment_delete(comment_id: int, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        crsr.execute("select c.creator_uid from comment c where c.id = %s;", (comment_id,))
        comment_creator_uid = crsr.fetchone()
        if not comment_creator_uid:
            raise HTTPException(status_code=404, detail="comment with given id not found.")
        if comment_creator_uid[0] != account_uid:
            raise HTTPException(status_code=403, detail="this user isn't the author of the comment.")

        crsr.execute("delete from comment c where c.id = %s and c.creator_uid = %s;",(comment_id,account_uid))
        connection.commit()

    return {"detail": "comment removed successfully"}
