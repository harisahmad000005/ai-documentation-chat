from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.services.document_processing.extractor import extract_document


DOCUMENTS_DIR = ROOT_DIR / "storage" / "documents"


def main() -> None:
    files = [
        path
        for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file()
    ]

    print(f"DOCUMENTS_DIR: {DOCUMENTS_DIR}")
    print(f"PATHS: {files}")

    if not files:
        print("No documents found.")
        return

    for file_path in files:
        print("=" * 80)
        print(f"FILE: {file_path}")
        print("=" * 80)

        try:
            text = extract_document(file_path)

            print(f"Characters extracted: {len(text)}")
            print()
            print(text[:500])
            print()

        except Exception as exc:
            print(f"ERROR: {exc}")

        print()


if __name__ == "__main__":
    main()