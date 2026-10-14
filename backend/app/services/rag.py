import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentHit:
    source: str
    excerpt: str
    score: float


class LocalKnowledgeBase:
    """Recuperador lexical ligero; se sustituirá por pgvector al ingerir PDFs."""

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def search(self, query: str, limit: int = 3) -> list[DocumentHit]:
        if not self.directory.exists():
            return []
        terms = set(re.findall(r"[a-záéíóúñ0-9]+", query.lower()))
        hits: list[DocumentHit] = []
        for path in self.directory.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for block in text.split("\n\n"):
                words = set(re.findall(r"[a-záéíóúñ0-9]+", block.lower()))
                overlap = len(terms & words)
                if overlap:
                    hits.append(DocumentHit(path.name, block[:500], overlap / max(len(terms), 1)))
        return sorted(hits, key=lambda item: item.score, reverse=True)[:limit]
