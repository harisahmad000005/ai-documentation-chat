from sqladmin import ModelView

from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.created_at,
    ]

    column_searchable_list = [
        User.email,
    ]


class DocumentAdmin(ModelView, model=Document):
    column_list = [
        Document.id,
        Document.filename,
        Document.file_type,
        Document.file_size,
        Document.status,
        Document.created_at,
    ]


class DocumentChunkAdmin(ModelView, model=DocumentChunk):
    column_list = [
        DocumentChunk.id,
        DocumentChunk.document_id,
        DocumentChunk.created_at,
    ]


class ChatAdmin(ModelView, model=Chat):
    column_list = [
        Chat.id,
        Chat.user_id,
        Chat.title,
        Chat.created_at,
        Chat.updated_at,
    ]


class ChatMessageAdmin(ModelView, model=ChatMessage):
    column_list = [
        ChatMessage.id,
        ChatMessage.chat_id,
        ChatMessage.role,
        ChatMessage.created_at,
    ]
