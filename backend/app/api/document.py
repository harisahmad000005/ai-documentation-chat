from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.document import DocumentResponse
from app.services.storage_service import StorageService
from app.utils.file_upload_handling import (
    check_duplicate,
    create_document,
    save_document,
    validate_file,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

storage_service = StorageService()


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    extension = validate_file(file)
    document_id = uuid4()

    try:
        file_path, file_size, file_hash = await save_document(
            document_id=document_id,
            file=file,
            extension=extension,
            storage_service=storage_service,
        )

        await check_duplicate(
            db=db,
            file_hash=file_hash,
        )

        document = create_document(
            document_id=document_id,
            file=file,
            extension=extension,
            file_size=file_size,
            file_hash=file_hash,
            file_path=file_path,
            storage_service=storage_service,
        )

        db.add(document)

        await db.commit()
        await db.refresh(document)

        return document

    except HTTPException:
        storage_service.delete(document_id)
        await db.rollback()
        raise

    except Exception:
        storage_service.delete(document_id)
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )

    finally:
        await file.close()