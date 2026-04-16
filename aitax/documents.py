from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SourceMetadata:
    filename: str
    section: str | None
    article: str | None
    chunk_id: str


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    metadata: SourceMetadata

    def to_dict(self) -> dict:
        return {"text": self.text, "metadata": asdict(self.metadata)}

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentChunk":
        return cls(text=data["text"], metadata=SourceMetadata(**data["metadata"]))


SECTION_RE = re.compile(r"(Rozdzia[lł]\s+\d+:[^\n\r]+)", re.IGNORECASE)
ARTICLE_RE = re.compile(r"\bArt\.\s*\d+[a-z]?(?:\.\s*\d+)?", re.IGNORECASE)


def read_text_file(path: Path) -> str:
    """Read raw legal text while tolerating legacy encodings in source files."""
    for encoding in ("utf-8", "utf-8-sig", "cp1250", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def extract_section(text: str) -> str | None:
    match = SECTION_RE.search(text)
    return clean_whitespace(match.group(1)) if match else None


def extract_article(text: str) -> str | None:
    match = ARTICLE_RE.search(text)
    return clean_whitespace(match.group(0)) if match else None


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, max_words: int = 180, overlap_words: int = 35) -> list[str]:
    """Chunk by words; small overlap keeps article conditions near thresholds."""
    words = clean_whitespace(text).split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, max_words - overlap_words)
    for start in range(0, len(words), step):
        chunk_words = words[start : start + max_words]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
        if start + max_words >= len(words):
            break
    return chunks


def load_raw_documents(raw_dir: Path) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(raw_dir.glob("*.txt")):
        text = read_text_file(path)
        section = extract_section(text)
        article = extract_article(text)
        for index, chunk in enumerate(chunk_text(text), start=1):
            chunk_id = f"{path.stem}:{index}"
            chunks.append(
                DocumentChunk(
                    text=chunk,
                    metadata=SourceMetadata(
                        filename=path.name,
                        section=section,
                        article=article,
                        chunk_id=chunk_id,
                    ),
                )
            )
    return chunks


def format_source(metadata: SourceMetadata) -> str:
    parts = [metadata.filename]
    if metadata.article:
        parts.append(metadata.article)
    if metadata.section:
        parts.append(metadata.section)
    return " | ".join(parts)


def unique_sources(chunks: Iterable[DocumentChunk]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        source = format_source(chunk.metadata)
        if source not in seen:
            sources.append(source)
            seen.add(source)
    return sources
