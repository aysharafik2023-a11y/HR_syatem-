# AI Customer Support Platform

A production-ready, AI-powered customer support platform for SaaS companies. Automatically classifies, prioritizes, and routes support tickets while assisting agents with AI-generated responses.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (FastAPI)                         │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
│   Auth   │ Tickets  │Responses │Escalation│Knowledge │   Health     │
│  Routes  │  Routes  │  Routes  │  Routes  │  Routes  │   Routes     │
├──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┤
│                        Service Layer                                  │
├──────────┬──────────┬──────────┬──────────┬──────────────────────────┤
│   Auth   │  Ticket  │ Response │Escalation│   Classification         │
│ Service  │ Service  │ Service  │ Service  │     Service              │
├──────────┴──────────┴──────────┴──────────┴──────────────────────────┤
│                      Repository Layer                                 │
├──────────┬──────────┬──────────┬──────────┬──────────────────────────┤
│   User   │  Ticket  │ Response │Escalation│   Knowledge Base         │
│   Repo   │   Repo   │   Repo   │   Repo   │      Repo               │
├──────────┴──────────┴──────────┴──────────┴──────────────────────────┤
│                        Database (PostgreSQL)                           │
└──────────────────────────────────────────────────────────────────────┘
         │                                          │
         ▼                                          ▼
┌──────────────────┐                    ┌────────────────────┐
│  OpenAI API      │                    │  Redis + Celery    │
│  (Classification,│                    │  (Background Tasks,│
│   RAG, Responses)│                    │   SLA Monitoring)  │
└──────────────────┘                    └────────────────────┘
```

## Features

- **AI Ticket Classification**: Automatic categorization and priority assignment using LLM
- **AI Response Generation**: RAG-powered responses with knowledge base search
- **Escalation Engine**: Auto-escalates on critical priority, negative sentiment, or SLA breach
- **JWT Authentication**: Secure auth with role-based access control (Admin, Manager, Agent)
- **Knowledge Base**: Searchable knowledge store for RAG context retrieval
- **Background Tasks**: Celery workers for async classification and SLA monitoring
- **Monitoring**: Health checks, metrics, structured logging, audit trail
- **Full Test Suite**: Unit, integration, and API tests with 47 passing tests

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 16, SQLAlchemy 2.0 |
| Migrations | Alembic |
| Cache/Queue | Redis 7, Celery |
| AI | OpenAI API (GPT-4o-mini) |
| Auth | JWT (python-jose), bcrypt |
| Testing | Pytest, httpx |
| Deployment | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Logging | structlog (JSON) |

## Database Design

### Entity Relationships

```
Users (1) ──────── (N) Tickets
  │                      │
  │                      ├── (N) Responses
  │                      │
  │                      └── (N) Escalations
  │
  └── (N) Responses (as agent)

Knowledge Base (standalone, used for RAG)
Audit Logs (standalone, tracks all actions)
```

### Tables

| Table | Purpose |
|-------|---------|
| `users` | Support agents, managers, admins |
| `tickets` | Customer support tickets with AI classification |
| `responses` | AI-generated and agent-edited responses |
| `escalations` | Escalation history with reason tracking |
| `knowledge_base` | Articles for RAG retrieval |
| `audit_logs` | Complete action audit trail |

## Prompt Engineering Strategy

Prompts are organized in `app/prompts/` with dedicated templates for:

1. **Classification** (`classification.py`): Multi-factor categorization considering business impact, urgency, severity, and customer tone. Returns structured JSON with confidence scores.

2. **Response Generation** (`response_generation.py`): Context-aware responses using RAG. Includes knowledge base articles, generates troubleshooting steps, and evaluates escalation needs.

3. **Escalation Decision** (`escalation.py`): Evaluates tickets against SLA, sentiment, and resolution history to recommend escalation actions.

All prompts use structured JSON output format for reliable parsing with confidence scoring.

## AI Workflow

```
New Ticket Created
       │
       ▼
┌─────────────────┐
│ AI Classification│ ──→ Category + Priority + Confidence
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Sentiment Analysis│ ──→ Score (-1.0 to 1.0)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ Escalation Check │────→│ Auto-Escalate│ (if critical/negative/SLA breach)
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ Agent Requests   │────→│ Knowledge    │
│ AI Response      │     │ Base Search  │ (RAG)
└────────┬────────┘     └──────────────┘
         │
         ▼
┌─────────────────┐
│ Generate Response│ ──→ Professional response + troubleshooting steps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent Reviews &  │ ──→ Edit if needed, then send
│ Sends Response   │
└─────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- OpenAI API key

### Run with Docker

```bash
# Clone the repository
git clone https://github.com/aysharafik2023-a11y/ai-customer-support-platform.git
cd ai-customer-support-platform

# Copy environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

# Start all services
docker compose up -d

# Run migrations
docker compose exec app alembic upgrade head

# Access the API
open http://localhost:8000/docs
```

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Start PostgreSQL and Redis (via Docker)
docker compose up db redis -d

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest -v

# Run linting
ruff check app/ tests/
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/tickets` | Create ticket (triggers AI classification) |
| GET | `/api/v1/tickets` | List tickets with pagination/filtering |
| GET | `/api/v1/tickets/{id}` | Get ticket details |
| PUT | `/api/v1/tickets/{id}` | Update ticket |
| DELETE | `/api/v1/tickets/{id}` | Delete ticket |
| POST | `/api/v1/responses/generate` | Generate AI response for ticket |
| PUT | `/api/v1/responses/{id}` | Edit response before sending |
| POST | `/api/v1/responses/{id}/send` | Send response to customer |
| GET | `/api/v1/escalations` | List pending escalations |
| POST | `/api/v1/escalations/{id}/acknowledge` | Acknowledge escalation |
| POST | `/api/v1/escalations/{id}/resolve` | Resolve escalation |
| POST | `/api/v1/knowledge-base` | Add knowledge base entry |
| GET | `/api/v1/knowledge-base/search?q=` | Search knowledge base |
| GET | `/health` | Health check |
| GET | `/metrics` | Application metrics |

## Deployment

### Docker Compose (Production)

```bash
docker compose -f docker-compose.yml up -d
```

Services:
- **app** (port 8000): FastAPI application
- **db** (port 5432): PostgreSQL 16
- **redis** (port 6379): Redis 7
- **celery_worker**: Background task processing
- **celery_beat**: Scheduled SLA checks every 15 minutes

### Kubernetes

The Docker image is Kubernetes-ready with:
- Health checks (`/health`, `/ready`)
- Non-root user
- Environment variable configuration
- Stateless application design

## Project Structure

```
ai-customer-support-platform/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/                # Config, security, logging
│   ├── database/            # SQLAlchemy setup, Alembic migrations
│   ├── middleware/          # Auth middleware, audit logging
│   ├── models/              # SQLAlchemy ORM models
│   ├── prompts/             # AI prompt templates
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   ├── utils/               # Shared utilities
│   ├── main.py              # FastAPI app factory
│   └── worker.py            # Celery worker configuration
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── integration/         # Integration tests
│   └── unit/                # Unit tests
├── config/                  # Configuration files
├── .github/workflows/       # CI/CD pipeline
├── docker-compose.yml       # Multi-service orchestration
├── Dockerfile               # Application container
├── alembic.ini              # Migration configuration
└── pyproject.toml           # Python project configuration
```

## Assumptions

1. OpenAI API is used for LLM operations (configurable model)
2. Email notifications are configured via SMTP (not fully implemented in MVP)
3. Knowledge base uses text search (vector embeddings ready for future upgrade)
4. Single-tenant deployment (multi-tenancy can be added)
5. SLA timers are based on ticket creation time
6. AI classification happens synchronously on ticket creation (can be made async via Celery)

## Future Improvements

1. **Vector Search**: Replace text-based knowledge search with embedding-based similarity
2. **Multi-tenancy**: Add organization/tenant isolation
3. **WebSocket**: Real-time ticket updates and agent notifications
4. **Email Integration**: Inbound email parsing and outbound notification sending
5. **Analytics Dashboard**: Ticket volume, resolution times, agent performance metrics
6. **Fine-tuning**: Custom model fine-tuning on historical ticket data
7. **Multi-LLM**: Support for Anthropic Claude, local models via Ollama
8. **Caching**: Redis caching for frequent knowledge base queries
9. **Rate Limiting**: API rate limiting per user/role
10. **Webhook Support**: Integration with Slack, Teams, PagerDuty for escalations
