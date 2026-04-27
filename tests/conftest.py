"""
Pytest Configuration and Shared Fixtures

Provides common test utilities and fixtures for all tests.
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any


# ============================================================================
# Fixtures for Domain Models
# ============================================================================

@pytest.fixture
def sample_organization() -> Dict[str, Any]:
    """Create a sample organization"""
    return {
        "id": "org-1",
        "name": "Grace Church",
        "created_at": datetime.now(),
        "owner_id": "user-1",
    }


@pytest.fixture
def sample_user(sample_organization) -> Dict[str, Any]:
    """Create a sample user"""
    return {
        "id": "user-1",
        "org_id": sample_organization["id"],
        "email": "leader@gracechurch.com",
        "name": "John Leader",
        "role": "leader",
        "created_at": datetime.now(),
    }


@pytest.fixture
def sample_song() -> Dict[str, Any]:
    """Create a sample song"""
    return {
        "id": "song-1",
        "org_id": "org-1",
        "title": "Amazing Grace",
        "artist": "John Newton",
        "duration": 213,
        "source_url": "https://www.youtube.com/watch?v=...",
        "created_at": datetime.now(),
    }


@pytest.fixture
def sample_analysis() -> Dict[str, Any]:
    """Create a sample song analysis"""
    return {
        "id": "analysis-1",
        "song_id": "song-1",
        "status": "ready",
        "bpm": 113,
        "bpm_confidence": 0.92,
        "key": "D major",
        "key_confidence": 0.88,
        "sections": [
            {"name": "Intro", "start": 0, "end": 15},
            {"name": "Verse 1", "start": 15, "end": 45},
            {"name": "Chorus", "start": 45, "end": 75},
        ],
        "chords": [
            {"timestamp": 15, "chord": "D", "confidence": 0.85},
            {"timestamp": 30, "chord": "A", "confidence": 0.82},
        ],
        "created_at": datetime.now(),
    }


@pytest.fixture
def sample_arrangement(sample_song, sample_analysis) -> Dict[str, Any]:
    """Create a sample arrangement"""
    return {
        "id": "arr-1",
        "org_id": "org-1",
        "song_id": sample_song["id"],
        "analysis_id": sample_analysis["id"],
        "version": 1,
        "is_published": False,
        "created_by": "user-1",
        "sections": [
            {"id": "sec-1", "name": "Verse 1", "start": 15, "end": 45},
            {"id": "sec-2", "name": "Chorus", "start": 45, "end": 75},
        ],
        "chords": [
            {"section_id": "sec-1", "chord": "D", "timestamp": 15},
            {"section_id": "sec-1", "chord": "A", "timestamp": 30},
        ],
        "created_at": datetime.now(),
    }


@pytest.fixture
def sample_setlist(sample_arrangement) -> Dict[str, Any]:
    """Create a sample setlist"""
    return {
        "id": "setlist-1",
        "org_id": "org-1",
        "name": "Sunday Worship Service",
        "status": "draft",
        "created_by": "user-1",
        "items": [
            {
                "id": "item-1",
                "arrangement_id": sample_arrangement["id"],
                "position": 1,
                "key": "D major",
                "notes": "Start with acoustic intro",
            },
        ],
        "created_at": datetime.now(),
    }


# ============================================================================
# Fixtures for API Testing
# ============================================================================

@pytest.fixture
def api_headers() -> Dict[str, str]:
    """Create API request headers"""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token-123",
    }


@pytest.fixture
def api_client():
    """Mock API client"""
    class MockAPIClient:
        def __init__(self):
            self.base_url = "http://localhost:8000/api"
            
        def get(self, endpoint: str, **kwargs):
            return {"status": "success", "data": {}}
        
        def post(self, endpoint: str, data: Dict, **kwargs):
            return {"status": "success", "data": data}
        
        def put(self, endpoint: str, data: Dict, **kwargs):
            return {"status": "success", "data": data}
        
        def delete(self, endpoint: str, **kwargs):
            return {"status": "success"}
    
    return MockAPIClient()


# ============================================================================
# Fixtures for Database Testing
# ============================================================================

@pytest.fixture
def db_session():
    """Mock database session"""
    class MockDBSession:
        def __init__(self):
            self.data = {}
        
        def query(self, model):
            return self
        
        def filter(self, condition):
            return self
        
        def first(self):
            return None
        
        def all(self):
            return []
        
        def add(self, obj):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def close(self):
            pass
    
    return MockDBSession()


# ============================================================================
# Fixtures for Authentication Testing
# ============================================================================

@pytest.fixture
def auth_token() -> str:
    """Create a test JWT token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEiLCJvcmdfaWQiOiJvcmctMSIsInJvbGUiOiJsZWFkZXIifQ.test"


@pytest.fixture
def auth_headers(auth_token) -> Dict[str, str]:
    """Create authenticated request headers"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }


# ============================================================================
# Fixtures for Celery Testing
# ============================================================================

@pytest.fixture
def celery_config():
    """Configure Celery for testing"""
    return {
        "broker_url": "redis://localhost:6379/0",
        "result_backend": "redis://localhost:6379/0",
        "task_always_eager": True,
        "task_eager_propagates": True,
    }


@pytest.fixture
def celery_task_mock():
    """Mock Celery task"""
    class MockTask:
        def __init__(self, task_id: str = "task-1"):
            self.id = task_id
            self.status = "PENDING"
            self.result = None
        
        def get(self):
            return self.result
        
        def ready(self):
            return self.status in ["SUCCESS", "FAILURE"]
    
    return MockTask()


# ============================================================================
# Fixtures for File Testing
# ============================================================================

@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a temporary audio file"""
    audio_file = tmp_path / "test_audio.mp3"
    audio_file.write_bytes(b"fake audio data")
    return audio_file


@pytest.fixture
def sample_video_file(tmp_path):
    """Create a temporary video file"""
    video_file = tmp_path / "test_video.mp4"
    video_file.write_bytes(b"fake video data")
    return video_file


# ============================================================================
# Utility Functions
# ============================================================================

def create_test_user(org_id: str, role: str = "musician") -> Dict[str, Any]:
    """Create a test user"""
    return {
        "id": f"user-{org_id}-{role}",
        "org_id": org_id,
        "email": f"{role}@example.com",
        "role": role,
        "created_at": datetime.now(),
    }


def create_test_song(org_id: str, title: str = "Test Song") -> Dict[str, Any]:
    """Create a test song"""
    return {
        "id": f"song-{org_id}-{title.lower().replace(' ', '-')}",
        "org_id": org_id,
        "title": title,
        "artist": "Test Artist",
        "duration": 180,
        "created_at": datetime.now(),
    }


def create_test_arrangement(org_id: str, song_id: str, is_published: bool = False) -> Dict[str, Any]:
    """Create a test arrangement"""
    return {
        "id": f"arr-{song_id}",
        "org_id": org_id,
        "song_id": song_id,
        "version": 1,
        "is_published": is_published,
        "sections": [],
        "chords": [],
        "created_at": datetime.now(),
    }


def create_test_setlist(org_id: str, items: List[str] = None) -> Dict[str, Any]:
    """Create a test setlist"""
    return {
        "id": f"setlist-{org_id}",
        "org_id": org_id,
        "name": "Test Setlist",
        "status": "draft",
        "items": items or [],
        "created_at": datetime.now(),
    }


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set test environment variables
    import os
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    
    yield
    
    # Cleanup after tests
    pass
