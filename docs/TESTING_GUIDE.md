# Testing Guide

Comprehensive guide for testing the Music Analysis Platform.

## Overview

The project uses multiple testing strategies:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test components working together
- **E2E Tests**: Test complete user workflows
- **BDD Tests**: Test business requirements in Gherkin format

## Test Structure

```
tests/
├── unit/
│   ├── test_domain_models.py      # Domain logic tests
│   ├── test_business_rules.py     # Business rule tests
│   └── test_utils.py              # Utility function tests
├── integration/
│   ├── test_api_complete.py       # API endpoint tests
│   ├── test_songs_api.py          # Songs API tests
│   └── test_database.py           # Database tests
├── e2e/
│   ├── test_workflows.py          # Complete workflows
│   └── test_user_journeys.py      # User journeys
├── bdd/
│   └── features.feature           # Gherkin scenarios
├── conftest.py                    # Shared fixtures
└── __init__.py
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Category

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v

# BDD tests only
pytest tests/bdd/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_domain_models.py -v
```

### Run Specific Test

```bash
pytest tests/unit/test_domain_models.py::TestAnalysisPhaseTransition::test_valid_phase_sequence -v
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Skip slow tests
pytest -m "not slow"
```

### Run with Coverage

```bash
pytest tests/ --cov=apps --cov-report=html
```

### Run with Parallel Execution

```bash
pytest tests/ -n auto
```

## Test Categories

### Unit Tests

Test individual functions and classes without external dependencies.

**File**: `tests/unit/test_domain_models.py`

**Examples**:
- Analysis phase transitions
- Arrangement versioning rules
- Setlist business rules
- User permissions
- Transposition logic
- Confidence scoring
- Multi-tenancy isolation
- Audit logging

**Run**:
```bash
pytest tests/unit/ -v
```

### Integration Tests

Test components working together with database and API.

**Files**:
- `tests/integration/test_api_complete.py`
- `tests/integration/test_songs_api.py`

**Examples**:
- Song import API
- Analysis status polling
- Arrangement CRUD operations
- Setlist management
- User authentication
- Permission enforcement

**Run**:
```bash
pytest tests/integration/ -v
```

### E2E Tests

Test complete user workflows from start to finish.

**File**: `tests/e2e/test_workflows.py`

**Workflows**:
1. **Import & Analyze**: YouTube import → analysis → ready
2. **Arrangement Creation**: Create → edit → publish
3. **Setlist Management**: Create → add songs → execute
4. **Collaboration**: Leader publishes → musician views
5. **Error Recovery**: Failure → retry → success
6. **Performance**: Large library navigation

**Run**:
```bash
pytest tests/e2e/ -v
```

### BDD Tests

Test business requirements in human-readable Gherkin format.

**File**: `tests/bdd/features.feature`

**Scenarios**:
- Import song from YouTube
- Analyze music automatically
- Create and edit arrangements
- Manage setlists
- Execute live mode
- Manage users and permissions

**Run**:
```bash
pytest tests/bdd/ -v
```

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

### Domain Fixtures

```python
@pytest.fixture
def sample_organization():
    """Create a sample organization"""
    
@pytest.fixture
def sample_user(sample_organization):
    """Create a sample user"""
    
@pytest.fixture
def sample_song():
    """Create a sample song"""
    
@pytest.fixture
def sample_analysis():
    """Create a sample analysis"""
    
@pytest.fixture
def sample_arrangement(sample_song, sample_analysis):
    """Create a sample arrangement"""
    
@pytest.fixture
def sample_setlist(sample_arrangement):
    """Create a sample setlist"""
```

### API Fixtures

```python
@pytest.fixture
def api_headers():
    """Create API request headers"""
    
@pytest.fixture
def api_client():
    """Mock API client"""
```

### Auth Fixtures

```python
@pytest.fixture
def auth_token():
    """Create a test JWT token"""
    
@pytest.fixture
def auth_headers(auth_token):
    """Create authenticated request headers"""
```

### Utility Functions

```python
def create_test_user(org_id, role="musician"):
    """Create a test user"""
    
def create_test_song(org_id, title="Test Song"):
    """Create a test song"""
    
def create_test_arrangement(org_id, song_id, is_published=False):
    """Create a test arrangement"""
    
def create_test_setlist(org_id, items=None):
    """Create a test setlist"""
```

## Writing Tests

### Unit Test Example

