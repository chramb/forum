#!/usr/bin/env python3

from subprocess import run

from server.util.config import config

cfg = config("server/config.ini")

cmd = f"""
podman run -d \\
       --name forum-db \\
        -e POSTGRES_USER={cfg['user']} \\
        -e POSTGRES_PASSWORD={cfg['password']} \\
        -e POSTGRES_DB={cfg['database']} \\
        -p {cfg['port']}:5432 \\
        -v $PWD/pgdata:/var/lib/postgresql/data:rw,Z \\
    postgres:12-alpine
"""

run(['sh', '-c', cmd])
