"""Tests for policy RAG service."""

import pytest

from hr_system.policy_rag.embeddings import SimpleEmbedder
from hr_system.policy_rag.schemas import PolicyDocumentCreate
from hr_system.policy_rag.service import PolicyRAGService
from hr_system.policy_rag.vector_store import VectorStore


@pytest.fixture
def rag_service(db_session):
    vector_store = VectorStore()
    embedder = SimpleEmbedder(dimension=64)
    return PolicyRAGService(db_session, vector_store, embedder)


@pytest.fixture
def sample_policy(rag_service):
    return rag_service.ingest_document(
        PolicyDocumentCreate(
            title="Leave Policy",
            content=(
                "Employees are entitled to 20 days of annual leave per year. "
                "Unused leave can be carried over up to 5 days. "
                "Sick leave is separate and provides 10 days per year. "
                "Parental leave is 12 weeks for primary caregivers."
            ),
            category="HR",
            version="2.0",
        )
    )


class TestPolicyRAGService:
    def test_ingest_document(self, rag_service):
        doc = rag_service.ingest_document(
            PolicyDocumentCreate(
                title="Remote Work Policy",
                content="Employees may work remotely up to 3 days per week.",
                category="HR",
            )
        )
        assert doc.id is not None
        assert doc.title == "Remote Work Policy"
        assert rag_service.vector_store.size > 0

    def test_get_document(self, rag_service, sample_policy):
        found = rag_service.get_document(sample_policy.id)
        assert found is not None
        assert found.title == "Leave Policy"

    def test_get_document_not_found(self, rag_service):
        assert rag_service.get_document(9999) is None

    def test_list_documents(self, rag_service, sample_policy):
        docs = rag_service.list_documents()
        assert len(docs) >= 1

    def test_list_documents_filter_category(self, rag_service, sample_policy):
        rag_service.ingest_document(
            PolicyDocumentCreate(
                title="IT Security",
                content="All passwords must be 12+ characters.",
                category="IT",
            )
        )
        hr_docs = rag_service.list_documents(category="HR")
        assert all(d.category == "HR" for d in hr_docs)

    def test_delete_document(self, rag_service, sample_policy):
        initial_size = rag_service.vector_store.size
        assert rag_service.delete_document(sample_policy.id) is True
        assert rag_service.vector_store.size < initial_size
        assert rag_service.get_document(sample_policy.id) is None

    def test_delete_document_not_found(self, rag_service):
        assert rag_service.delete_document(9999) is False

    def test_query_policies(self, rag_service, sample_policy):
        result = rag_service.query_policies("How many days of annual leave?")
        assert result.query == "How many days of annual leave?"
        assert len(result.results) > 0
        assert result.results[0].relevance_score > 0

    def test_query_policies_empty_store(self, rag_service):
        result = rag_service.query_policies("anything")
        assert result.results == []

    def test_query_returns_relevant_content(self, rag_service):
        rag_service.ingest_document(
            PolicyDocumentCreate(
                title="Expense Policy",
                content="Travel expenses must be submitted within 30 days of travel.",
                category="Finance",
            )
        )
        rag_service.ingest_document(
            PolicyDocumentCreate(
                title="Leave Policy",
                content="Annual leave entitlement is 25 days per calendar year.",
                category="HR",
            )
        )
        result = rag_service.query_policies("leave entitlement days", top_k=1)
        assert len(result.results) == 1
        assert "leave" in result.results[0].content.lower()
