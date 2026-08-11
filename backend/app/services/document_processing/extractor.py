from pathlib import Path

from .pdf_extractor import extract_pdf_text
from .docx_extractor import extract_docx_text
from .markdown_extractor import extract_markdown_text

EXTRACTORS = {
    ".pdf": extract_pdf_text,
    ".docx": extract_docx_text,
    ".md": extract_markdown_text,
    ".markdown": extract_markdown_text,
}


def extract_document(file_path: Path) -> str:
    """Extract text from a supported document."""

    extension = file_path.suffix.lower()

    extractor = EXTRACTORS.get(extension)

    if extractor is None:
        raise ValueError(
            f"Unsupported document type: {extension}"
        )

    text = extractor(file_path)

    if not text.strip():
        raise ValueError(
            "Document contains no extractable text"
        )

    return text