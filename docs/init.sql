-- Initialize database for Music Analysis Platform
-- This script creates the schema and helper functions
-- Tables are created by SQLAlchemy ORM when the API starts

-- Create app schema for session variables
CREATE SCHEMA IF NOT EXISTS app;

-- Create session variable for organization context
CREATE OR REPLACE FUNCTION app.set_organization_context(org_id UUID) RETURNS void AS $$
BEGIN
  PERFORM set_config('app.current_organization_id', org_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- Create function to get current organization ID
CREATE OR REPLACE FUNCTION app.get_organization_context() RETURNS UUID AS $$
BEGIN
  RETURN current_setting('app.current_organization_id')::UUID;
EXCEPTION WHEN OTHERS THEN
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create function to check if user is in organization
CREATE OR REPLACE FUNCTION app.user_in_organization(user_org_id UUID) RETURNS boolean AS $$
BEGIN
  RETURN user_org_id = app.get_organization_context();
END;
$$ LANGUAGE plpgsql;

-- Grant schema permissions
GRANT USAGE ON SCHEMA app TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA app TO postgres;

-- Note: RLS policies and table creation are handled by the FastAPI application
-- This ensures consistency between the ORM schema and database schema
