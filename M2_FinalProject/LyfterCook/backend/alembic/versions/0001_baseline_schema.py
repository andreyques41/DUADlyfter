"""baseline schema

Revision ID: 0001_baseline
Revises: 
Create Date: 2026-01-04

This baseline migration creates the project schemas and all tables as defined in
SQLAlchemy models.

For existing databases that were previously created via scripts/init_db.py,
prefer resetting the dev/test database (drop schemas) and then running
`alembic upgrade head` to ensure schema matches models.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schemas first (tables are namespaced under these).
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS core")
    op.execute("CREATE SCHEMA IF NOT EXISTS integrations")

    # Create tables from SQLAlchemy metadata.
    from app.core.database import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    # Destructive; intended for dev/test only.
    op.execute("DROP SCHEMA IF EXISTS integrations CASCADE")
    op.execute("DROP SCHEMA IF EXISTS core CASCADE")
    op.execute("DROP SCHEMA IF EXISTS auth CASCADE")
