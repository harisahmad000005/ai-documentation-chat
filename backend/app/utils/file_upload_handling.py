from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_UPLOAD_SIZE_MB,
)
from app.models.document import Document, DocumentStatus
from app.services.storage_service import StorageService


MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_file(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {extension}",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type: {file.content_type}",
        )

    return extension


async def save_document(
    document_id: UUID,
    file: UploadFile,
    extension: str,
    storage_service: StorageService,
):
    file_path, file_size, file_hash = await storage_service.save(
        document_id=document_id,
        extension=extension,
        upload_file=file,
    )

    if file_size > MAX_UPLOAD_SIZE:
        storage_service.delete(document_id)

        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {MAX_UPLOAD_SIZE_MB} MB",
        )

    return file_path, file_size, file_hash


async def check_duplicate(
    db: AsyncSession,
    file_hash: str,
):
    existing_document = await db.scalar(
        select(Document).where(
            Document.file_hash == file_hash
        )
    )

    if existing_document:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A document with the same content already exists",
        )


def create_document(
    document_id: UUID,
    file: UploadFile,
    extension: str,
    file_size: int,
    file_hash: str,
    file_path: Path,
    storage_service: StorageService,
) -> Document:

    return Document(
        id=document_id,
        filename=f"original{extension}",
        original_filename=Path(file.filename).name,
        file_type=file.content_type,
        file_size=file_size,
        file_hash=file_hash,
        storage_path=str(
            file_path.relative_to(
                storage_service.storage_dir.parent.parent
            )
        ),
        status=DocumentStatus.UPLOADED,
    )