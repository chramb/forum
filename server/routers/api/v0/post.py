from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor

from models.post import Post
from util.database import connection
from util.auth import AuthHandler

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v0/account/token")


@router.get("/api/v0/posts", tags=['Post'])
def posts_get(limit: Optional[int] = 20):
    if not limit or limit > 50:
        limit = 20

    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select
                p.id as post_id,
                json_build_object(
                    'uid', p.creator_uid,
                    'username', a.username
                    )as author,
                p.title as post_title,
                p.creation_date,
                p.last_update is not null as edited,
                comments_get(p.id) as comments-- TODO: make this not null when no comments
            from post p
                     left join account a on a.uid = p.creator_uid
            limit %s;
        """, (limit,))
        posts = crsr.fetchall()
        if posts:
            return posts
        else:
            return {}


@router.post("/api/v0/post/", status_code=201, tags=['Post'])
def post_create(post: Post, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        # TODO: !!! Validate lengths of post
        crsr.execute("""
            select count(*) > 0
            from post p
            where p.creator_uid = %s and p.title = %s;
        """, (account_uid, post.title))  # user can't make post with same title, spam or sth?
        if not crsr.fetchall()[0][0]:  # fetchall should return [[ True ]]

            crsr.execute("""
                call post_create(
                    author_uid := %s,
                    title := %s,
                   tag := %s,
                  content := %s
                );
        """, (account_uid, post.title, post.tag, post.content))
            connection.commit()
            return {"details": "post successfully created"}
        else:
            raise HTTPException(status_code=400, detail="post with this title already exists from this user.")

    # TODO: validate lengths in model


@router.get("/api/v0/post/{post_id}", tags=['Post'])
def post_get(post_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select
                p.id as post_id,
                json_build_object(
                        'uid', p.creator_uid,
                        'username', a.username
                    ) as author,
                p.title as post_title,
                p.creation_date,
                p.last_update is not null as edited,
                comments_get(p.id) as comments
            from post p
                join account a on a.uid = p.creator_uid
            where p.id = %s;
        """, (post_id,))
        posts = crsr.fetchall()
    if not posts:
        return {}
    else:
        return posts[0]


@router.put("/api/v0/post/{post_id}", tags=['Post'])
def post_update(post_id: int, post: Post, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    # TODO: validate creator uid == auth uid
    with connection.cursor() as crsr:
        crsr.execute("""
            select p.creator_uid
            from post p where p.id = %s;
        """, (post_id,))
        post_author_uid = crsr.fetchone()
        if not post_author_uid:
            return HTTPException(status_code=404, detail="post with given ID not found")

        if post_author_uid[0] != account_uid:
            return HTTPException(status_code=401, detail="unauthorized, you're not the author of this post")

        crsr.execute("""
            call post_update(
                author_uid := %s,
                post_id := %s,
                title := %s,
                tag := %s,
                content := %s
            );
        """, (post_author_uid, post_id, post.title, post.tag, post.content))
        connection.commit()
        return {"detail": "post updated successfully"}


@router.delete("/api/v0/post/{post_id}", tags=['Post'])
def post_delete(post_id: int, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        crsr.execute("""
            select p.creator_uid
            from post p where p.id = %s;
        """, (post_id,))
        post_author_uid = crsr.fetchone()
        if not post_author_uid:
            return HTTPException(status_code=404, detail="post with given ID not found")

        if post_author_uid[0] != account_uid:
            return HTTPException(status_code=401, detail="unauthorized, you're not the author of this post")

        crsr.execute("""
        delete from post p
        where creator_uid = %s
          and p.id = %s;
        """, (post_author_uid, post_id))
        connection.commit()
    return {"detail": "post deleted successfully"}
