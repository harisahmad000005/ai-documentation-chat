from fastapi import FastAPI

from app.api.document import router as documents_router
from app.api.health import router as health_router
from app.api.question import router as questions_router
from app.core.config import get_settings


settings = get_settings()

API_V1_PREFIX = "/api/v1"


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


app.include_router(
    health_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    documents_router,
    prefix=API_V1_PREFIX,
)

app.include_router(
    questions_router,
    prefix=API_V1_PREFIX,
)

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
    }