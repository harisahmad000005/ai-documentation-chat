import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse
from app.services.chat import (
    create_chat,
    delete_chat,
    get_chat,
    get_user_chats,
)

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    return await create_chat(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "",
    response_model=list[ChatResponse],
)
async def list_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatResponse]:
    return await get_user_chats(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
)
async def get(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    chat = await get_chat(
        db=db,
        user_id=current_user.id,
        chat_id=chat_id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    return chat


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await delete_chat(
        db=db,
        user_id=current_user.id,
        chat_id=chat_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
