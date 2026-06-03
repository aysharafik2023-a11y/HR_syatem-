"""Vector store abstraction for policy document embeddings."""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class DocumentChunk:
    """A chunk of a policy document with its embedding."""

    document_id: int
    title: str
    content: str
    embedding: list[float] = field(default_factory=list)


class VectorStore:
    """In-memory vector store using cosine similarity.

    This is a lightweight implementation suitable for small-to-medium
    policy document collections. For production, swap with ChromaDB or similar.
    """

    def __init__(self):
        self._chunks: list[DocumentChunk] = []

    @property
    def size(self) -> int:
        return len(self._chunks)

    def add_chunk(self, chunk: DocumentChunk) -> None:
        """Add a document chunk to the store."""
        self._chunks.append(chunk)

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Add multiple document chunks."""
        self._chunks.extend(chunks)

    def clear(self) -> None:
        """Remove all chunks from the store."""
        self._chunks.clear()

    def remove_by_document_id(self, document_id: int) -> int:
        """Remove all chunks for a given document. Returns count removed."""
        before = len(self._chunks)
        self._chunks = [c for c in self._chunks if c.document_id != document_id]
        return before - len(self._chunks)

    def search(
        self, query_embedding: list[float], top_k: int = 3
    ) -> list[tuple[DocumentChunk, float]]:
        """Find the most similar chunks to the query embedding.

        Returns list of (chunk, similarity_score) tuples sorted by relevance.
        """
        if not self._chunks or not query_embedding:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        results: list[tuple[DocumentChunk, float]] = []
        for chunk in self._chunks:
            if not chunk.embedding:
                continue
            chunk_vec = np.array(chunk.embedding, dtype=np.float32)
            chunk_norm = np.linalg.norm(chunk_vec)
            if chunk_norm == 0:
                continue
            similarity = float(np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm))
            results.append((chunk, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
