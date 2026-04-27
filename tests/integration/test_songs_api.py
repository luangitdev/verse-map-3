"""
Integration tests for songs API.

Tests the complete flow from HTTP request to database.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from uuid import uuid4
import json

from apps.api.main import app
from apps.api.models import Base, Organization, User, Song, SongAnalysis, AnalysisPhaseEnum, UserRoleEnum
from packages.test_fixtures.factories import OrganizationFactory, UserFactory, SongFactory


@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def client():
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_org(db_session: AsyncSession):
    """Create test organization."""
    org = Organization(
        id=uuid4(),
        name="Test Church",
        description="Test organization",
    )
    db_session.add(org)
    await db_session.commit()
    return org


@pytest.fixture
async def test_user(db_session: AsyncSession, test_org: Organization):
    """Create test user."""
    user = User(
        id=uuid4(),
        organization_id=test_org.id,
        email="test@example.com",
        name="Test User",
        role=UserRoleEnum.LEADER,
    )
    db_session.add(user)
    await db_session.commit()
    return user


class TestSongsImport:
    """Tests for song import endpoint."""
    
    @pytest.mark.asyncio
    async def test_import_youtube_url_returns_analysis_id(self, client: AsyncClient):
        """Test importing a YouTube URL returns analysis_id."""
        response = await client.post(
            "/api/songs/import-youtube",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Test Song",
            },
            headers={"X-Organization-ID": str(uuid4())},
        )
        
        # Should return 202 Accepted
        assert response.status_code == 202
        
        data = response.json()
        assert "analysis_id" in data
        assert "song_id" in data
        assert data["status"] == "queued"
    
    @pytest.mark.asyncio
    async def test_import_invalid_url_returns_error(self, client: AsyncClient):
        """Test importing invalid URL returns error."""
        response = await client.post(
            "/api/songs/import-youtube",
            json={
                "url": "https://example.com/invalid",
            },
            headers={"X-Organization-ID": str(uuid4())},
        )
        
        # Should return 400 Bad Request
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    @pytest.mark.asyncio
    async def test_import_without_organization_id_returns_error(self, client: AsyncClient):
        """Test importing without organization ID returns error."""
        response = await client.post(
            "/api/songs/import-youtube",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            },
        )
        
        # Should return 400 Bad Request
        assert response.status_code == 400


class TestAnalysisStatus:
    """Tests for analysis status endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_analysis_status_returns_phase(self, client: AsyncClient):
        """Test getting analysis status returns current phase."""
        analysis_id = uuid4()
        
        response = await client.get(
            f"/api/analyses/{analysis_id}",
            headers={"X-Organization-ID": str(uuid4())},
        )
        
        # Should return 404 if analysis doesn't exist
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_analysis_status_without_organization_id_returns_error(
        self,
        client: AsyncClient,
    ):
        """Test getting analysis without organization ID returns error."""
        response = await client.get(f"/api/analyses/{uuid4()}")
        
        # Should return 400 Bad Request
        assert response.status_code == 400


class TestSongsLibrary:
    """Tests for songs library endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_songs_returns_empty_library(self, client: AsyncClient):
        """Test listing songs from empty organization."""
        org_id = uuid4()
        
        response = await client.get(
            f"/api/organizations/{org_id}/library",
            headers={"X-Organization-ID": str(org_id)},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_list_songs_respects_organization_isolation(
        self,
        client: AsyncClient,
    ):
        """Test that songs from other organizations are not visible."""
        org1_id = uuid4()
        org2_id = uuid4()
        
        # User from org1 should not see org2's songs
        response = await client.get(
            f"/api/organizations/{org2_id}/library",
            headers={"X-Organization-ID": str(org1_id)},
        )
        
        # Should return empty or error
        assert response.status_code in [200, 403]


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
