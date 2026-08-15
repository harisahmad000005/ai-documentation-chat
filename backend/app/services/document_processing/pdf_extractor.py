from pathlib import Path
import pymupdf


def extract_pdf_text(file_path: Path) -> str:
    """Extract text from a PDF document."""

    text_parts: list[str] = []

    with pymupdf.open(file_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text().strip()

            if text:
                text_parts.append(
                    f"[Page {page_number}]\n{text}"
                )

    return "\n\n".join(text_parts)