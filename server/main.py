#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI,  Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from util.database import connection as conn

from routes.root.base import base_router

app = FastAPI()
security = HTTPBasic()

app.include_router(base_router)


@app.get("/tag/{tag}")
def print_tag(tag: str):
    return {"tag": tag}


@app.get("/account/status")
async def get_account_status(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password, "status": "TODO"}


@app.get("/db_version")
async def get_db_version():
    curr = conn.cursor()
    curr.execute("SELECT version()")
    version = curr.fetchone()
    return {"version": version[0]}


@app.get("/admin/user")
async def get_users():
    curr = conn.cursor()
    curr.execute("""
    select json_agg(t) from 
      (select account_uid, account_username,account_email ,account_status from account) as t;
    """)
    users = curr.fetchone()[0]
    return {"user": users}


@app.get("/admin/user/{username}")
async def get_user(username: str):
    curr = conn.cursor()
    curr.execute("""
    select json_agg(t) from 
    (select account_uid, account_username,account_email ,account_status from account where account_username = %s) as t;
    """, (username,))
    # TODO: convert ^^ into view
    user = curr.fetchone()[0]
    return {"user": user}


if __name__ == "__main__":
    uvicorn.run(app)
