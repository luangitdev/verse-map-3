Feature: Music Analysis Platform - Core Workflows

  Background:
    Given an authenticated user belongs to an active organization
    And the organization has a valid database context

  # ============================================================================
  # Feature: YouTube Import
  # ============================================================================

  Feature: Import song from YouTube URL
    Scenario: Successfully import a valid YouTube URL
      Given the user has a valid YouTube URL
      When the user submits the import request
      Then the system returns an analysis_id immediately
      And the status is "queued"
      And a song record is created in the database
      And a job is published to the analysis queue

    Scenario: Reject invalid YouTube URL
      Given the user has an invalid URL
      When the user submits the import request
      Then the system returns a validation error
      And no song or analysis record is created

    Scenario: Handle duplicate imports
      Given a song has already been imported from a YouTube URL
      When the user imports the same URL again
      Then the system returns the existing song_id
      And no duplicate song is created

  # ============================================================================
  # Feature: Analysis Pipeline
  # ============================================================================

  Feature: Async analysis pipeline
    Scenario: Complete analysis with musical metadata
      Given an analysis is in "queued" status
      And the pipeline has access to necessary artifacts
      When the workers complete processing
      Then the analysis status changes to "ready"
      And BPM is detected and saved
      And tonality is detected and saved
      And structure sections are generated
      And confidence scores are calculated

    Scenario: Handle analysis failure gracefully
      Given an analysis is in "processing" status
      When a worker fails (e.g., Demucs separation)
      Then the analysis is marked as "failed" or "partial"
      And the error is logged with phase and reason
      And the user is notified of the failure

    Scenario: Poll analysis status
      Given an analysis_id for a queued job
      When the user polls the status endpoint
      Then the system returns current phase and progress
      And the response includes confidence scores when available

  # ============================================================================
  # Feature: Arrangement Editing
  # ============================================================================

  Feature: Edit arrangement structure
    Scenario: Rename a section
      Given an arrangement with auto-detected sections
      When the user renames section 3 to "Bridge"
      Then the arrangement is updated
      And the raw analysis result remains unchanged
      And the version number is incremented

    Scenario: Mark section as speech
      Given an arrangement with an unlabeled section
      When the user marks the section as "Speech"
      Then the section type is updated
      And the arrangement reflects the change

    Scenario: Reorder sections
      Given an arrangement with multiple sections
      When the user reorders sections
      Then the order is persisted
      And the arrangement maintains consistency

    Scenario: Only leaders can publish arrangements
      Given an arrangement in draft status
      When a musician attempts to publish
      Then the system denies the action
      And the arrangement remains unpublished
      When a leader publishes the arrangement
      Then the status changes to published
      And the published_by field is set

  # ============================================================================
  # Feature: Chord Charts & Transposition
  # ============================================================================

  Feature: Chord chart management
    Scenario: Transpose arrangement to new key
      Given an arrangement in key "G major"
      When the user transposes to "A major"
      Then all chords are transposed correctly
      And the structure remains unchanged
      And the key field is updated

    Scenario: Signal low confidence chords
      Given an analysis with low confidence chords
      When the user views the chord chart
      Then low-confidence chords are visually marked
      And a review recommendation is shown

    Scenario: Edit individual chords
      Given a chord chart
      When the user edits a chord
      Then the change is saved
      And the version is incremented

  # ============================================================================
  # Feature: Setlists
  # ============================================================================

  Feature: Setlist management
    Scenario: Create and manage setlist
      Given the user wants to create a setlist
      When the user creates a new setlist
      Then a setlist record is created
      And the status is "draft"

    Scenario: Add arrangement to setlist
      Given a setlist in draft status
      And a published arrangement
      When the user adds the arrangement with execution key "C major"
      Then a setlist_item is created
      And the arrangement reference is preserved
      And the execution key is recorded

    Scenario: Preserve immutable history
      Given a setlist that has been executed
      When the user attempts to modify the setlist
      Then the system denies the modification
      And a message indicates the setlist is locked

    Scenario: Reorder setlist items
      Given a setlist with multiple items
      When the user reorders items
      Then the order is updated
      And consistency is maintained

  # ============================================================================
  # Feature: Multi-Tenant Isolation
  # ============================================================================

  Feature: Data isolation between organizations
    Scenario: Prevent cross-organization access
      Given user A belongs to organization A
      And a song exists in organization B
      When user A attempts to access the song
      Then the system denies access
      And no data is leaked

    Scenario: RLS enforces isolation at database level
      Given two organizations with similar data
      When querying songs for organization A
      Then only songs from organization A are returned
      And songs from organization B are not visible

    Scenario: Audit logs are organization-scoped
      Given an audit log entry
      When querying audit logs
      Then only logs for the current organization are returned

  # ============================================================================
  # Feature: Live Mode
  # ============================================================================

  Feature: Live presentation mode
    Scenario: Start live mode for setlist
      Given a published setlist
      When the user starts live mode
      Then the live mode interface is displayed
      And the current song is shown with large typography
      And sections are navigable

    Scenario: Navigate between songs in live mode
      Given live mode is active
      When the user navigates to the next song
      Then the display updates to the next arrangement
      And the current section is highlighted

  # ============================================================================
  # Feature: Permissions & Roles
  # ============================================================================

  Feature: Role-based access control
    Scenario: Leader can publish arrangements
      Given a leader user
      And a draft arrangement
      When the leader publishes the arrangement
      Then the arrangement is published
      And the published_by field is set to the leader

    Scenario: Musician can view but not publish
      Given a musician user
      And a draft arrangement
      When the musician attempts to publish
      Then the system denies the action
      And an error is returned

    Scenario: Admin can manage users and permissions
      Given an admin user
      When the admin modifies user roles
      Then the changes are applied
      And audit logs are created
