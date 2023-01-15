from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor

from models.post import PostCreate
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
                p.last_update is null as edited,
                json_agg(comments_get(c.id)) as comments
            from post p
                     join account a on a.uid = p.creator_uid
                     join comment c on p.id = c.post_id where response_for is null
            group by p.id, a.username, p.title, c.creation_date, c.score order by c.creation_date, c.score
            limit %s;
        """, (limit,))
        posts = crsr.fetchall()
        return posts[0]


@router.post("/api/v0/post/", status_code=201, tags=['Post'])
def post_create(post: PostCreate, jwt=Depends(oauth2_scheme)):
    account_uid = auth_handler.token_decode(jwt)
    with connection.cursor() as crsr:
        # TODO: !!! Validate lengths of post
        crsr.execute("""
            select count(*) > 0
            from account
            where uid = %s
        """, (account_uid,))
        if crsr.fetchall()[0][0]:  # fetchall should return [[ True ]]

            crsr.execute("""
                call create_post(
                    user_uid := %s,
                    title := %s,
                   tag := %s,
                  content := %s
        );""", (account_uid, post.title, post.tag, post.content))
        connection.commit()
    # TODO: validate lengths in model
    return {"details": "post successfully created"}  # TODO: return created post from db


@router.get("/api/v0/post/{id}", tags=['Post'])
def post_get(id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select
                p.id,
                json_build_object(
                        'uid', p.creator_uid,
                        'username', a.username
                    ) as author,
                p.title,
                p.creation_date,
                p.last_update is null as edited,
                json_agg(comments_get(c.id)) as comments
            from post p
                join account a on a.uid = p.creator_uid
                join comment c on p.id = c.post_id 
                where c.response_for is null 
                    and p.id = %s
            group by p.id, a.username, p.title, c.creation_date, c.score order by c.creation_date, c.score
        """, (id,))
        posts = crsr.fetchall()[0]
    return posts


@router.put("/api/v0/post/{id}", tags=['TODO'])
def post_update(id: int, post: PostCreate):
    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
        
        """)


@router.delete("/api/v0/post/", tags=['TODO'])
def post_delete():
    pass