```python
import pytest

class TestArrangementVersioning:
    """Test arrangement versioning rules"""
    
    def test_arrangement_versions_are_immutable(self):
        """Test that published arrangements cannot be modified"""
        arrangement = {
            "id": "arr-1",
            "is_published": True,
            "sections": [{"name": "Verse"}],
        }
        
        assert arrangement["is_published"] is True
```

### Integration Test Example

```python
@pytest.mark.integration
def test_import_song_api(api_client, auth_headers):
    """Test song import API"""
    response = api_client.post(
        "/songs/import",
        data={"url": "https://youtube.com/..."},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    assert response.json()["analysis_id"] is not None
```

### E2E Test Example

```python
@pytest.mark.e2e
def test_complete_workflow(sample_song, sample_arrangement):
    """Test complete import to setlist workflow"""
    # Step 1: Import
    # Step 2: Analyze
    # Step 3: Create arrangement
    # Step 4: Publish
    # Step 5: Add to setlist
    # Step 6: Execute
    
    assert final_result["status"] == "success"
```

## Mocking

### Mock API Client

```python
from unittest.mock import Mock, patch

@patch("requests.get")
def test_with_mock(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "value"}
    
    # Your test code
```

### Mock Database

```python
@pytest.fixture
def mock_db():
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db
```

### Mock Celery Task

```python
@patch("celery_app.send_task")
def test_celery_task(mock_send_task):
    mock_send_task.return_value.id = "task-123"
    
    # Your test code
```

## Test Coverage

### Generate Coverage Report

```bash
pytest tests/ --cov=apps --cov-report=html
open htmlcov/index.html
```

### Coverage Targets

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: 70%+ coverage
- **Overall**: 75%+ coverage

### Check Coverage

```bash
pytest tests/ --cov=apps --cov-report=term-missing
```

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class MusicAnalysisUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def import_song(self):
        self.client.post("/songs/import", json={
            "url": "https://youtube.com/..."
        })
    
    @task
    def list_songs(self):
        self.client.get("/songs")
```

Run:
```bash
locust -f tests/performance/locustfile.py
```

### Benchmark Tests

```python
import pytest

@pytest.mark.benchmark
def test_song_search_performance(benchmark):
    def search():
        # Search implementation
        pass
    
    result = benchmark(search)
    assert result is not None
```

Run:
```bash
pytest tests/ --benchmark-only
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
      
      redis:
        image: redis:7
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=apps
      - run: codecov
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -vv
```

### Show Print Statements

```bash
pytest tests/ -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Drop into Debugger

```bash
pytest tests/ --pdb
```

### Show Local Variables

```bash
pytest tests/ -l
```

## Best Practices

### 1. Test Naming

```python
# Good
def test_arrangement_cannot_be_edited_after_publishing():
    pass

# Bad
def test_arr():
    pass
```

### 2. Single Responsibility

```python
# Good - tests one thing
def test_bpm_detection_returns_confidence():
    pass

# Bad - tests multiple things
def test_analysis():
    pass
```

### 3. Arrange-Act-Assert

```python
def test_example():
    # Arrange
    arrangement = create_test_arrangement()
    
    # Act
    result = publish_arrangement(arrangement)
    
    # Assert
    assert result["is_published"] is True
```

### 4. Use Fixtures

```python
# Good
def test_with_fixture(sample_arrangement):
    assert sample_arrangement["id"] is not None

# Bad
def test_without_fixture():
    arrangement = {"id": "arr-1"}
    assert arrangement["id"] is not None
```

### 5. Test Edge Cases

```python
def test_empty_setlist():
    setlist = create_test_setlist(items=[])
    assert len(setlist["items"]) == 0

def test_large_setlist():
    items = [f"arr-{i}" for i in range(100)]
    setlist = create_test_setlist(items=items)
    assert len(setlist["items"]) == 100
```

## Troubleshooting

### Tests Failing Locally but Passing in CI

```bash
# Run with same Python version as CI
python3.11 -m pytest tests/

# Run with same environment
export ENVIRONMENT=test
pytest tests/
```

### Fixture Not Found

```bash
# Check conftest.py is in correct location
# Should be in tests/ directory

# Verify fixture name matches
@pytest.fixture
def my_fixture():
    pass

def test_example(my_fixture):  # Name must match
    pass
```

### Timeout Issues

```bash
# Increase timeout
pytest tests/ --timeout=300

# Or mark test as slow
@pytest.mark.slow
def test_slow_operation():
    pass
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/latest/fixture.html)
- [Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Mocking with unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
