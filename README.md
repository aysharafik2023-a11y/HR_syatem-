# HR System API

Production-ready FastAPI application for HR management with AI-powered resume screening.

## Tech Stack

- **Python 3.12** + **FastAPI**
- **PostgreSQL** with **SQLAlchemy** (async)
- **Alembic** for database migrations
- **JWT** authentication (PyJWT + bcrypt)
- **Docker** + **Docker Compose**
- **AI Matching Engine** (TF-IDF + NLP skill extraction)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI REST API                       │
│                   /api/v1/...                            │
├─────────────┬──────────────────┬────────────────────────┤
│  Resume     │   AI Matching    │   Screening &          │
│  Parser     │   Engine         │   Ranking              │
│  (PDF/DOCX) │   (TF-IDF +     │   (Score + Rank        │
│             │    Skills NLP)   │    candidates)         │
├─────────────┴──────────────────┴────────────────────────┤
│              SQLAlchemy ORM + PostgreSQL                  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### With Docker

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Start PostgreSQL (or use docker compose up db)
# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |

### Job Postings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/jobs/` | Create a job posting |
| GET | `/api/v1/jobs/` | List all job postings |
| GET | `/api/v1/jobs/{id}` | Get a job posting |
| PATCH | `/api/v1/jobs/{id}` | Update a job posting |
| DELETE | `/api/v1/jobs/{id}` | Delete a job posting |

### Resumes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resumes/upload` | Upload resume file (PDF/DOCX) |
| POST | `/api/v1/resumes/submit` | Submit pre-parsed resume text |
| GET | `/api/v1/resumes/` | List all candidates |
| GET | `/api/v1/resumes/{id}` | Get candidate details |

### Screening & Ranking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/screening/run/{job_id}` | Run AI screening for a job |
| GET | `/api/v1/screening/results/{job_id}` | Get ranked results |
| PATCH | `/api/v1/screening/applications/{id}/status` | Update application status |
| GET | `/api/v1/screening/statistics/{job_id}` | Get screening statistics |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |

## Project Structure

```
app/
├── api/          # Route handlers and dependencies
├── database/     # Database engine, session, base model
├── models/       # SQLAlchemy ORM models
├── prompts/      # AI/LLM prompt templates
├── schemas/      # Pydantic request/response schemas
├── services/     # Business logic layer
├── config.py     # Application settings
└── main.py       # FastAPI application entry point
hr_system/        # Resume screening engine
alembic/          # Database migration scripts
tests/            # Test suite
```

## Environment Variables

See `.env.example` for all available configuration options.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Database connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration |
| `HR_UPLOAD_DIR` | `./uploads` | Resume file storage directory |
| `HR_MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |

## Running Tests

```bash
pytest --tb=short -q
```

## Linting

```bash
ruff check app/ tests/
```
