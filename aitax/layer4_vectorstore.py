"""Layer 4 — Vector store. Indeks in-memory + wyszukiwanie po podobieństwie kosinusowym."""

import numpy as np

from . import config, layer3_embeddings


class VectorStore:
    def __init__(self):
        self.chunks = []
        self.matrix = None

    def index(self, chunks):
        self.chunks = chunks
        vectors = layer3_embeddings.embed([c["text"] for c in chunks])
        matrix = np.array(vectors, dtype=np.float32)
        matrix /= np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-9
        self.matrix = matrix
        return self

    def search(self, query, k=None):
        k = k or config.TOP_K
        q = np.array(layer3_embeddings.embed(query)[0], dtype=np.float32)
        q /= np.linalg.norm(q) + 1e-9
        scores = self.matrix @ q
        idx = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in idx]
