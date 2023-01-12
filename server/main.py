#!/usr/bin/env python3
import json

import uvicorn
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI,  Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from routes.account import account_router
from routes.root.base import base_router

from util.database import connection as conn


app = FastAPI()
security = HTTPBasic()


app.include_router(base_router)
app.include_router(account_router)


@app.get("/tag/{tag}")
def print_tag(tag: str):
    return {"tag": tag}


@app.get("/account/status")
async def get_account_status(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password, "status": "TODO"}



if __name__ == "__main__":
    uvicorn.run(app)
