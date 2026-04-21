"""Layer 2 — Chunker. Dzieli dokumenty na fragmenty z zakładką słów."""

from . import config


def chunk_text(text, size=None, overlap=None):
    size = size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP
    words = text.split()
    if len(words) <= size:
        return [text]
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + size]))
        i += size - overlap
    return chunks


def chunk_documents(documents):
    chunks = []
    for doc in documents:
        for i, piece in enumerate(chunk_text(doc["text"])):
            chunks.append(
                {
                    "id": f"{doc['stem']}#{i}",
                    "source": doc["source"],
                    "text": piece,
                }
            )
    return chunks
