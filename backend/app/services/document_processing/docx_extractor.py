from pathlib import Path

from docx import Document


def extract_docx_text(file_path: Path) -> str:
    """Extract text from a DOCX document."""

    document = Document(file_path)

    text_parts: list[str] = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)