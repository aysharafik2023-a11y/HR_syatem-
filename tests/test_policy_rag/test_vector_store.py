"""Tests for the vector store."""

from hr_system.policy_rag.vector_store import DocumentChunk, VectorStore


class TestVectorStore:
    def setup_method(self):
        self.store = VectorStore()

    def test_initial_size_is_zero(self):
        assert self.store.size == 0

    def test_add_chunk(self):
        chunk = DocumentChunk(
            document_id=1,
            title="Test",
            content="Hello",
            embedding=[1.0, 0.0, 0.0],
        )
        self.store.add_chunk(chunk)
        assert self.store.size == 1

    def test_add_chunks_batch(self):
        chunks = [
            DocumentChunk(document_id=1, title="A", content="a", embedding=[1, 0, 0]),
            DocumentChunk(document_id=2, title="B", content="b", embedding=[0, 1, 0]),
        ]
        self.store.add_chunks(chunks)
        assert self.store.size == 2

    def test_clear(self):
        self.store.add_chunk(
            DocumentChunk(document_id=1, title="X", content="x", embedding=[1, 0])
        )
        self.store.clear()
        assert self.store.size == 0

    def test_remove_by_document_id(self):
        self.store.add_chunks(
            [
                DocumentChunk(document_id=1, title="A", content="a", embedding=[1, 0]),
                DocumentChunk(document_id=1, title="A2", content="a2", embedding=[0, 1]),
                DocumentChunk(document_id=2, title="B", content="b", embedding=[1, 1]),
            ]
        )
        removed = self.store.remove_by_document_id(1)
        assert removed == 2
        assert self.store.size == 1

    def test_search_returns_results(self):
        self.store.add_chunks(
            [
                DocumentChunk(document_id=1, title="Doc1", content="hello", embedding=[1, 0, 0]),
                DocumentChunk(document_id=2, title="Doc2", content="world", embedding=[0, 1, 0]),
                DocumentChunk(document_id=3, title="Doc3", content="test", embedding=[0, 0, 1]),
            ]
        )
        results = self.store.search([1, 0, 0], top_k=2)
        assert len(results) == 2
        assert results[0][0].document_id == 1
        assert results[0][1] == pytest.approx(1.0)

    def test_search_empty_store(self):
        results = self.store.search([1, 0, 0])
        assert results == []

    def test_search_empty_query(self):
        self.store.add_chunk(
            DocumentChunk(document_id=1, title="X", content="x", embedding=[1, 0])
        )
        results = self.store.search([])
        assert results == []

    def test_search_respects_top_k(self):
        for i in range(10):
            self.store.add_chunk(
                DocumentChunk(
                    document_id=i, title=f"Doc{i}", content=f"content{i}", embedding=[i, 1, 0]
                )
            )
        results = self.store.search([5, 1, 0], top_k=3)
        assert len(results) == 3

    def test_search_cosine_similarity_order(self):
        self.store.add_chunks(
            [
                DocumentChunk(document_id=1, title="A", content="a", embedding=[1, 0, 0]),
                DocumentChunk(document_id=2, title="B", content="b", embedding=[0.9, 0.1, 0]),
                DocumentChunk(document_id=3, title="C", content="c", embedding=[0, 0, 1]),
            ]
        )
        results = self.store.search([1, 0, 0], top_k=3)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_skips_empty_embeddings(self):
        self.store.add_chunks(
            [
                DocumentChunk(document_id=1, title="A", content="a", embedding=[]),
                DocumentChunk(document_id=2, title="B", content="b", embedding=[1, 0]),
            ]
        )
        results = self.store.search([1, 0], top_k=5)
        assert len(results) == 1
        assert results[0][0].document_id == 2


# Need pytest for approx
import pytest  # noqa: E402
