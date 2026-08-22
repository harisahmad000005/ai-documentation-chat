from app.models.document_chunk import DocumentChunk


def build_sources(
    chunks: list[tuple[DocumentChunk, float]],
) -> list[dict]:
    """
    Build source information from retrieved document chunks.
    """

    sources = []

    seen = set()

    for chunk, _ in chunks:
        metadata = chunk.metadata_ or {}

        source = (
            metadata.get("source"),
            metadata.get("page"),
            metadata.get("line_start"),
            metadata.get("line_end"),
        )

        if source in seen:
            continue

        seen.add(source)

        sources.append(
            {
                "document": metadata.get("source"),
                "page": metadata.get("page"),
                "line_start": metadata.get("line_start"),
                "line_end": metadata.get("line_end"),
            }
        )

    return sources