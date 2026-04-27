"""
Comprehensive API integration tests.

Tests complete workflows across all endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from uuid import uuid4
from datetime import datetime

from apps.api.main import app
from apps.api.models import (
    Base, Organization, User, Song, SongAnalysis, Arrangement,
    Setlist, SetlistItem, UserRoleEnum, AnalysisPhaseEnum, SetlistStatusEnum
)


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
async def test_data(db_session: AsyncSession):
    """Create test data."""
    # Organization
    org_id = uuid4()
    org = Organization(id=org_id, name="Test Church")
    db_session.add(org)
    
    # Leader user
    leader_id = uuid4()
    leader = User(
        id=leader_id,
        organization_id=org_id,
        email="leader@test.com",
        name="Leader",
        role=UserRoleEnum.LEADER,
    )
    db_session.add(leader)
    
    # Musician user
    musician_id = uuid4()
    musician = User(
        id=musician_id,
        organization_id=org_id,
        email="musician@test.com",
        name="Musician",
        role=UserRoleEnum.MUSICIAN,
    )
    db_session.add(musician)
    
    # Song
    song_id = uuid4()
    song = Song(
        id=song_id,
        organization_id=org_id,
        title="Amazing Grace",
        artist="John Newton",
        duration_seconds=240,
    )
    db_session.add(song)
    
    # Analysis
    analysis_id = uuid4()
    analysis = SongAnalysis(
        id=analysis_id,
        song_id=song_id,
        phase=AnalysisPhaseEnum.READY,
        bpm=90.0,
        bpm_confidence=0.95,
        key="G major",
        key_confidence=0.90,
    )
    db_session.add(analysis)
    
    await db_session.commit()
    
    return {
        "org_id": org_id,
        "leader_id": leader_id,
        "leader": leader,
        "musician_id": musician_id,
        "musician": musician,
        "song_id": song_id,
        "song": song,
        "analysis_id": analysis_id,
        "analysis": analysis,
    }


class TestArrangementsWorkflow:
    """Tests for arrangement creation and editing workflow."""
    
    @pytest.mark.asyncio
    async def test_create_arrangement(self, client: AsyncClient, test_data):
        """Test creating an arrangement."""
        response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={
                "name": "Original Arrangement",
                "key": "G major",
                "sections": [],
                "notes": "Beautiful hymn",
            },
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Original Arrangement"
        assert data["key"] == "G major"
        assert data["published"] is False
    
    @pytest.mark.asyncio
    async def test_list_arrangements_for_song(self, client: AsyncClient, test_data):
        """Test listing arrangements for a song."""
        # Create arrangement first
        await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Arrangement 1", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        # List arrangements
        response = await client.get(
            f"/api/songs/{test_data['song_id']}/arrangements",
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_musician_cannot_publish_arrangement(self, client: AsyncClient, test_data):
        """Test that musicians cannot publish arrangements."""
        # Create arrangement
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Try to publish as musician
        response = await client.post(
            f"/api/arrangements/{arrangement_id}/publish",
            headers={
                "X-Organization-ID": str(test_data["org_id"]),
                "X-User-Role": "musician",
            },
        )
        
        # Should be forbidden
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_leader_can_publish_arrangement(self, client: AsyncClient, test_data):
        """Test that leaders can publish arrangements."""
        # Create arrangement
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Publish as leader
        response = await client.post(
            f"/api/arrangements/{arrangement_id}/publish",
            headers={
                "X-Organization-ID": str(test_data["org_id"]),
                "X-User-Role": "leader",
            },
        )
        
        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["published"] is True


class TestSetlistsWorkflow:
    """Tests for setlist creation and management workflow."""
    
    @pytest.mark.asyncio
    async def test_create_setlist(self, client: AsyncClient, test_data):
        """Test creating a setlist."""
        response = await client.post(
            "/api/setlists",
            json={"name": "Sunday Service"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sunday Service"
        assert data["status"] == "draft"
    
    @pytest.mark.asyncio
    async def test_add_arrangement_to_setlist(self, client: AsyncClient, test_data):
        """Test adding an arrangement to a setlist."""
        # Create and publish arrangement
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Publish it
        await client.post(
            f"/api/arrangements/{arrangement_id}/publish",
            headers={
                "X-Organization-ID": str(test_data["org_id"]),
                "X-User-Role": "leader",
            },
        )
        
        # Create setlist
        setlist_response = await client.post(
            "/api/setlists",
            json={"name": "Sunday Service"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        setlist_id = setlist_response.json()["id"]
        
        # Add arrangement to setlist
        response = await client.post(
            f"/api/setlists/{setlist_id}/items",
            json={
                "arrangement_id": arrangement_id,
                "key": "G major",
                "notes": "Start with this song",
            },
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["arrangement_id"] == arrangement_id
    
    @pytest.mark.asyncio
    async def test_cannot_add_unpublished_arrangement_to_setlist(
        self,
        client: AsyncClient,
        test_data,
    ):
        """Test that unpublished arrangements cannot be added to setlists."""
        # Create unpublished arrangement
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Create setlist
        setlist_response = await client.post(
            "/api/setlists",
            json={"name": "Sunday Service"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        setlist_id = setlist_response.json()["id"]
        
        # Try to add unpublished arrangement
        response = await client.post(
            f"/api/setlists/{setlist_id}/items",
            json={
                "arrangement_id": arrangement_id,
                "key": "G major",
            },
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        # Should fail
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_start_live_mode(self, client: AsyncClient, test_data):
        """Test starting live mode for a setlist."""
        # Create setlist
        setlist_response = await client.post(
            "/api/setlists",
            json={"name": "Sunday Service"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        setlist_id = setlist_response.json()["id"]
        
        # Start live mode
        response = await client.post(
            f"/api/setlists/{setlist_id}/live/start",
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "live"
    
    @pytest.mark.asyncio
    async def test_cannot_modify_executed_setlist(self, client: AsyncClient, test_data):
        """Test that executed setlists cannot be modified."""
        # Create setlist
        setlist_response = await client.post(
            "/api/setlists",
            json={"name": "Sunday Service"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        setlist_id = setlist_response.json()["id"]
        
        # Start live mode (marks as executed)
        await client.post(
            f"/api/setlists/{setlist_id}/live/start",
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        # Try to add item
        response = await client.post(
            f"/api/setlists/{setlist_id}/items",
            json={
                "arrangement_id": uuid4(),
                "key": "G major",
            },
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        # Should fail
        assert response.status_code == 400


class TestMultiTenantIsolation:
    """Tests for multi-tenant data isolation."""
    
    @pytest.mark.asyncio
    async def test_cannot_access_other_org_songs(self, client: AsyncClient, test_data):
        """Test that users cannot access songs from other organizations."""
        other_org_id = uuid4()
        
        # Try to access song from different org
        response = await client.get(
            f"/api/songs/{test_data['song_id']}",
            headers={"X-Organization-ID": str(other_org_id)},
        )
        
        # Should be forbidden or return 404
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_cannot_access_other_org_arrangements(
        self,
        client: AsyncClient,
        test_data,
    ):
        """Test that users cannot access arrangements from other organizations."""
        other_org_id = uuid4()
        
        # Create arrangement in test org
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Try to access from different org
        response = await client.get(
            f"/api/arrangements/{arrangement_id}",
            headers={"X-Organization-ID": str(other_org_id)},
        )
        
        # Should be forbidden or return 404
        assert response.status_code in [403, 404]


class TestAuditLogging:
    """Tests for audit logging."""
    
    @pytest.mark.asyncio
    async def test_arrangement_creation_logged(self, client: AsyncClient, test_data):
        """Test that arrangement creation is logged."""
        # Create arrangement
        response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        
        # Should succeed and be logged
        assert response.status_code == 201
        # TODO: Verify audit log in database
    
    @pytest.mark.asyncio
    async def test_arrangement_publishing_logged(self, client: AsyncClient, test_data):
        """Test that arrangement publishing is logged."""
        # Create and publish arrangement
        arr_response = await client.post(
            f"/api/songs/{test_data['song_id']}/arrangements",
            json={"name": "Test", "key": "G major"},
            headers={"X-Organization-ID": str(test_data["org_id"])},
        )
        arrangement_id = arr_response.json()["id"]
        
        # Publish
        response = await client.post(
            f"/api/arrangements/{arrangement_id}/publish",
            headers={
                "X-Organization-ID": str(test_data["org_id"]),
                "X-User-Role": "leader",
            },
        )
        
        # Should succeed and be logged
        assert response.status_code == 200
        # TODO: Verify audit log in database


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
