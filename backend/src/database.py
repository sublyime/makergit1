import os
import asyncpg
from fastapi import FastAPI

# FIXED: Removed hardcoded credentials with a sensitive password.
# Always rely on environment variables for database connections.
# Fallback is set to a standard local dev default without a password.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres@localhost:5432/makergit",
)

async def connect_db(app: FastAPI) -> None:
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

async def close_db(app: FastAPI) -> None:
    pool = getattr(app.state, "db_pool", None)
    if pool is not None:
        await pool.close()

def get_pool(app: FastAPI) -> asyncpg.pool.Pool:
    return app.state.db_pool