import hashlib
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.constants import STORAGE_DIR


CHUNK_SIZE = 1024 * 1024  # 1 MB


class StorageService:
    def __init__(self, storage_dir: Path = STORAGE_DIR):
        self.storage_dir = storage_dir

    async def save(
        self,
        document_id: UUID,
        extension: str,
        upload_file: UploadFile,
    ) -> tuple[Path, int, str]:
        document_dir = self.storage_dir / str(document_id)
        document_dir.mkdir(parents=True, exist_ok=True)

        file_path = document_dir / f"original{extension}"

        sha256 = hashlib.sha256()
        file_size = 0

        try:
            with file_path.open("wb") as output_file:
                while chunk := await upload_file.read(CHUNK_SIZE):
                    file_size += len(chunk)
                    sha256.update(chunk)
                    output_file.write(chunk)

        except Exception:
            if file_path.exists():
                file_path.unlink()

            if document_dir.exists() and not any(document_dir.iterdir()):
                document_dir.rmdir()

            raise

        return file_path, file_size, sha256.hexdigest()

    def delete(self, document_id: UUID) -> None:
        document_dir = self.storage_dir / str(document_id)

        if not document_dir.exists():
            return

        for file_path in document_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()

        document_dir.rmdir()