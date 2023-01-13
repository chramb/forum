from pydantic import BaseModel


class AccountRegister(BaseModel):
    username: str
    email: str
    password: str

class AccountLogin(BaseModel):
    username: str
    password: str
    # IDEA: allow login with username OR email
