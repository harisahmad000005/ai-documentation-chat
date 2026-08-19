from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services.ai.ollama_embeddings import generate_embedding
from app.services.chunking import split_text
from app.services.document_processing.extractor import extract_document
from app.core.constants import EMBEDDING_DIMENSION



async def process_document(
    document: Document,
    db: AsyncSession,
) -> None:
    """
    Extract, chunk, embed, and store a document.
    """

    document.status = DocumentStatus.PROCESSING
    document.error_message = None

    await db.flush()

    try:
        file_path = Path(document.storage_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Document file not found: {file_path}"
            )

        # 1. Extract text
        text = extract_document(file_path)

        if not text.strip():
            raise ValueError(
                "Document contains no extractable text."
            )

        # 2. Split text into chunks
        chunks = split_text(text)

        if not chunks:
            raise ValueError(
                "Document produced no chunks."
            )

        # 3. Remove existing chunks before reprocessing
        await db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document.id
            )
        )

        # 4. Generate embeddings and create chunk records
        for index, chunk_text in enumerate(chunks):
            embedding = generate_embedding(chunk_text)

            if len(embedding) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Expected embedding dimension "
                    f"{EMBEDDING_DIMENSION}, "
                    f"got {len(embedding)}."
                )

            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                metadata_={
                    "source": document.original_filename,
                },
                embedding=embedding,
            )

            db.add(chunk)

        # 5. Mark document as ready
        document.status = DocumentStatus.READY

        await db.commit()

    except Exception as exc:
        await db.rollback()

        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)

        await db.commit()

        raise