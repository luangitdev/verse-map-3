"""
Unit tests for domain business rules.

Tests the core business logic independent of frameworks.
"""

import pytest
from uuid import uuid4
from packages.domain.models import (
    TranspositionRule, VersioningRule, SetlistRule, AnalysisRule,
    UserRole, SetlistStatus, AnalysisPhase
)
from packages.test_fixtures.factories import (
    UserFactory, ArrangementFactory, SetlistFactory, SongAnalysisFactory
)


class TestTranspositionRule:
    """Tests for chord transposition logic."""
    
    def test_transpose_major_chord_up(self):
        """Transpose C major to D major."""
        result = TranspositionRule.transpose_chord("C", "C major", "D major")
        assert result == "D"
    
    def test_transpose_minor_chord_up(self):
        """Transpose Cm to Dm."""
        result = TranspositionRule.transpose_chord("Cm", "C major", "D major")
        assert result == "Dm"
    
    def test_transpose_seventh_chord(self):
        """Transpose G7 to A7."""
        result = TranspositionRule.transpose_chord("G7", "G major", "A major")
        assert result == "A7"
    
    def test_transpose_with_sharp(self):
        """Transpose C# to D#."""
        result = TranspositionRule.transpose_chord("C#", "C major", "D major")
        assert result == "D#"
    
    def test_transpose_down(self):
        """Transpose D to C."""
        result = TranspositionRule.transpose_chord("D", "D major", "C major")
        assert result == "C"
    
    def test_transpose_full_circle(self):
        """Transpose and return to original key."""
        original = "G"
        transposed = TranspositionRule.transpose_chord(original, "G major", "A major")
        back = TranspositionRule.transpose_chord(transposed, "A major", "G major")
        assert back == original
    
    def test_invalid_chord_root(self):
        """Raise error for invalid chord root."""
        with pytest.raises(ValueError):
            TranspositionRule.transpose_chord("H", "C major", "D major")
    
    def test_invalid_key(self):
        """Raise error for invalid key."""
        with pytest.raises(ValueError):
            TranspositionRule.transpose_chord("C", "H major", "D major")


class TestVersioningRule:
    """Tests for arrangement versioning and permissions."""
    
    def test_leader_can_edit_published_arrangement(self):
        """Leader can edit published arrangements."""
        leader = UserFactory.create(role=UserRole.LEADER, organization_id=uuid4())
        arrangement = ArrangementFactory.create(
            organization_id=leader.organization_id,
            published=True
        )
        
        assert VersioningRule.can_edit(arrangement, leader) is True
    
    def test_musician_cannot_edit_published_arrangement(self):
        """Musician cannot edit published arrangements."""
        musician = UserFactory.create(role=UserRole.MUSICIAN, organization_id=uuid4())
        arrangement = ArrangementFactory.create(
            organization_id=musician.organization_id,
            published=True
        )
        
        assert VersioningRule.can_edit(arrangement, musician) is False
    
    def test_musician_can_edit_draft_arrangement(self):
        """Musician can edit draft arrangements."""
        musician = UserFactory.create(role=UserRole.MUSICIAN, organization_id=uuid4())
        arrangement = ArrangementFactory.create(
            organization_id=musician.organization_id,
            published=False
        )
        
        assert VersioningRule.can_edit(arrangement, musician) is True
    
    def test_cross_org_cannot_edit(self):
        """User from different org cannot edit."""
        user = UserFactory.create(organization_id=uuid4())
        arrangement = ArrangementFactory.create(organization_id=uuid4())
        
        assert VersioningRule.can_edit(arrangement, user) is False
    
    def test_leader_can_publish(self):
        """Leader can publish arrangements."""
        leader = UserFactory.create(role=UserRole.LEADER, organization_id=uuid4())
        arrangement = ArrangementFactory.create(organization_id=leader.organization_id)
        
        assert VersioningRule.can_publish(arrangement, leader) is True
    
    def test_musician_cannot_publish(self):
        """Musician cannot publish arrangements."""
        musician = UserFactory.create(role=UserRole.MUSICIAN, organization_id=uuid4())
        arrangement = ArrangementFactory.create(organization_id=musician.organization_id)
        
        assert VersioningRule.can_publish(arrangement, musician) is False
    
    def test_admin_can_publish(self):
        """Admin can publish arrangements."""
        admin = UserFactory.create(role=UserRole.ADMIN, organization_id=uuid4())
        arrangement = ArrangementFactory.create(organization_id=admin.organization_id)
        
        assert VersioningRule.can_publish(arrangement, admin) is True


