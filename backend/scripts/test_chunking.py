from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.services.chunking import split_text
from app.services.document_processing.extractor import extract_document


DOCUMENT_PATH = ROOT_DIR / "storage" / "documents"


def main():
    files = [
        path
        for path in DOCUMENT_PATH.rglob("*")
        if path.is_file()
    ]

    if not files:
        print("No documents found.")
        return

    document_path = files[0]

    print(f"Testing document: {document_path}")

    text = extract_document(document_path)

    print(f"Extracted characters: {len(text)}")

    chunks = split_text(text)

    print(f"Number of chunks: {len(chunks)}")
    print()

    for index, chunk in enumerate(chunks):
        print("=" * 80)
        print(f"CHUNK {index}")
        print(f"Characters: {len(chunk)}")
        print("=" * 80)
        print(chunk)
        print()


if __name__ == "__main__":
    main()