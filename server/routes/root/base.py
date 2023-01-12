from fastapi import APIRouter

from ..account import account_get_by_username

base_router = APIRouter()


@base_router.get("/@{username}")
async def get_user(username: str):
    return await account_get_by_username(username)
