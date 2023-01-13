from pydantic import BaseModel


class AccountRegister(BaseModel):
    username: str
    email: str
    password: str
