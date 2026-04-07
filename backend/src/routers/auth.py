from fastapi import APIRouter, Depends, HTTPException, Request, status
from ..database import get_pool
from ..models import LoginRequest, TokenResponse, UserCreate, UserRead, RegisterResponse
from ..utils import create_api_key, get_current_user, get_password_hash, verify_password

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, request: Request):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = $2",
            user.username,
            user.email,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

        password_hash = get_password_hash(user.password)
        api_key = create_api_key()
        row = await conn.fetchrow(
            "INSERT INTO users(username, email, display_name, password_hash, api_key) VALUES ($1, $2, $3, $4, $5) RETURNING id, username, email, display_name, bio, avatar_url, website_url, location, created_at, updated_at, api_key",
            user.username,
            user.email,
            user.display_name,
            password_hash,
            api_key,
        )
        # Convert UUID to string
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        return RegisterResponse(**row_dict)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, request: Request):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT password_hash, api_key FROM users WHERE username = $1 OR email = $1",
            credentials.username,
        )
        if row is None or not verify_password(credentials.password, row["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return TokenResponse(api_key=row["api_key"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user=Depends(get_current_user)):
    user_dict = dict(current_user)
    user_dict['id'] = str(user_dict['id'])
    return UserRead(**user_dict)
