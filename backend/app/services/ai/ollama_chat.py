from collections.abc import AsyncGenerator

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from app.core.config import get_settings


settings = get_settings()


chat_model = ChatOllama(
    model=settings.ollama_chat_model,
    base_url=settings.ollama_base_url,
)


async def generate_answer(
    question: str,
    context: str,
) -> str:
    """Generate a complete answer using the provided context."""

    prompt = f"""
You are a documentation assistant.

Answer the user's question using only the provided documentation context.

If the answer cannot be found in the context, say:
"I could not find relevant information in the document."

Do not make up information.

Documentation context:
{context}

User question:
{question}
"""

    response = await chat_model.ainvoke(
        [HumanMessage(content=prompt)]
    )

    return response.content


async def stream_answer(
    question: str,
    context: str,
) -> AsyncGenerator[str, None]:
    """Stream the answer token-by-token."""

    prompt = f"""
You are a documentation assistant.

Answer the user's question using only the provided documentation context.

If the answer cannot be found in the context, say:
"I could not find relevant information in the document."

Do not make up information.

Documentation context:
{context}

User question:
{question}
"""

    async for chunk in chat_model.astream(
        [HumanMessage(content=prompt)]
    ):
        if chunk.content:
            yield chunk.content