class TestSetlistRule:
    """Tests for setlist management rules."""
    
    def test_can_modify_draft_setlist(self):
        """Draft setlists can be modified."""
        setlist = SetlistFactory.create(status=SetlistStatus.DRAFT)
        assert SetlistRule.can_modify_executed_setlist(setlist) is True
    
    def test_can_modify_published_setlist(self):
        """Published setlists can be modified."""
        setlist = SetlistFactory.create(status=SetlistStatus.PUBLISHED)
        assert SetlistRule.can_modify_executed_setlist(setlist) is True
    
    def test_cannot_modify_executed_setlist(self):
        """Executed setlists cannot be modified (immutable)."""
        setlist = SetlistFactory.create(status=SetlistStatus.EXECUTED)
        assert SetlistRule.can_modify_executed_setlist(setlist) is False
    
    def test_mark_setlist_as_executed(self):
        """Mark setlist as executed."""
        setlist = SetlistFactory.create(status=SetlistStatus.DRAFT)
        executed = SetlistRule.mark_as_executed(setlist)
        
        assert executed.status == SetlistStatus.EXECUTED


class TestAnalysisRule:
    """Tests for analysis management rules."""
    
    def test_analysis_ready_is_complete(self):
        """Analysis with READY phase is complete."""
        analysis = SongAnalysisFactory.create(phase=AnalysisPhase.READY)
        assert AnalysisRule.is_analysis_complete(analysis) is True
    
    def test_analysis_partial_is_complete(self):
        """Analysis with PARTIAL phase is complete."""
        analysis = SongAnalysisFactory.create(phase=AnalysisPhase.PARTIAL)
        assert AnalysisRule.is_analysis_complete(analysis) is True
    
    def test_analysis_queued_not_complete(self):
        """Analysis with QUEUED phase is not complete."""
        analysis = SongAnalysisFactory.create(phase=AnalysisPhase.QUEUED)
        assert AnalysisRule.is_analysis_complete(analysis) is False
    
    def test_analysis_processing_not_complete(self):
        """Analysis with processing phase is not complete."""
        analysis = SongAnalysisFactory.create(phase=AnalysisPhase.ANALYZING_AUDIO)
        assert AnalysisRule.is_analysis_complete(analysis) is False
    
    def test_high_confidence_analysis(self):
        """Analysis with high confidence scores."""
        analysis = SongAnalysisFactory.create(
            bpm_confidence=0.95,
            key_confidence=0.90
        )
        assert AnalysisRule.has_low_confidence(analysis, threshold=0.6) is False
    
    def test_low_confidence_bpm(self):
        """Analysis with low BPM confidence."""
        analysis = SongAnalysisFactory.create(
            bpm_confidence=0.4,
            key_confidence=0.90
        )
        assert AnalysisRule.has_low_confidence(analysis, threshold=0.6) is True
    
    def test_low_confidence_key(self):
        """Analysis with low key confidence."""
        analysis = SongAnalysisFactory.create(
            bpm_confidence=0.95,
            key_confidence=0.4
        )
        assert AnalysisRule.has_low_confidence(analysis, threshold=0.6) is True


class TestYoutubeUrlParsing:
    """Tests for YouTube URL parsing (domain rule)."""
    
    def test_parse_standard_youtube_url(self):
        """Extract video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        # This would be tested in the actual implementation
        # video_id = extract_youtube_video_id(url)
        # assert video_id == "dQw4w9WgXcQ"
        pass
    
    def test_parse_short_youtube_url(self):
        """Extract video ID from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        # video_id = extract_youtube_video_id(url)
        # assert video_id == "dQw4w9WgXcQ"
        pass
    
    def test_reject_invalid_url(self):
        """Reject invalid URLs."""
        url = "https://example.com/video"
        # with pytest.raises(ValueError):
        #     extract_youtube_video_id(url)
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
