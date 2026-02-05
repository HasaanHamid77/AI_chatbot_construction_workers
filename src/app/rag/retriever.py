from __future__ import annotations

from typing import List, Tuple

import numpy as np

from app.rag.vector_store import DocumentChunk, EmbeddingModel, get_store


class Retriever:
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.store = get_store(self.embedder)

    def retrieve(self, query: str, k: int = 4) -> List[Tuple[DocumentChunk, float]]:
        q_emb = self.embedder.encode([query])
        return self.store.search(q_emb, k=k)

    def add_documents(self, chunks: List[DocumentChunk]):
        embeddings = self.embedder.encode([c.text for c in chunks])
        self.store.add(embeddings, chunks)
        self.store.save()


def sanitize_context(chunks: List[DocumentChunk], max_chars: int = 1800) -> str:
    """Simple prompt-injection hardening: drop long or suspicious spans."""
    safe_lines = []
    total = 0
    for c in chunks:
        text = c.text
        if any(marker in text.lower() for marker in ["ignore previous", "disregard", "system prompt"]):
            continue
        snippet = text[:400]  # avoid overly long attacker content
        safe_lines.append(snippet)
        total += len(snippet)
        if total >= max_chars:
            break
    return "\n---\n".join(safe_lines)

