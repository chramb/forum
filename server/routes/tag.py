from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor

from util.database import connection

tag_router = APIRouter()

# @tag.route("/tag/{tag}"):
# TODO:
