import os
import asyncpg
from fastapi import FastAPI

# FIXED: Include password in default connection string for local development
# For production, always use environment variables!
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:NatEvan12!!@localhost:5432/makergit",
)

async def connect_db(app: FastAPI) -> None:
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

async def close_db(app: FastAPI) -> None:
    pool = getattr(app.state, "db_pool", None)
    if pool is not None:
        await pool.close()

def get_pool(app: FastAPI) -> asyncpg.pool.Pool:
    return app.state.db_pool