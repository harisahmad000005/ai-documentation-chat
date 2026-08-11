from pathlib import Path


def extract_markdown_text(file_path: Path) -> str:
    """Extract text from a Markdown document."""

    return file_path.read_text(
        encoding="utf-8",
    ).strip()