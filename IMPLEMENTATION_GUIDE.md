# Implementation Guide - Music Analysis Platform

This guide provides step-by-step instructions for completing the implementation of the Music Analysis Platform according to the PRD.

## Architecture Overview

The platform is built as a monorepo with the following components:

- **Frontend**: Next.js + React + TypeScript
- **Backend API**: FastAPI + Pydantic
- **Job Queue**: Celery + Redis
- **Database**: PostgreSQL with Row Level Security
- **Workers**: Specialized Celery workers for audio analysis, source separation, ASR, and semantic processing

## Project Structure

```
/apps
  /api              ← FastAPI backend (main)
  /web              ← Next.js frontend (TODO)
  /worker-audio     ← Celery worker for audio analysis (TODO)
  /worker-semantic  ← Celery worker for semantic processing (TODO)
/packages
  /domain           ← Pure domain models
  /contracts        ← API schemas
  /test_fixtures    ← Test factories
/docs
  *.md              ← Documentation and ADRs
/tests
  /unit             ← Unit tests
  /integration      ← Integration tests
  /bdd              ← BDD scenarios
  /e2e              ← End-to-end tests (TODO)
```

## Phase-by-Phase Implementation

### Phase 1: ✅ Architecture & Planning (COMPLETED)

- [x] Domain models and business rules
- [x] API contracts and schemas
- [x] Database models and RLS policies
- [x] FastAPI setup and middleware
- [x] Celery task definitions
- [x] BDD scenarios
- [x] Unit tests for domain rules
- [x] Documentation and ADRs

**Status**: Core architecture in place. Ready for Phase 2.

### Phase 2: Backend Implementation (CURRENT)

**Objectives**:
1. Complete FastAPI API implementation
2. Implement all CRUD endpoints
3. Add authentication and authorization
4. Implement RLS enforcement
5. Add comprehensive error handling
6. Write integration tests

**Tasks**:

#### 2.1 Complete Songs Router
- [x] `POST /songs/import-youtube` - Import from YouTube
- [ ] `GET /analyses/{analysis_id}` - Poll analysis status
- [ ] `GET /songs/{song_id}` - Get song details
- [ ] `GET /organizations/{org_id}/library` - List songs

**Implementation**:
```python
# apps/api/routers/songs.py
# Already has basic structure, needs:
# - RLS context enforcement
# - Async database operations
# - Error handling
# - Celery task dispatch
```

#### 2.2 Implement Arrangements Router
- [ ] `POST /songs/{song_id}/arrangements` - Create arrangement
- [ ] `GET /arrangements/{arrangement_id}` - Get arrangement
- [ ] `PATCH /arrangements/{arrangement_id}/sections` - Edit sections
- [ ] `PATCH /arrangements/{arrangement_id}/chords` - Edit chords
- [ ] `POST /arrangements/{arrangement_id}/publish` - Publish arrangement

**Key Rules**:
- Never overwrite raw analysis results
- Only leaders can publish
- Version tracking on edits

#### 2.3 Implement Setlists Router
- [ ] `POST /setlists` - Create setlist
- [ ] `GET /setlists/{setlist_id}` - Get setlist
- [ ] `POST /setlists/{setlist_id}/items` - Add song
- [ ] `PATCH /setlist-items/{item_id}` - Reorder/edit
- [ ] `POST /setlists/{setlist_id}/live/start` - Start live mode
- [ ] `GET /setlists/{setlist_id}/live/status` - Live status

**Key Rules**:
- Executed setlists are immutable
- Items reference arrangements (not raw songs)
- Preserve historical accuracy

#### 2.4 Authentication & Authorization
- [ ] JWT token generation and validation
- [ ] User authentication endpoint
- [ ] Role-based access control
- [ ] Organization context middleware
- [ ] RLS context enforcement

**Implementation**:
```python
# apps/api/auth.py - Already has utilities
# Need to integrate into routers:
# - Extract token from Authorization header
# - Validate token
# - Set RLS context
# - Check permissions
```

#### 2.5 Database Migrations
- [ ] Create Alembic migration environment
- [ ] Generate initial migration from models
- [ ] Create RLS policies migration
- [ ] Test migrations locally

