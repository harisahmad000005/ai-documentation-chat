from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.constants import CHUNK_OVERLAP, CHUNK_SIZE


@dataclass
class DocumentChunkData:
    content: str
    page: int | None
    line_start: int
    line_end: int


def split_text(text: str) -> list[DocumentChunkData]:
    """
    Split extracted document text into overlapping chunks while
    preserving page and line information.
    """

    if not text or not text.strip():
        return []

    lines = text.splitlines()

    chunks_with_locations: list[DocumentChunkData] = []

    current_lines: list[str] = []
    current_start_line = 1
    current_page: int | None = None

    for line_number, line in enumerate(lines, start=1):

        # Detect page markers such as:
        # [Page 1]
        # [Page 2]
        if line.startswith("[Page ") and line.endswith("]"):
            try:
                current_page = int(
                    line.removeprefix("[Page ").removesuffix("]")
                )
            except ValueError:
                pass

        if not current_lines:
            current_start_line = line_number

        current_lines.append(line)

        current_text = "\n".join(current_lines)

        if len(current_text) >= CHUNK_SIZE:
            chunks_with_locations.append(
                DocumentChunkData(
                    content=current_text,
                    page=current_page,
                    line_start=current_start_line,
                    line_end=line_number,
                )
            )

            # Preserve overlap by keeping the last few lines.
            overlap_lines: list[str] = []
            overlap_length = 0

            for previous_line in reversed(current_lines):
                if overlap_length + len(previous_line) > CHUNK_OVERLAP:
                    break

                overlap_lines.insert(0, previous_line)
                overlap_length += len(previous_line) + 1

            current_lines = overlap_lines

            if current_lines:
                current_start_line = (
                    line_number - len(current_lines) + 1
                )

    # Store remaining content.
    if current_lines:
        chunks_with_locations.append(
            DocumentChunkData(
                content="\n".join(current_lines),
                page=current_page,
                line_start=current_start_line,
                line_end=len(lines),
            )
        )

    return chunks_with_locations