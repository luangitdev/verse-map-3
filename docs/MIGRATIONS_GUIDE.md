# Database Migrations Guide

Using Alembic for database schema management.

## Overview

Alembic is a lightweight database migration tool for SQLAlchemy. It allows us to:
- Track database schema changes
- Version control database schemas
- Rollback changes when needed
- Collaborate on database changes

## Setup

### 1. Initialize Alembic

```bash
cd apps/api
alembic init alembic
```

### 2. Configure Alembic

Edit `alembic/env.py`:

```python
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/music_analysis')

config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL)
```

## Creating Migrations

### Automatic Migration

When you change models in `models.py`:

```bash
# Generate migration automatically
alembic revision --autogenerate -m "Add user_role column"
```

This creates a new file in `alembic/versions/` with the changes.

### Manual Migration

For complex changes:

```bash
# Create empty migration
alembic revision -m "Custom migration description"
```

Then edit the file to add your SQL commands:

```python
def upgrade():
    op.add_column('users', sa.Column('role', sa.String(50)))

def downgrade():
    op.drop_column('users', 'role')
```

## Applying Migrations

### Apply All Pending Migrations

```bash
alembic upgrade head
```

### Apply Specific Migration

```bash
alembic upgrade 1234567890ab
```

### Apply N Migrations

```bash
alembic upgrade +2
```

## Rollback Migrations

### Rollback One Migration

```bash
alembic downgrade -1
```

### Rollback to Specific Migration

```bash
alembic downgrade 1234567890ab
```

### Rollback All Migrations

```bash
alembic downgrade base
```

## Viewing Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history --verbose

# Show migration details
alembic show 1234567890ab
```

## Migration Best Practices

### 1. Write Descriptive Messages

```bash
alembic revision --autogenerate -m "Add arrangement_id foreign key to setlist_items"
```

### 2. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 3. Review Generated Migrations

Always review auto-generated migrations before committing:

```python
# Check for correct column types
# Check for correct constraints
# Check for correct indexes
```

### 4. Handle Data Migrations

For migrations that involve data changes:

```python
def upgrade():
    # Create new column
    op.add_column('songs', sa.Column('new_field', sa.String(255)))
    
    # Migrate data
    connection = op.get_bind()
    connection.execute(
        "UPDATE songs SET new_field = old_field"
    )
    
    # Drop old column
    op.drop_column('songs', 'old_field')

def downgrade():
    # Reverse the process
    op.add_column('songs', sa.Column('old_field', sa.String(255)))
    connection = op.get_bind()
    connection.execute(
        "UPDATE songs SET old_field = new_field"
    )
    op.drop_column('songs', 'new_field')
```

### 5. Use Transactions

```python
from alembic import op

def upgrade():
    # This will be wrapped in a transaction
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer, primary_key=True),
    )

def downgrade():
    op.drop_table('new_table')
```

## Common Migration Patterns

### Add Column

```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255)))

def downgrade():
    op.drop_column('users', 'email')
```

### Drop Column

```python
def upgrade():
    op.drop_column('users', 'deprecated_field')

def downgrade():
    op.add_column('users', sa.Column('deprecated_field', sa.String(255)))
```

### Rename Column

```python
def upgrade():
    op.alter_column('users', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('users', 'new_name', new_column_name='old_name')
```

### Create Index

```python
def upgrade():
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email')
```

### Add Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_songs_org_id',
        'songs',
        'organizations',
        ['organization_id'],
        ['id']
    )

def downgrade():
    op.drop_constraint('fk_songs_org_id', 'songs')
```

### Add Unique Constraint

```python
def upgrade():
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

def downgrade():
    op.drop_constraint('uq_users_email', 'users')
```

## Docker Integration

### Run Migrations in Docker

```bash
# Apply migrations
docker-compose exec api alembic upgrade head

# Create migration
docker-compose exec api alembic revision --autogenerate -m "Description"

# View history
docker-compose exec api alembic history
```

### Automatic Migrations on Startup

Add to `apps/api/main.py`:

```python
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

async def startup_event():
    """Run migrations on startup"""
    alembic_cfg = Config("alembic.ini")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        op = Operations(context)
        
        # Run migrations
        from alembic.command import upgrade
        upgrade(alembic_cfg, 'head')

app = FastAPI()

@app.on_event("startup")
async def startup():
    await startup_event()
```

## Troubleshooting

### Migration Conflicts

If migrations conflict:

```bash
# View conflicting migrations
alembic branches

# Merge branches
alembic merge -m "Merge conflicting migrations"
```

### Rollback Issues

If a rollback fails:

```bash
# Mark migration as current without running
alembic stamp 1234567890ab

# Then manually fix the database
```

### Lost Migrations

If migrations are lost:

```bash
# Check git history
git log --oneline alembic/versions/

# Restore from git
git checkout alembic/versions/
```

## Workflow Example

### 1. Modify Models

```python
# apps/api/models.py
class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    artist = Column(String(255))
    new_field = Column(String(255))  # NEW
```

### 2. Generate Migration

```bash
alembic revision --autogenerate -m "Add new_field to songs"
```

### 3. Review Migration

```bash
# Check generated migration file
cat alembic/versions/1234567890ab_add_new_field_to_songs.py
```

### 4. Test Migration

```bash
# Apply migration
alembic upgrade head

# Test application
pytest tests/

# Rollback if needed
alembic downgrade -1
```

### 5. Commit Changes

```bash
git add alembic/versions/
git add models.py
git commit -m "Add new_field to songs table"
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Database Migrations Best Practices](https://www.liquibase.org/get-started/best-practices)
