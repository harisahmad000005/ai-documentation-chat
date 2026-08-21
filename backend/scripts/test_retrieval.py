from pathlib import Path
import asyncio
import sys

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.database.session import AsyncSessionLocal
from app.models.document import Document
from app.services.retrieval.retriever import retrieve_similar_chunks


async def main() -> None:
    async with AsyncSessionLocal() as db:
        # Get the first document
        result = await db.execute(
            select(Document)
            .order_by(Document.created_at)
            .limit(1)
        )

        document = result.scalar_one_or_none()

        if document is None:
            print("No documents found.")
            return

        question = "What is the company's vacation policy?"

        print(f"Document: {document.original_filename}")
        print(f"Question: {question}")
        print()

        chunks = await retrieve_similar_chunks(
            question=question,
            db=db,
            document_id=document.id,
            top_k=3,
        )

        print(f"Retrieved chunks: {len(chunks)}")
        print()

        for chunk, similarity in chunks:
            print("=" * 80)
            print(f"CHUNK INDEX: {chunk.chunk_index}")
            print(f"COSINE SIMILARITY: {similarity:.4f}")
            print("=" * 80)
            print(chunk.content)
            print()


if __name__ == "__main__":
    asyncio.run(main())