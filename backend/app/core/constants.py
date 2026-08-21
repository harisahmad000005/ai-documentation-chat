from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

MAX_UPLOAD_SIZE_MB = 20

STORAGE_DIR = BASE_DIR / "storage" / "documents"

ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".md",
    ".markdown",
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
    "text/plain",
}

EMBEDDING_DIMENSION = 768

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

DEFAULT_TOP_K = 5
DEFAULT_SIMILARITY_THRESHOLD = 0.50