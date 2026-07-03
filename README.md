# HR Resume Screening System

AI-powered resume screening system that processes 10,000+ resumes per month. Reads resumes (PDF/DOCX), matches them to job descriptions using NLP, ranks candidates, stores results, and exposes a REST API for HR portal integration.

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
│              SQLAlchemy ORM + SQLite/PostgreSQL           │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn hr_system.app:app --host 0.0.0.0 --port 8000

# Open API docs
# http://localhost:8000/docs
```

## API Endpoints

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

## Usage Example

```bash
# 1. Create a job posting
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "department": "Engineering",
    "description": "Build scalable backend services...",
    "requirements": "5+ years Python, Django/FastAPI, PostgreSQL, Docker"
  }'

# 2. Upload a resume
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -F "file=@resume.pdf" \
  -F "candidate_name=Jane Smith" \
  -F "candidate_email=jane@example.com"

# 3. Run AI screening
curl -X POST http://localhost:8000/api/v1/screening/run/1?top_n=10

# 4. Get ranked results
curl http://localhost:8000/api/v1/screening/results/1
```

## AI Matching Engine

The system uses a multi-signal approach:
- **TF-IDF Cosine Similarity (40%)**: Content-level matching between resume and job description
- **Skill Extraction & Matching (40%)**: NLP-based technical skill identification and comparison
- **Experience Matching (20%)**: Years of experience extraction and comparison

Scoring is 0.0–1.0, with candidates ranked by overall score.

## Development

```bash
# Run tests
pytest --tb=short -q

# Run linter
ruff check hr_system/ tests/

# Fix lint issues
ruff check --fix hr_system/ tests/
```

## Configuration

Environment variables (prefix `HR_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `HR_DATABASE_URL` | `sqlite:///./hr_system.db` | Database connection string |
| `HR_UPLOAD_DIR` | `./uploads` | Resume file storage directory |
| `HR_MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |

For PostgreSQL in production:
```bash
export HR_DATABASE_URL="postgresql://user:pass@host:5432/hr_db"
```
