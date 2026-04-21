from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections import Counter


TOKEN_RE = re.compile(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", re.UNICODE)


class HashingEmbedder:
    """Small local embedding model for demos.

    It creates deterministic normalized bag-of-token vectors. The vector store
    interface is intentionally simple so Chroma, FAISS, or sentence-transformer
    embeddings can replace this class later without touching orchestration code.
    """

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def tokenize(self, text: str) -> list[str]:
        return [normalize_token(token) for token in TOKEN_RE.findall(text)]

    def embed(self, text: str) -> list[float]:
        counts: Counter[int] = Counter()
        for token in self.tokenize(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            counts[index] += 1

        vector = [0.0] * self.dimensions
        if not counts:
            return vector

        norm = math.sqrt(sum(value * value for value in counts.values()))
        for index, value in counts.items():
            vector[index] = value / norm
        return vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def normalize_token(token: str) -> str:
    decomposed = unicodedata.normalize("NFKD", token.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))
