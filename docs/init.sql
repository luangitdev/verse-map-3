-- Initialize Music Analysis Platform Database with RLS

-- Create app schema for session variables
CREATE SCHEMA IF NOT EXISTS app;

-- Create session variable for organization context
CREATE OR REPLACE FUNCTION app.set_organization_context(org_id UUID) RETURNS void AS $$
BEGIN
  PERFORM set_config('app.current_organization_id', org_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;
ALTER TABLE song_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE song_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE song_sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE lyrics_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE chord_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE arrangements ENABLE ROW LEVEL SECURITY;
ALTER TABLE setlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE setlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for organizations (admin only)
CREATE POLICY org_admin_only ON organizations
  FOR ALL USING (
    -- Allow if user is admin (simplified; in production, check user role)
    true
  );

-- RLS Policies for users
CREATE POLICY user_org_isolation ON users
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY user_org_isolation_insert ON users
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- RLS Policies for teams
CREATE POLICY team_org_isolation ON teams
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY team_org_isolation_insert ON teams
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- RLS Policies for team_members (via team)
CREATE POLICY team_member_org_isolation ON team_members
  USING (
    team_id IN (
      SELECT id FROM teams 
      WHERE organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for songs
CREATE POLICY song_org_isolation ON songs
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY song_org_isolation_insert ON songs
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- RLS Policies for song_sources (via song)
CREATE POLICY song_source_org_isolation ON song_sources
  USING (
    song_id IN (
      SELECT id FROM songs 
      WHERE organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for song_analyses (via song)
CREATE POLICY song_analysis_org_isolation ON song_analyses
  USING (
    song_id IN (
      SELECT id FROM songs 
      WHERE organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for song_sections (via analysis → song)
CREATE POLICY song_section_org_isolation ON song_sections
  USING (
    analysis_id IN (
      SELECT sa.id FROM song_analyses sa
      JOIN songs s ON sa.song_id = s.id
      WHERE s.organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for lyrics_lines (via analysis → song)
CREATE POLICY lyrics_line_org_isolation ON lyrics_lines
  USING (
    analysis_id IN (
      SELECT sa.id FROM song_analyses sa
      JOIN songs s ON sa.song_id = s.id
      WHERE s.organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for chord_charts (via analysis → song)
CREATE POLICY chord_chart_org_isolation ON chord_charts
  USING (
    analysis_id IN (
      SELECT sa.id FROM song_analyses sa
      JOIN songs s ON sa.song_id = s.id
      WHERE s.organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for arrangements
CREATE POLICY arrangement_org_isolation ON arrangements
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY arrangement_org_isolation_insert ON arrangements
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- RLS Policies for setlists
CREATE POLICY setlist_org_isolation ON setlists
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY setlist_org_isolation_insert ON setlists
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- RLS Policies for setlist_items (via setlist)
CREATE POLICY setlist_item_org_isolation ON setlist_items
  USING (
    setlist_id IN (
      SELECT id FROM setlists 
      WHERE organization_id = (current_setting('app.current_organization_id')::UUID)
    )
  );

-- RLS Policies for audit_logs
CREATE POLICY audit_log_org_isolation ON audit_logs
  USING (organization_id = (current_setting('app.current_organization_id')::UUID));

CREATE POLICY audit_log_org_isolation_insert ON audit_logs
  WITH CHECK (organization_id = (current_setting('app.current_organization_id')::UUID));

-- Create indexes for performance
CREATE INDEX idx_song_organization ON songs(organization_id);
CREATE INDEX idx_arrangement_organization ON arrangements(organization_id);
CREATE INDEX idx_setlist_organization ON setlists(organization_id);
CREATE INDEX idx_audit_organization ON audit_logs(organization_id);
CREATE INDEX idx_user_organization ON users(organization_id);
CREATE INDEX idx_team_organization ON teams(organization_id);
CREATE INDEX idx_analysis_song ON song_analyses(song_id);
CREATE INDEX idx_analysis_phase ON song_analyses(phase);
CREATE INDEX idx_section_analysis ON song_sections(analysis_id);
CREATE INDEX idx_lyrics_analysis ON lyrics_lines(analysis_id);
CREATE INDEX idx_chord_analysis ON chord_charts(analysis_id);
CREATE INDEX idx_setlist_item_setlist ON setlist_items(setlist_id);
CREATE INDEX idx_setlist_item_arrangement ON setlist_items(arrangement_id);
