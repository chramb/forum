
from fastapi import APIRouter


router = APIRouter()


@router.get("/api/v0/posts", tags=['TODO'])
def posts_get(limit: int, sort_by: str):
    pass


@router.get("/api/v0/post/{id}", tags=['TODO'])
def post_create(id: int):
    pass


@router.get("/api/v0/post/", tags=['TODO'])
def post_create(tag: str):
    pass


@router.post("/api/v0/post/", tags=['TODO'])
def post_create():
    pass


@router.put("/api/v0/post/", tags=['TODO'])
def post_create():
    pass


@router.delete("/api/v0/post/", tags=['TODO'])
def post_create():
    pass
