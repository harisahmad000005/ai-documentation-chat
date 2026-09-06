from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.database.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserCreate,
    UserResponse,
    RefreshTokenRequest
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    email = data.email.strip().lower()

    result = await db.execute(
        select(User).where(User.email == email),
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        email=email,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    settings = get_settings()

    email = form_data.username.strip().lower()

    result = await db.execute(
        select(User).where(User.email == email),
    )

    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Short-lived access token
    access_token = create_access_token(
        user_id=user.id,
    )

    # Long-lived refresh token
    refresh_token = create_refresh_token()

    # Store only the hash in the database
    refresh_token_hash = hash_refresh_token(
        refresh_token,
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days,
    )

    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
    )

    db.add(db_refresh_token)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    token_hash = hash_refresh_token(
        data.refresh_token,
    )

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
        ),
    )

    refresh_token = result.scalar_one_or_none()

    if refresh_token is not None and refresh_token.revoked_at is None:
        refresh_token.revoked_at = datetime.now(timezone.utc)

        await db.commit()


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user
