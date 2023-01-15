from pydantic import BaseModel


class Post(BaseModel):
    title: str
    tag: str
    content: str
