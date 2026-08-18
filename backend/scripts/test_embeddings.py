from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.services.ai.ollama_embeddings import generate_embedding


def main() -> None:
    text = (
        "The Acme Documentation Assistant provides "
        "conversational search over organizational documentation."
    )

    embedding = generate_embedding(text)

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")


if __name__ == "__main__":
    main()