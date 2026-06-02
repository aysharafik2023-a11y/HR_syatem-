"""Policy RAG service layer."""

from sqlalchemy.orm import Session

from hr_system.policy_rag.chunker import chunk_text
from hr_system.policy_rag.embeddings import SimpleEmbedder
from hr_system.policy_rag.models import PolicyDocument
from hr_system.policy_rag.schemas import PolicyChunk, PolicyDocumentCreate, PolicyQueryResponse
from hr_system.policy_rag.vector_store import DocumentChunk, VectorStore


class PolicyRAGService:
    """Service for managing policy documents and performing RAG queries."""

    def __init__(self, db: Session, vector_store: VectorStore, embedder: SimpleEmbedder):
        self.db = db
        self.vector_store = vector_store
        self.embedder = embedder

    def ingest_document(self, data: PolicyDocumentCreate) -> PolicyDocument:
        """Ingest a policy document: store in DB and index in vector store."""
        doc = PolicyDocument(**data.model_dump())
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        chunks = chunk_text(doc.content)
        embeddings = self.embedder.embed_batch(chunks)

        doc_chunks = [
            DocumentChunk(
                document_id=doc.id,
                title=doc.title,
                content=chunk,
                embedding=embedding,
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self.vector_store.add_chunks(doc_chunks)

        return doc

    def get_document(self, doc_id: int) -> PolicyDocument | None:
        return self.db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()

    def list_documents(self, category: str | None = None) -> list[PolicyDocument]:
        query = self.db.query(PolicyDocument)
        if category:
            query = query.filter(PolicyDocument.category == category)
        return query.all()

    def delete_document(self, doc_id: int) -> bool:
        doc = self.get_document(doc_id)
        if not doc:
            return False
        self.vector_store.remove_by_document_id(doc_id)
        self.db.delete(doc)
        self.db.commit()
        return True

    def query_policies(self, query: str, top_k: int = 3) -> PolicyQueryResponse:
        """Query policy documents using semantic similarity."""
        query_embedding = self.embedder.embed(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        policy_chunks = [
            PolicyChunk(
                document_id=chunk.document_id,
                title=chunk.title,
                content=chunk.content,
                relevance_score=round(score, 4),
            )
            for chunk, score in results
        ]

        return PolicyQueryResponse(query=query, results=policy_chunks)
