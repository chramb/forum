#!/usr/bin/env python3

import uvicorn

from fastapi import FastAPI

from routers.api.v0 import account
from routers.website import index
from routers.website import register

app = FastAPI()

app.include_router(account.router)
app.include_router(index.router)
app.include_router(register.router)

if __name__ == "__main__":
    uvicorn.run(app)
