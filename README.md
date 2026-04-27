# Music Analysis Platform for Worship Groups

A comprehensive web platform for worship groups and professional musicians that transforms a YouTube link into an editable base of musical structure, key, BPM, chords, and setlist, with an asynchronous pipeline architecture.

## Architecture Overview

This is a monorepo implementing a Software Design Document-driven Development (SDD) approach with explicit contracts between domain, architecture, flows, data, interfaces, observability, and acceptance criteria.

### Technology Stack

| Component | Technology | Responsibility |
|-----------|-----------|-----------------|
| Frontend | Next.js / React / TypeScript | Library, editor, setlists, live mode |
| API Gateway | FastAPI / Pydantic | Auth, CRUD, job creation, status queries |
| Job Queue | Celery + Redis | Async task orchestration |
| MIR Worker | Essentia | BPM, beats, key, segmentation, features |
| Separation Worker | Demucs | Vocal/instrumental separation |
| Speech Worker | Whisper | ASR with timestamps, speech detection |
| Semantic Worker | LLM | Section labeling, output normalization |
| Database | PostgreSQL | Transactional domain, audit, versioning |
| Security | Row Level Security (RLS) | Multi-tenant isolation |
| Storage | S3/GCS | Stems, waveforms, analysis JSON |

## Project Structure

```
/apps
  /web                 ← Next.js frontend
  /api                 ← FastAPI backend
  /worker-audio        ← Celery worker for audio analysis
  /worker-semantic     ← Celery worker for semantic processing
/packages
  /domain              ← Shared domain models and business rules
  /contracts           ← API contracts and schemas
  /test-fixtures       ← Shared test utilities and factories
/docs
  PRD.md               ← Product requirements document
  ADR-*.md             ← Architecture decision records
/tests
  /contract            ← API contract tests
  /integration         ← Integration tests
  /e2e                 ← End-to-end tests
  /bdd                 ← BDD scenarios in Gherkin
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd music-analysis-platform-prd

# Start infrastructure
docker-compose up -d

# Install dependencies
cd apps/api && pip install -r requirements.txt
cd ../worker-audio && pip install -r requirements.txt
cd ../worker-semantic && pip install -r requirements.txt
cd ../web && npm install

# Run migrations
cd ../api && python manage.py migrate

# Start services
# Terminal 1: API
cd apps/api && python -m uvicorn main:app --reload

# Terminal 2: Worker Audio
cd apps/worker-audio && celery -A tasks worker --loglevel=info

# Terminal 3: Worker Semantic
cd apps/worker-semantic && celery -A tasks worker --loglevel=info

# Terminal 4: Frontend
cd apps/web && npm run dev
```

## Core Features

### 1. YouTube Import Pipeline

Users paste a YouTube URL and receive an `analysis_id` immediately with status `queued`. The system then processes through phases: `extracting_metadata` → `fetching_text` → `separating_sources` → `analyzing_audio` → `postprocessing_structure` → `ready`.

### 2. Async Analysis Pipeline

The system combines Music Information Retrieval (MIR), Automatic Speech Recognition (ASR), and Large Language Models (LLM) to automatically detect:

- **BPM and Tempo**: Beat detection and tempo estimation
- **Tonality**: Key detection with confidence scores
- **Structure**: Sections (intro, verse, pre-chorus, chorus, bridge, interlude, speech)
- **Lyrics**: Aligned to timestamps with speech/singing classification
- **Harmony**: Chord progression detection

### 3. Manual Editing & Versioning

Users can edit the automatically detected structure without affecting the raw analysis results. Arrangements are versioned and support multiple variations (original, acoustic, morning worship, conference).

### 4. Chord Charts & Transposition

Editable chord charts with automatic transposition to different keys. Low-confidence chords are visually marked for user review.

### 5. Setlists & Live Mode

Create setlists with specific execution keys, preserve immutable history of past performances, and use a clean live mode interface for stage presentations.

### 6. Multi-Tenant Isolation

Complete data isolation by organization with Row Level Security (RLS) in PostgreSQL. Role-based access control (leader, musician) enforces permissions.

## API Reference

### Main Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/songs/import-youtube` | POST | Import song from YouTube URL |
| `/analyses/{analysis_id}` | GET | Poll analysis status and progress |
| `/songs/{song_id}` | GET | Retrieve song with metadata |
| `/songs/{song_id}/arrangements` | POST | Create new arrangement |
| `/arrangements/{arrangement_id}/sections` | PATCH | Edit arrangement sections |
| `/arrangements/{arrangement_id}/chords` | PATCH | Edit chord chart |
| `/setlists` | POST | Create setlist |
| `/setlists/{setlist_id}/items` | POST | Add song to setlist |
| `/setlists/{setlist_id}/live/start` | POST | Start live mode |
| `/organizations/{organization_id}/library` | GET | List songs in organization |

## Analysis Pipeline Phases

```
queued
  ↓
extracting_metadata (fetch YouTube metadata, title, duration)
  ↓
fetching_text (get captions or use manual entry)
  ↓
separating_sources (optional: Demucs for vocal/instrumental)
  ↓
analyzing_audio (Essentia: BPM, key, features)
  ↓
postprocessing_structure (LLM: label sections, normalize output)
  ↓
ready (analysis complete, ready for editing)
```

## Testing Strategy

The project follows a pyramid approach:

- **Unit Tests**: Domain rules, transposition, versioning, permissions, URL parsing
- **Contract Tests**: API schemas, state machines, auth, authorization
- **Integration Tests**: FastAPI + queue + database + storage; workers with mocked Essentia/Demucs/Whisper/LLM
- **BDD Tests**: Complete user workflows (import → edit → setlist → live)
- **E2E Tests**: Full browser-based scenarios

## Key Business Rules

1. **Analysis Immutability**: Automatically detected analysis results are never overwritten by user edits. Arrangements are separate entities.
2. **Setlist History**: Once a setlist is used in a presentation, its items become immutable to preserve historical accuracy.
3. **Role-Based Publishing**: Only leaders can publish arrangements; musicians can view and comment.
4. **Confidence Scores**: All critical results (BPM, key, sections, chords) include confidence scores for user review.
5. **Multi-Tenant Isolation**: Organizations cannot access each other's data through any API endpoint.

## Documentation

- **PRD.md**: Complete product requirements document
- **ADR-001-essentia-first.md**: Architecture decision for Essentia as primary MIR engine
- **ADR-002-multi-tenant-rls.md**: Multi-tenant isolation strategy with RLS

## Development Workflow

1. Update schema in `packages/domain/models.py`
2. Add database helpers in `apps/api/db.py`
3. Add or extend procedures in `apps/api/routers.py`
4. Write unit tests in `tests/unit/`
5. Write integration tests in `tests/integration/`
6. Build frontend features in `apps/web/`
7. Cover with E2E tests in `tests/e2e/`

## Contributing

This project uses SDD methodology. Before implementing:

1. Document the requirement in the PRD
2. Define domain rules and contracts
3. Write tests first (TDD)
4. Implement functionality
5. Verify all tests pass
6. Create ADR if making architectural decisions

## License

MIT
