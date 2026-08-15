from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.services.document_processing.chunker import chunk_document
from app.services.document_processing.extractor import extract_document


DOCUMENTS_DIR = ROOT_DIR / "storage" / "documents"


def main() -> None:
    files = [
        path
        for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file()
    ]

    if not files:
        print("No documents found.")
        return

    for file_path in files:
        print("=" * 80)
        print(f"FILE: {file_path}")
        print("=" * 80)

        try:
            text = extract_document(file_path)

            document_id = file_path.parent.name

            chunks = chunk_document(
                text,
                document_id=document_id,
                filename=file_path.name,
            )

            print(f"Characters: {len(text)}")
            print(f"Chunks: {len(chunks)}")
            print()

            for chunk in chunks[:3]:
                print("-" * 80)
                print(f"Chunk index: {chunk.chunk_index}")
                print(f"Metadata: {chunk.metadata}")
                print()
                print(chunk.content)

        except Exception as exc:
            print(f"ERROR: {exc}")

        print()


if __name__ == "__main__":
    main()