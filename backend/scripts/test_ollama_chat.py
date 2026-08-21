from pathlib import Path
import asyncio
import sys



ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.ai.ollama_chat import generate_answer



async def main() -> None:
    question = "How do I upload a document?"

    context = """
    ACME PRODUCT MANUAL

    Getting Started

    Sign in, open the Documents page, and upload a PDF,
    DOCX, or Markdown file. The system displays the
    processing status.
    """

    answer = await generate_answer(
        question=question,
        context=context,
    )

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())