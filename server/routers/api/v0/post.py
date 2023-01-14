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


@router.get("/api/v0/posts", tags=['TODO'])
def posts_get(limit: Optional[int] = 20, sort_by: Optional[str] = "date"):
    if not limit or limit > 50:
        limit = 20
    if not sort_by or sort_by != "date" or sort_by != "popularity":
        sort_by = "date"

    with connection.cursor(cursor_factory=RealDictCursor) as crsr:
        crsr.execute("""
            select
                p.id,
                a.username as author,
                p.title,
                json_agg(comment_get_recursive_json_v2(c.id))
            from post p
            join account a on a.uid = p.creator_uid
            join comment c on p.id = c.post_id where response_for is null
            group by p.id, a.username, p.title, c.creation_date order by c.creation_date;
        """)
        posts = crsr.fetchall()
        return posts[0]


@router.post("/api/v0/post/", status_code=201, tags=['TODO'])
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


@router.get("/api/v0/post/", tags=['TODO'])
def post_create(tag: str):
    pass


@router.put("/api/v0/post/", tags=['TODO'])
def post_create():
    pass


@router.delete("/api/v0/post/", tags=['TODO'])
def post_create():
    pass
