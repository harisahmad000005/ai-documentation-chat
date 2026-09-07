import uuid

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
)


async def authenticate_user(
    db: AsyncSession,
    data: LoginRequest,
) -> User:
    email = data.email.strip().lower()

    result = await db.execute(
        select(User).where(User.email == email),
    )

    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        data.password,
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

    return user


def create_token_pair(
    user_id: uuid.UUID,
) -> TokenResponse:
    access_token = create_access_token(
        user_id=user_id,
    )

    refresh_token = create_refresh_token(
        user_id=user_id,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def register_user(
    db: AsyncSession,
    data: UserCreate,
) -> User:
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


async def refresh_tokens(
    db: AsyncSession,
    data: RefreshTokenRequest,
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise credentials_exception

        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = uuid.UUID(subject)

    except (JWTError, ValueError):
        raise credentials_exception from None

    result = await db.execute(
        select(User).where(User.id == user_id),
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return create_token_pair(
        user_id=user.id,
    )