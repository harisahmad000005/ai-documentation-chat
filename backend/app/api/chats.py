import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.chat import ChatCreate, ChatResponse
from app.services.chat_service import (
    create_chat,
    delete_chat,
    get_chat,
    get_user_chats,
)

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)