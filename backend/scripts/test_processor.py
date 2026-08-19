from pathlib import Path
import asyncio
import sys

from sqlalchemy import select


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.database.session import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_processing.processor import process_document


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document)
            .order_by(Document.created_at)
            .limit(1)
        )

        document = result.scalar_one_or_none()

        if document is None:
            print("No documents found.")
            return

        print(f"Document: {document.original_filename}")
        print(f"Storage path: {document.storage_path}")
        print(f"Current status: {document.status}")

        await process_document(document, db)

        result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
        )

        chunks = result.scalars().all()

        print()
        print(f"Document status: {document.status}")
        print(f"Number of chunks stored: {len(chunks)}")
        print()

        for chunk in chunks:
            print("=" * 80)
            print(f"CHUNK {chunk.chunk_index}")
            print(f"Characters: {len(chunk.content)}")
            print(f"Embedding dimensions: {len(chunk.embedding)}")
            print("=" * 80)
            print(chunk.content)
            print()


if __name__ == "__main__":
    asyncio.run(main())