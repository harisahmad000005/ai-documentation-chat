from fastapi import FastAPI
from sqladmin import Admin

from app.admin.views import (
    ChatAdmin,
    ChatMessageAdmin,
    DocumentAdmin,
    DocumentChunkAdmin,
    UserAdmin,
)
from app.database.session import engine
from app.admin.auth import AdminAuth


def setup_admin(app: FastAPI) -> Admin:
    authentication_backend = AdminAuth()

    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(DocumentAdmin)
    admin.add_view(DocumentChunkAdmin)
    admin.add_view(ChatAdmin)
    admin.add_view(ChatMessageAdmin)

    return admin