from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.constants import CHUNK_SIZE, CHUNK_OVERLAP



def split_text(text: str) -> list[str]:
    """
    Split extracted document text into overlapping chunks.
    """

    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    return splitter.split_text(text)