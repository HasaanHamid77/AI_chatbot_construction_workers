from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings


@dataclass
class DocumentChunk:
    text: str
    document: str
    section: str | None = None
    page: int | None = None


class EmbeddingModel:
    def __init__(self):
        settings = get_settings()
        self.model = SentenceTransformer(settings.embedding_model)

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        return np.array(self.model.encode(list(texts), normalize_embeddings=True))


class FaissStore:
    def __init__(self, dim: int, path: str):
        import faiss

        self.dim = dim
        self.path = path
        self.index = faiss.IndexFlatIP(dim)
        self.meta: List[DocumentChunk] = []
        if os.path.exists(path):
            self._load()

    def _load(self):
        import faiss

        self.index = faiss.read_index(self.path)
        meta_path = self.path + ".meta.npy"
        if os.path.exists(meta_path):
            self.meta = list(np.load(meta_path, allow_pickle=True))

    def save(self):
        import faiss

        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        faiss.write_index(self.index, self.path)
        np.save(self.path + ".meta.npy", np.array(self.meta, dtype=object))

    def add(self, embeddings: np.ndarray, chunks: List[DocumentChunk]):
        self.index.add(embeddings.astype(np.float32))
        self.meta.extend(chunks)

    def search(self, embedding: np.ndarray, k: int = 5):
        scores, idx = self.index.search(embedding.astype(np.float32), k)
        results = []
        for i, score in zip(idx[0], scores[0]):
            if i == -1 or i >= len(self.meta):
                continue
            results.append((self.meta[i], float(score)))
        return results


def get_store(embedder: EmbeddingModel) -> FaissStore:
    settings = get_settings()
    store_type = settings.vector_store.lower()
    if store_type != "faiss":
        # Keep code path explicit; Chroma can be added later.
        raise NotImplementedError("Only FAISS is wired in this prototype.")
    dim = embedder.model.get_sentence_embedding_dimension()
    return FaissStore(dim=dim, path=settings.vector_store_path)

