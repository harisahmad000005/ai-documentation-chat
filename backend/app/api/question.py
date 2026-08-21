import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.question import QuestionRequest
from app.services.ai.ollama_chat import stream_answer
from app.services.retrieval.retriever import retrieve_similar_chunks


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

    async def generate_response():
        # No relevant context
        if not chunks:
            yield (
                "event: token\n"
                "data: I could not find relevant information "
                "in the documents.\n\n"
            )

            yield (
                "event: sources\n"
                "data: []\n\n"
            )

            yield "event: done\ndata: {}\n\n"

            return

        # Build context for the LLM
        context = "\n\n".join(
            chunk.content
            for chunk, _ in chunks
        )

        # Stream the answer
        async for token in stream_answer(
            question=request.question,
            context=context,
        ):
            yield (
                "event: token\n"
                f"data: {json.dumps(token)}\n\n"
            )

        # Build sources
        sources = []

        for chunk, _ in chunks:
            metadata = chunk.metadata_ or {}

            source = {
                "document": metadata.get("document"),
                "page": metadata.get("page"),
                "line_start": metadata.get("line_start"),
                "line_end": metadata.get("line_end"),
            }

            # Avoid duplicate sources
            if source not in sources:
                sources.append(source)

        # Send sources after the answer
        yield (
            "event: sources\n"
            f"data: {json.dumps(sources)}\n\n"
        )

        # Signal completion
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )