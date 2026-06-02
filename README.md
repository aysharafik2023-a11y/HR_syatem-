# HR System

A comprehensive HR system built with FastAPI featuring:

- **Recruitment Module** — Job postings, candidate management, and application tracking
- **Policy Analysis (RAG)** — Upload company policies, chunk and embed them, then query using semantic similarity
- **Chatbot** — Conversational interface that uses RAG to answer HR policy questions

## Architecture

```
src/hr_system/
├── app.py                 # FastAPI application entry point
├── database.py            # SQLAlchemy database config
├── recruitment/           # Recruitment module
│   ├── models.py          # DB models (JobPosting, Candidate, Application)
│   ├── schemas.py         # Pydantic schemas
│   ├── service.py         # Business logic
│   └── routes.py          # API endpoints
├── policy_rag/            # RAG-based policy analysis
│   ├── models.py          # DB models (PolicyDocument)
│   ├── schemas.py         # Pydantic schemas
│   ├── chunker.py         # Text chunking utilities
│   ├── embeddings.py      # Embedding generation
│   ├── vector_store.py    # In-memory vector store
│   ├── service.py         # RAG service logic
│   └── routes.py          # API endpoints
└── chatbot/               # Chatbot module
    ├── schemas.py          # Pydantic schemas
    ├── conversation.py     # Conversation management
    ├── service.py          # Chatbot service with RAG integration
    └── routes.py           # API endpoints
```

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn hr_system.app:app --reload

# Run tests
pytest --cov=hr_system

# Run linter
ruff check src/ tests/
```

## API Endpoints

### Recruitment
- `POST /recruitment/jobs` — Create a job posting
- `GET /recruitment/jobs` — List job postings
- `GET /recruitment/jobs/{id}` — Get job details
- `PATCH /recruitment/jobs/{id}` — Update a job posting
- `DELETE /recruitment/jobs/{id}` — Delete a job posting
- `POST /recruitment/candidates` — Register a candidate
- `GET /recruitment/candidates` — List candidates
- `POST /recruitment/applications` — Submit an application
- `GET /recruitment/applications` — List applications
- `PATCH /recruitment/applications/{id}/status` — Update application status

### Policy Analysis (RAG)
- `POST /policies/documents` — Upload a policy document
- `GET /policies/documents` — List policy documents
- `GET /policies/documents/{id}` — Get a policy document
- `DELETE /policies/documents/{id}` — Delete a policy document
- `POST /policies/query` — Query policies using semantic search

### Chatbot
- `POST /chat/` — Send a message to the HR chatbot
- `GET /chat/{conversation_id}/history` — Get conversation history

### Health
- `GET /health` — Health check
