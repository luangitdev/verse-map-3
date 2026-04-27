# API Reference - Music Analysis Platform

Complete reference for all API endpoints.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All endpoints (except `/health` and `/auth/login`) require a JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

## Health Endpoints

### Health Check

```http
GET /health
```

Returns basic health status.

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2026-04-27T22:00:00Z",
  "version": "1.0.0"
}
```

### Detailed Health Check

```http
GET /health/detailed
```

Returns detailed health status including database and Redis.

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2026-04-27T22:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": "ok",
    "redis": "ok"
  }
}
```

## Authentication Endpoints

### Login

```http
POST /auth/login
```

Authenticate user and receive JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (201):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "leader"
}
```

### Get Current User

```http
GET /auth/me
```

Get current authenticated user information.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "leader",
  "organization_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Logout

```http
POST /auth/logout
```

Logout current user (logs action in audit trail).

**Response** (200):
```json
{
  "message": "Logged out successfully"
}
```

### Refresh Token

```http
POST /auth/refresh
```

Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Songs Endpoints

### Import from YouTube

```http
POST /songs/import-youtube
```

Import a song from YouTube URL. Returns immediately with analysis_id.

**Request**:
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "Never Gonna Give You Up"
}
```

**Response** (202 Accepted):
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "queued",
  "message": "Analysis queued successfully"
}
```

### Get Analysis Status

```http
GET /analyses/{analysis_id}
```

Poll analysis status and progress.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "phase": "ready",
  "bpm": 120.0,
  "bpm_confidence": 0.95,
  "key": "C major",
  "key_confidence": 0.90,
  "error_message": null,
  "created_at": "2026-04-27T22:00:00Z",
  "updated_at": "2026-04-27T22:05:00Z"
}
```

### Get Song Details

```http
GET /songs/{song_id}
```

Retrieve song with metadata and analysis results.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Never Gonna Give You Up",
  "artist": "Rick Astley",
  "duration_seconds": 213,
  "created_at": "2026-04-27T22:00:00Z",
  "updated_at": "2026-04-27T22:05:00Z"
}
```

### List Songs in Organization

```http
GET /organizations/{organization_id}/library
```

List songs in organization library with pagination.

**Query Parameters**:
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 20) - Number of items to return

**Response** (200):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Never Gonna Give You Up",
      "artist": "Rick Astley",
      "duration_seconds": 213,
      "created_at": "2026-04-27T22:00:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

## Arrangements Endpoints

### Create Arrangement

```http
POST /songs/{song_id}/arrangements
```

Create a new arrangement for a song.

**Request**:
```json
{
  "name": "Original Arrangement",
  "key": "G major",
  "sections": [],
  "chords": null,
  "notes": "Beautiful hymn"
}
```

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Original Arrangement",
  "key": "G major",
  "published": false,
  "version": 1,
  "created_at": "2026-04-27T22:00:00Z"
}
```

### Get Arrangement

```http
GET /arrangements/{arrangement_id}
```

Retrieve arrangement with all details.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Original Arrangement",
  "key": "G major",
  "sections": [],
  "chords": null,
  "notes": "Beautiful hymn",
  "published": false,
  "published_by": null,
  "version": 1,
  "created_at": "2026-04-27T22:00:00Z",
  "updated_at": "2026-04-27T22:00:00Z"
}
```

### Update Sections

```http
PATCH /arrangements/{arrangement_id}/sections
```

Update arrangement sections (rename, reorder, mark as speech).

**Request**:
```json
{
  "sections": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "type": "verse",
      "label": "Verse 1",
      "start_time": 0.0,
      "end_time": 30.0
    }
  ]
}
```

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Original Arrangement",
  "key": "G major",
  "published": false,
  "version": 2,
  "created_at": "2026-04-27T22:00:00Z"
}
```

### Update Chords

```http
PATCH /arrangements/{arrangement_id}/chords
```

Update arrangement chords (edit individual chords or transpose).

