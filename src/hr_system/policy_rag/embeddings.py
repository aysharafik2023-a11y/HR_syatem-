"""Embedding generation for policy documents.

Uses a simple TF-IDF-like approach as the default embedder
so the system works without external API keys. Can be swapped
for sentence-transformers or OpenAI embeddings in production.
"""

import hashlib
import math
import re
from collections import Counter


class SimpleEmbedder:
    """A lightweight embedder based on term frequency hashing.

    This provides deterministic, API-free embeddings suitable for
    testing and small deployments. For production, replace with
    SentenceTransformerEmbedder or OpenAIEmbedder.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        """Generate a fixed-dimension embedding for text."""
        if not text:
            return [0.0] * self.dimension

        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension
        token_counts = Counter(tokens)

        for token, count in token_counts.items():
            hash_bytes = hashlib.md5(token.encode()).hexdigest()
            for i in range(0, len(hash_bytes), 2):
                idx = int(hash_bytes[i : i + 2], 16) % self.dimension
                tf = 1 + math.log(count)
                vector[idx] += tf

        # Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(text) for text in texts]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple whitespace + punctuation tokenizer."""
        text = text.lower()
        tokens = re.findall(r"\b[a-z0-9]+\b", text)
        # Filter very short tokens
        return [t for t in tokens if len(t) > 2]
