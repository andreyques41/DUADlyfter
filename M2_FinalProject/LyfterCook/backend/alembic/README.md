# Alembic Migrations

This directory contains Alembic database migrations for the LyfterCook project.

## Quick Start

### Initialize Database with Current Schema
```bash
# Create all schemas and tables from models
python scripts/init_db.py
```

### Create a New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for data migrations)
alembic revision -m "description"
```

### Apply Migrations
```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Check Migration Status
```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Migration Best Practices

1. **Always review auto-generated migrations**
   - Check for unintended changes
   - Verify data type changes
   - Ensure indexes are preserved

2. **Test migrations before committing**
   - Apply in dev environment
   - Test upgrade and downgrade
   - Verify data integrity

3. **Use meaningful commit messages**
   - Describe what changed
   - Include ticket/issue numbers

4. **Handle data migrations carefully**
   - Backup data before migration
   - Use batch operations for large tables
   - Consider downtime requirements

## Schema Organization

LyfterCook uses 3 PostgreSQL schemas:

- **auth**: User authentication and authorization
- **core**: Business logic (chefs, dishes, menus, etc.)
- **integrations**: External services (scrapers, appointments)

All migrations handle multiple schemas automatically.

## Common Operations

### Add a Column
```python
def upgrade():
    op.add_column('tablename', 
        sa.Column('new_column', sa.String(50), nullable=True),
        schema='core'
    )

def downgrade():
    op.drop_column('tablename', 'new_column', schema='core')
```

### Create an Index
```python
def upgrade():
    op.create_index('idx_table_column', 'tablename', ['column'], 
                    unique=False, schema='core')

def downgrade():
    op.drop_index('idx_table_column', 'tablename', schema='core')
```

### Modify Column Type
```python
def upgrade():
    op.alter_column('tablename', 'columnname',
                    type_=sa.String(100),
                    existing_type=sa.String(50),
                    schema='core')

def downgrade():
    op.alter_column('tablename', 'columnname',
                    type_=sa.String(50),
                    existing_type=sa.String(100),
                    schema='core')
```

## Migration Files Location

- **Configuration**: `alembic.ini`
- **Environment**: `alembic/env.py`
- **Versions**: `alembic/versions/*.py`
- **Template**: `alembic/script.py.mako`

## Legacy SQL Migrations

Legacy SQL migrations have been removed. Alembic is the single source of truth for schema changes.
