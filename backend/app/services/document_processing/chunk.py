from dataclasses import dataclass


@dataclass
class DocumentChunk:
    content: str
    chunk_index: int
    metadata: dict