**Request**:
```json
{
  "chords": [
    {
      "time": 0.0,
      "chord": "G",
      "confidence": 0.95
    }
  ],
  "new_key": "A major"
}
```

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Original Arrangement",
  "key": "A major",
  "published": false,
  "version": 3,
  "created_at": "2026-04-27T22:00:00Z"
}
```

### Publish Arrangement

```http
POST /arrangements/{arrangement_id}/publish
```

Publish an arrangement (only leaders and admins).

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "song_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Original Arrangement",
  "key": "G major",
  "published": true,
  "version": 1,
  "created_at": "2026-04-27T22:00:00Z"
}
```

### List Arrangements for Song

```http
GET /songs/{song_id}/arrangements
```

List all arrangements for a song.

**Response** (200):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Original Arrangement",
      "key": "G major",
      "published": true,
      "version": 1,
      "created_at": "2026-04-27T22:00:00Z"
    }
  ],
  "total": 1
}
```

## Setlists Endpoints

### Create Setlist

```http
POST /setlists
```

Create a new setlist.

**Request**:
```json
{
  "name": "Sunday Service"
}
```

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "name": "Sunday Service",
  "status": "draft",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-27T22:00:00Z"
}
```

### Get Setlist

```http
GET /setlists/{setlist_id}
```

Retrieve setlist with all items.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "name": "Sunday Service",
  "status": "draft",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "arrangement_id": "550e8400-e29b-41d4-a716-446655440002",
      "order": 1,
      "key": "G major",
      "notes": "Start with this song",
      "duration_seconds": 240,
      "created_at": "2026-04-27T22:00:00Z"
    }
  ],
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-27T22:00:00Z",
  "updated_at": "2026-04-27T22:00:00Z"
}
```

### Add Item to Setlist

```http
POST /setlists/{setlist_id}/items
```

Add an arrangement to a setlist.

**Request**:
```json
{
  "arrangement_id": "550e8400-e29b-41d4-a716-446655440002",
  "key": "G major",
  "notes": "Start with this song",
  "duration_seconds": 240
}
```

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "arrangement_id": "550e8400-e29b-41d4-a716-446655440002",
  "order": 1,
  "key": "G major",
  "created_at": "2026-04-27T22:00:00Z"
}
```

### Update Setlist Item

```http
PATCH /setlist-items/{item_id}
```

Update a setlist item (reorder, change key, edit notes).

**Request**:
```json
{
  "order": 2,
  "key": "A major",
  "notes": "Updated notes"
}
```

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "order": 2,
  "key": "A major",
  "notes": "Updated notes"
}
```

### Start Live Mode

```http
POST /setlists/{setlist_id}/live/start
```

Start live mode for a setlist (marks as executed).

**Response** (200):
```json
{
  "setlist_id": "550e8400-e29b-41d4-a716-446655440004",
  "status": "live",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "arrangement_id": "550e8400-e29b-41d4-a716-446655440002",
      "order": 1,
      "key": "G major"
    }
  ],
  "current_item_index": 0,
  "started_at": "2026-04-27T22:00:00Z"
}
```

### Get Live Status

```http
GET /setlists/{setlist_id}/live/status
```

Get live mode status for a setlist.

**Response** (200):
```json
{
  "setlist_id": "550e8400-e29b-41d4-a716-446655440004",
  "status": "live",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "arrangement_id": "550e8400-e29b-41d4-a716-446655440002",
      "order": 1,
      "key": "G major",
      "duration_seconds": 240
    }
  ],
  "total_items": 1,
  "updated_at": "2026-04-27T22:00:00Z"
}
```

### List Setlists in Organization

```http
GET /organizations/{organization_id}/setlists
```

List setlists in organization with pagination.

**Query Parameters**:
- `skip` (int, default: 0) - Number of items to skip
- `limit` (int, default: 20) - Number of items to return

**Response** (200):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "name": "Sunday Service",
      "status": "draft",
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-04-27T22:00:00Z"
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "code": 400,
  "timestamp": "2026-04-27T22:00:00Z"
}
```

### Common Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing (async)
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Rate limiting is not currently implemented but will be added in production.

## Pagination

List endpoints support pagination with `skip` and `limit` query parameters:

```
GET /organizations/{org_id}/library?skip=0&limit=20
```

## Filtering

Filtering is not currently implemented but will be added for:
- Songs: by title, artist, date range
- Arrangements: by publication status, key
- Setlists: by status, date range
