from typing import TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.user import User


class Chat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chats"

    user_id: Mapped["uuid.UUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="chats",
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )
