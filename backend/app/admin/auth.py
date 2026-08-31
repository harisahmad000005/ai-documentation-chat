from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from app.core.config import get_settings


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        settings = get_settings()

        super().__init__(secret_key=settings.admin_secret_key)

        self.username = settings.admin_username
        self.password = settings.admin_password

    async def login(self, request: Request) -> bool:
        form = await request.form()

        username = form.get("username")
        password = form.get("password")

        if username == self.username and password == self.password:
            request.session.update({
                "admin_authenticated": True,
            })
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_authenticated", False)