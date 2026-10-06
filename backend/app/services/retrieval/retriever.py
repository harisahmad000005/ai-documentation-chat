from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TOP_K,
)
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services.ai.ollama_embeddings import generate_embedding


async def retrieve_similar_chunks(
    question: str,
    db: AsyncSession,
    user_id: UUID,
    document_id: UUID | None = None,
    top_k: int = DEFAULT_TOP_K,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> list[tuple[DocumentChunk, float]]:
    """
    Retrieve relevant document chunks belonging only to the given user
    using pgvector cosine similarity.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    if not 0 <= similarity_threshold <= 1:
        raise ValueError("similarity_threshold must be between 0 and 1.")

    # 1. Generate embedding for the question
    query_embedding = generate_embedding(question)

    # 2. Calculate cosine distance
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    # 3. Build user-scoped vector search
    query = (
        select(
            DocumentChunk,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            Document.user_id == user_id,
            Document.status == DocumentStatus.READY,
        )
        .order_by(distance)
        .limit(top_k)
    )

    # 4. Further restrict to a specific document if provided
    if document_id is not None:
        query = query.where(DocumentChunk.document_id == document_id)

    # 5. Execute vector search
    result = await db.execute(query)

    results = []

    for chunk, chunk_distance in result.all():
        similarity = 1 - float(chunk_distance)

        if similarity >= similarity_threshold:
            results.append((chunk, similarity))

    return results
