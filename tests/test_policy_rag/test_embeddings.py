"""Tests for embedding generation."""

import math

from hr_system.policy_rag.embeddings import SimpleEmbedder


class TestSimpleEmbedder:
    def setup_method(self):
        self.embedder = SimpleEmbedder(dimension=64)

    def test_embed_returns_correct_dimension(self):
        embedding = self.embedder.embed("Hello world")
        assert len(embedding) == 64

    def test_embed_empty_text(self):
        embedding = self.embedder.embed("")
        assert len(embedding) == 64
        assert all(v == 0.0 for v in embedding)

    def test_embed_is_normalized(self):
        embedding = self.embedder.embed("This is a test sentence about HR policies")
        norm = math.sqrt(sum(v * v for v in embedding))
        assert abs(norm - 1.0) < 1e-6

    def test_embed_deterministic(self):
        text = "Company leave policy"
        emb1 = self.embedder.embed(text)
        emb2 = self.embedder.embed(text)
        assert emb1 == emb2

    def test_similar_texts_have_similar_embeddings(self):
        emb1 = self.embedder.embed("annual leave policy for employees")
        emb2 = self.embedder.embed("employee annual leave rules")
        emb3 = self.embedder.embed("quarterly financial budget report")

        # Cosine similarity
        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(x * x for x in b))
            return dot / (na * nb) if na > 0 and nb > 0 else 0

        sim_related = cosine_sim(emb1, emb2)
        sim_unrelated = cosine_sim(emb1, emb3)
        assert sim_related > sim_unrelated

    def test_embed_batch(self):
        texts = ["text one", "text two", "text three"]
        embeddings = self.embedder.embed_batch(texts)
        assert len(embeddings) == 3
        assert all(len(e) == 64 for e in embeddings)

    def test_tokenize(self):
        tokens = SimpleEmbedder._tokenize("Hello, World! This is a test-123.")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "123" in tokens
        # Short tokens filtered
        assert "is" not in tokens
        assert "a" not in tokens
