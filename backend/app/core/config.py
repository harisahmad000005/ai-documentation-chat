from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import BASE_DIR


class Settings(BaseSettings):
    app_name: str = "AI Documentation Chat"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"

    admin_username: str
    admin_password: str
    admin_secret_key: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "envs" / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
