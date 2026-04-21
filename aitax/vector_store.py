from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .documents import DocumentChunk
from .embeddings import HashingEmbedder, cosine_similarity


STOPWORDS = {
    "jakie",
    "jaki",
    "moge",
    "mogę",
    "czy",
    "sie",
    "się",
    "na",
    "do",
    "od",
    "i",
    "w",
    "z",
    "za",
    "dla",
    "oraz",
}


@dataclass(frozen=True)
class SearchResult:
    chunk: DocumentChunk
    score: float


class LocalVectorStore:
    """JSON-backed vector database for local development."""

    def __init__(self, path: Path, embedder: HashingEmbedder | None = None):
        self.path = path
        self.embedder = embedder or HashingEmbedder()
        self._records: list[dict] = []

    def build(self, chunks: list[DocumentChunk]) -> None:
        self._records = [
            {
                "chunk": chunk.to_dict(),
                "embedding": self.embedder.embed(chunk.text),
            }
            for chunk in chunks
        ]
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "backend": "local-hashing-json",
            "dimensions": self.embedder.dimensions,
            "records": self._records,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Vector index not found at {self.path}. Run ingestion first."
            )
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.embedder = HashingEmbedder(dimensions=payload.get("dimensions", 384))
        self._records = payload.get("records", [])

    def query(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not self._records:
            self.load()
        query_vector = self.embedder.embed(query)
        query_terms = {
            token for token in self.embedder.tokenize(query)
            if len(token) > 2 and token not in STOPWORDS
        }
        scored = [
            SearchResult(
                chunk=DocumentChunk.from_dict(record["chunk"]),
                score=self._score(query_vector, query_terms, record),
            )
            for record in self._records
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _score(self, query_vector: list[float], query_terms: set[str], record: dict) -> float:
        vector_score = cosine_similarity(query_vector, record["embedding"])
        if not query_terms:
            return vector_score
        chunk = DocumentChunk.from_dict(record["chunk"])
        source_text = " ".join(
            part or ""
            for part in (
                chunk.metadata.filename,
                chunk.metadata.section,
                chunk.metadata.article,
            )
        )
        chunk_terms = set(self.embedder.tokenize(chunk.text + " " + source_text))
        overlap = len(query_terms.intersection(chunk_terms)) / len(query_terms)
        source_overlap = len(query_terms.intersection(set(self.embedder.tokenize(source_text))))
        source_boost = 0.2 if source_overlap else 0.0
        return (0.45 * vector_score) + (0.55 * overlap) + source_boost
