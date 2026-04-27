# ADR-002: Multi-Tenant Isolation via PostgreSQL Row Level Security

## Status
Accepted

## Context

The platform serves multiple organizations (churches, worship groups, organizations) with strict data isolation requirements. Each organization must be unable to access data from other organizations through any API endpoint or direct query.

Isolation strategies:
1. **Application-level filtering**: Check organization_id in every query (error-prone, maintenance burden)
2. **Database-level RLS**: PostgreSQL Row Level Security policies enforce isolation at the database layer
3. **Separate databases**: One database per organization (operational complexity, scaling issues)
4. **Separate schemas**: One schema per organization (better than separate DBs, but still complex)

## Decision

**Implement multi-tenant isolation using PostgreSQL Row Level Security (RLS) with organization context passed through session variables.**

## Rationale

1. **Security by Default**: RLS enforces isolation at the database layer, preventing accidental data leaks from application bugs.

2. **Single Database**: Simpler operations, easier backups, unified monitoring, cost-effective.

3. **Transparent to Application**: Once RLS policies are in place, the application doesn't need to manually filter by organization_id on every query.

4. **Audit Trail**: All data access is logged by PostgreSQL, providing compliance and security benefits.

5. **Performance**: RLS uses indexes efficiently; no performance penalty compared to application-level filtering.

6. **PostgreSQL Native**: No external dependencies; RLS is a core PostgreSQL feature.

## Implementation Strategy

### 1. Organization Context

Every API request sets the current organization in the database session:

```sql
SET app.current_organization_id = 'org-123';
```

### 2. RLS Policies

All multi-tenant tables have RLS enabled with policies:

```sql
ALTER TABLE songs ENABLE ROW LEVEL SECURITY;

CREATE POLICY org_isolation ON songs
  USING (organization_id = current_setting('app.current_organization_id')::uuid);
```

### 3. Application Integration

In FastAPI middleware, after authentication:

```python
@app.middleware("http")
async def set_organization_context(request: Request, call_next):
    user = request.state.user
    org_id = user.organization_id
    
    # Set RLS context
    async with db.connection() as conn:
        await conn.execute(f"SET app.current_organization_id = '{org_id}'")
    
    response = await call_next(request)
    return response
```

### 4. Tables with RLS

- `organizations` (no RLS, but admin-only access)
- `teams` (RLS by organization_id)
- `users` (RLS by organization_id)
- `songs` (RLS by organization_id)
- `song_sources` (RLS via song → organization_id)
- `song_analyses` (RLS via song → organization_id)
- `arrangements` (RLS via song → organization_id)
- `setlists` (RLS by organization_id)
- `audit_logs` (RLS by organization_id)

## Consequences

### Positive
- Bulletproof isolation; no accidental cross-organization data leaks
- Audit trail for compliance
- Scales to thousands of organizations
- Transparent to application code

### Negative
- Requires careful RLS policy design
- Debugging RLS issues can be complex
- Small performance overhead for policy evaluation (negligible)

## Alternatives Considered

### Application-Level Filtering
Simpler to implement initially but error-prone. One forgotten filter = data leak.

### Separate Databases
Operational nightmare; backups, migrations, monitoring all multiply.

### Separate Schemas
Better than separate DBs but still complex; schema management overhead.

## Implementation Checklist

- [ ] Design RLS policies for all multi-tenant tables
- [ ] Create migration to enable RLS
- [ ] Implement middleware to set organization context
- [ ] Test RLS policies with cross-organization queries (should fail)
- [ ] Document RLS policy for each table
- [ ] Add integration tests for RLS enforcement

## Related Decisions

- ADR-001: Essentia as primary MIR engine
- ADR-003: Async pipeline with Celery (TBD)

## References

- PostgreSQL RLS Documentation: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Multi-Tenancy Patterns: https://www.postgresql.org/docs/current/sql-createpolicy.html
