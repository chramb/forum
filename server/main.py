#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI
from fastapi.security import HTTPBasic

from routes.root.account import account_router
from routes.root.base import base_router

app = FastAPI()
security = HTTPBasic()

app.include_router(base_router)
app.include_router(account_router)

if __name__ == "__main__":
    uvicorn.run(app)
