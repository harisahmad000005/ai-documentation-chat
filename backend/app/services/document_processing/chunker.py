from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.document_processing.chunk import DocumentChunk


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ],
)


def _extract_page_number(text: str) -> int | None:
    """Extract the page number from a chunk."""

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("[Page ") and line.endswith("]"):
            try:
                return int(
                    line.removeprefix("[Page ").removesuffix("]")
                )
            except ValueError:
                return None

    return None


def chunk_document(
    text: str,
    *,
    document_id: str,
    filename: str,
) -> list[DocumentChunk]:
    """Split document text into chunks with metadata."""

    if not text.strip():
        raise ValueError("Cannot chunk empty document text.")

    chunks = text_splitter.split_text(text)

    document_chunks: list[DocumentChunk] = []

    for index, content in enumerate(chunks):
        metadata = {
            "document_id": document_id,
            "filename": filename,
        }

        page_number = _extract_page_number(content)

        if page_number is not None:
            metadata["page"] = page_number

        document_chunks.append(
            DocumentChunk(
                content=content,
                chunk_index=index,
                metadata=metadata,
            )
        )

    return document_chunks