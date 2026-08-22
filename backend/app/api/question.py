import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.question import QuestionRequest
from app.services.ai.ollama_chat import stream_answer
from app.services.retrieval.retriever import retrieve_similar_chunks
from app.services.source_formatter import build_sources


router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)


@router.post("")
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
):
    chunks = await retrieve_similar_chunks(
        question=request.question,
        db=db,
    )

    async def generate():
        # ---------------------------------------------------------
        # No relevant context
        # ---------------------------------------------------------
        if not chunks:
            yield json.dumps(
                {
                    "type": "answer",
                    "content": (
                        "I could not find relevant information "
                        "in the documents."
                    ),
                }
            ) + "\n"

            yield json.dumps(
                {
                    "type": "sources",
                    "sources": [],
                }
            ) + "\n"

            return

        # ---------------------------------------------------------
        # Build context for the LLM
        # ---------------------------------------------------------
        context = "\n\n".join(
            chunk.content
            for chunk, _ in chunks
        )

        # ---------------------------------------------------------
        # Stream answer tokens
        # ---------------------------------------------------------
        async for token in stream_answer(
            question=request.question,
            context=context,
        ):
            yield json.dumps(
                {
                    "type": "answer",
                    "content": token,
                }
            ) + "\n"

        # ---------------------------------------------------------
        # Send sources after the answer finishes
        # ---------------------------------------------------------
        sources = build_sources(chunks)

        yield json.dumps(
            {
                "type": "sources",
                "sources": sources,
            }
        ) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )