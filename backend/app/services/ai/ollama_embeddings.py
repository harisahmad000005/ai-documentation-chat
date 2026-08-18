from langchain_ollama import OllamaEmbeddings

from app.core.config import get_settings


settings = get_settings()


embedding_model = OllamaEmbeddings(
    model=settings.ollama_embedding_model,
    base_url=settings.ollama_base_url,
)


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text."""

    if not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    return embedding_model.embed_query(text)