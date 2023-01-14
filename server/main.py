#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI

from routers.api.v0 import account, post
from routers.website import index, register, login

app = FastAPI()

# API
app.include_router(account.router)
app.include_router(post.router)
# Website
app.include_router(index.router)
app.include_router(register.router)
app.include_router(login.router)

if __name__ == "__main__":
    uvicorn.run(app)
