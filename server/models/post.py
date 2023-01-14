from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    tag: str
    content: str
