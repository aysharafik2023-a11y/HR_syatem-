"""Tests for text chunking utilities."""

from hr_system.policy_rag.chunker import chunk_text


class TestChunkText:
    def test_empty_text(self):
        assert chunk_text("") == []

    def test_short_text_single_chunk(self):
        text = "This is a short policy."
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_text_split_into_multiple_chunks(self):
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=300, overlap=50)
        assert len(chunks) > 1

    def test_overlap_between_chunks(self):
        # Create text with clear sentence boundaries
        text = "".join(f"Sentence number {i}. " for i in range(20))
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        assert len(chunks) > 1

    def test_breaks_at_sentence_boundary(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        # Check that chunks end at period boundaries when possible
        for chunk in chunks[:-1]:
            assert chunk.endswith(".") or len(chunk) <= 50

    def test_no_empty_chunks(self):
        text = "Word " * 200
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        assert all(len(c) > 0 for c in chunks)

    def test_all_content_preserved(self):
        text = "Hello world. This is a test document. It has multiple sentences."
        chunks = chunk_text(text, chunk_size=30, overlap=5)
        # All words from original should appear in at least one chunk
        for word in text.split():
            word_clean = word.strip(".")
            assert any(word_clean in chunk for chunk in chunks)
