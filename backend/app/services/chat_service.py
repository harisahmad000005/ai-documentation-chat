import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.schemas.chat import ChatCreate


async def create_chat(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: ChatCreate,
) -> Chat:
    chat = Chat(
        user_id=user_id,
        title=data.title,
    )

    db.add(chat)

    await db.commit()
    await db.refresh(chat)

    return chat


async def get_user_chats(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[Chat]:
    result = await db.execute(
        select(Chat).where(Chat.user_id == user_id).order_by(Chat.created_at.desc())
    )

    return list(result.scalars().all())


async def get_chat(
    db: AsyncSession,
    user_id: uuid.UUID,
    chat_id: uuid.UUID,
) -> Chat | None:
    result = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()


async def delete_chat(
    db: AsyncSession,
    user_id: uuid.UUID,
    chat_id: uuid.UUID,
) -> bool:
    chat = await get_chat(db, user_id, chat_id)

    if chat is None:
        return False

    await db.delete(chat)
    await db.commit()

    return True
