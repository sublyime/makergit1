import re
import uuid
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext
from .database import get_pool

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_API_KEY_HEADER = "Authorization"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_api_key() -> str:
    return uuid.uuid4().hex


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or uuid.uuid4().hex


async def get_current_user(request: Request):
    auth_header = request.headers.get(SECRET_API_KEY_HEADER)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    api_key = auth_header.split(" ", 1)[1].strip()
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, username, email, display_name, bio, avatar_url, website_url, location, created_at, updated_at FROM users WHERE api_key = $1",
            api_key,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        return row


async def get_current_user_optional(request: Request):
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
