from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services.ai.ollama_embeddings import generate_embedding
from app.services.chunking import split_text
from app.services.document_processing.extractor import extract_document


async def process_document(
    document: Document,
    db: AsyncSession,
) -> None:
    """
    Extract, chunk, embed, and store a document.

    Each chunk keeps its source metadata such as:
    - page number
    - line start
    - line end
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

        # ---------------------------------------------------------
        # 1. Extract document
        # ---------------------------------------------------------
        extracted_document = extract_document(file_path)

        if not extracted_document:
            raise ValueError(
                "Document contains no extractable text."
            )

        # ---------------------------------------------------------
        # 2. Split document into chunks
        # ---------------------------------------------------------
        chunks = split_text(extracted_document)

        if not chunks:
            raise ValueError(
                "Document produced no chunks."
            )

        # ---------------------------------------------------------
        # 3. Remove old chunks
        #
        # This is important when re-processing the same document.
        # Otherwise every test/re-processing would create duplicates.
        # ---------------------------------------------------------
        await db.execute(
            DocumentChunk.__table__.delete().where(
                DocumentChunk.document_id == document.id
            )
        )

        # ---------------------------------------------------------
        # 4. Generate embeddings and create chunk records
        # ---------------------------------------------------------
        for index, chunk_data in enumerate(chunks):

            # DocumentChunkData contains metadata + actual text.
            chunk_text = chunk_data.content

            if not chunk_text.strip():
                continue

            # Generate embedding ONLY from the actual text.
            embedding = generate_embedding(chunk_text)

            if len(embedding) != 768:
                raise ValueError(
                    f"Expected embedding dimension 768, "
                    f"got {len(embedding)}."
                )

            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                metadata_={
                    "source": document.original_filename,
                    "page": chunk_data.page,
                    "line_start": chunk_data.line_start,
                    "line_end": chunk_data.line_end,
                },
                embedding=embedding,
            )

            db.add(chunk)

        # ---------------------------------------------------------
        # 5. Mark document as ready
        # ---------------------------------------------------------
        document.status = DocumentStatus.READY

        await db.commit()

    except Exception as exc:
        await db.rollback()

        # Refresh the document after rollback because SQLAlchemy
        # expires the current transaction state.
        document = await db.get(
            Document,
            document.id,
        )

        if document is not None:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)

            await db.commit()

        raise