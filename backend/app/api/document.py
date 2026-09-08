import uuid
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

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    get_user_document,
    get_user_documents,
)
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
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
            user_id=current_user.id,
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
        ) from None

    finally:
        await file.close()


@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    return await get_user_documents(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await get_user_document(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    document = await get_user_document(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        storage_service.delete(document.id)

        await db.delete(document)
        await db.commit()

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        ) from None