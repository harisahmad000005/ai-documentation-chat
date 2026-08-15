from dataclasses import dataclass


@dataclass
class DocumentContent:
    text: str
    metadata: dict