**Commands**:
```bash
cd apps/api
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

#### 2.6 Error Handling & Validation
- [ ] Comprehensive error responses
- [ ] Input validation with Pydantic
- [ ] HTTP status code consistency
- [ ] Logging and observability

#### 2.7 Integration Tests
- [ ] Test all CRUD operations
- [ ] Test RLS enforcement
- [ ] Test permission checks
- [ ] Test error cases

### Phase 3: Workers Implementation (FUTURE)

**Objectives**: Implement Celery workers for async analysis pipeline

**Tasks**:
1. Audio Analysis Worker (Essentia)
   - BPM detection
   - Key detection
   - Feature extraction
   - Confidence scoring

2. Source Separation Worker (Demucs)
   - Vocal/instrumental separation
   - Stem extraction

3. Speech Worker (Whisper)
   - Automatic speech recognition
   - Timestamp alignment
   - Speech vs. singing detection

4. Semantic Worker (LLM)
   - Section labeling
   - Output normalization
   - Confidence scoring

### Phase 4: Frontend Implementation (FUTURE)

**Objectives**: Build Next.js frontend with React components

**Key Pages**:
1. Library - Browse songs and arrangements
2. Import - YouTube URL import with progress
3. Editor - Arrangement editing interface
4. Setlist Manager - Create and manage setlists
5. Live Mode - Stage presentation view
6. Dashboard - Operational metrics

### Phase 5: Deployment & Operations (FUTURE)

**Objectives**: Deploy to production with monitoring

**Tasks**:
1. Docker containerization
2. Kubernetes deployment
3. Database backups and recovery
4. Monitoring and alerting
5. CI/CD pipeline

## Development Workflow

### Local Development Setup

```bash
# 1. Install dependencies
cd apps/api
pip install -r requirements.txt

# 2. Start infrastructure
docker-compose up -d

# 3. Run migrations
alembic upgrade head

# 4. Start API
python -m uvicorn main:app --reload

# 5. In another terminal, start Celery worker
celery -A celery_tasks worker --loglevel=info

# 6. In another terminal, start Celery beat (scheduler)
celery -A celery_tasks beat --loglevel=info
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=apps/api --cov-report=html
```

### Database Operations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## Key Implementation Patterns

### 1. RLS Context Enforcement

```python
# In every endpoint that accesses data:
@router.get("/songs/{song_id}")
async def get_song(song_id: UUID, db: AsyncSession, org_id: str):
    # Set RLS context
    await set_rls_context(db, org_id)
    
    # Query will be automatically filtered by RLS
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()
```

### 2. Permission Checking

```python
# Check permissions before operations
if not PermissionChecker.can_publish_arrangement(user.role):
    raise HTTPException(status_code=403, detail="Permission denied")

# Or use decorator
@require_permission("publish_arrangement")
async def publish_arrangement(arrangement_id: UUID):
    ...
```

### 3. Async Database Operations

```python
# Use async context managers
async with db.begin():
    # Create entities
    song = await SongQueries.create_song(db, ...)
    analysis = await AnalysisQueries.create_analysis(db, ...)
    
    # Commit on context exit
```

### 4. Error Handling

```python
try:
    # Operation
    result = await db.execute(query)
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Testing Strategy

### Unit Tests
- Domain rules (transposition, versioning, permissions)
- Utility functions
- Validation logic

### Integration Tests
- API endpoints with database
- RLS enforcement
- Permission checks
- Error cases

### BDD Tests
- Complete user workflows
- Multi-step scenarios
- Business rule validation

### E2E Tests
- Full browser-based testing
- User interactions
- Visual regression

## Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Docker images built and pushed
- [ ] Kubernetes manifests created
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested
- [ ] Load testing completed

## Common Issues & Solutions

### Issue: RLS policies not working
**Solution**: Ensure `app.set_organization_context()` is called before queries

### Issue: Celery tasks not executing
**Solution**: Check Redis connection and Celery worker logs

### Issue: Database migrations failing
**Solution**: Check for conflicting migrations and run `alembic current`

### Issue: CORS errors in frontend
**Solution**: Update `cors_origins` in `config.py`

## Next Steps

1. Complete Phase 2 (Backend API)
2. Implement Phase 3 (Workers)
3. Build Phase 4 (Frontend)
4. Deploy Phase 5 (Production)

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Celery Docs: https://docs.celeryproject.org/
- PostgreSQL RLS: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Pydantic: https://docs.pydantic.dev/
