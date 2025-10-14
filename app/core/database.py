"""
Database Configuration Module

Provides SQLAlchemy Base, engine, session, and schema management.
Database initialization is handled by scripts/init_db.py

Essential Components:
- Base: Declarative base for ORM models
- get_schema(): Returns current schema name
- set_schema(): Changes schema dynamically
- get_db_session(): Creates new database session
- session_scope(): Context manager for transactions

Usage:
    from app.core.database import Base, get_schema, session_scope
    
    # In models:
    class MyModel(Base):
        __tablename__ = "my_table"
        
        @declared_attr
        def __table_args__(cls):
            return {'schema': get_schema()}
    
    # In services:
    with session_scope() as session:
        user = session.query(User).filter_by(username='john').first()
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from config.settings import get_database_url, DB_SCHEMA
import logging

# Configure module logger
logger = logging.getLogger(__name__)

# Database URL from config
DATABASE_URL = get_database_url()

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative Base for ORM models
Base = declarative_base()

# Current schema
_current_schema = DB_SCHEMA


def get_schema() -> str:
    """Get the current database schema name."""
    return _current_schema


def set_schema(schema_name: str):
    """Set the database schema name dynamically."""
    global _current_schema
    _current_schema = schema_name


def get_db_session():
    """Create and return a new database session."""
    return SessionLocal()


@contextmanager
def session_scope():
    """
    Context manager for database transactions.
    Automatically commits on success, rolls back on error, and always closes the session.
    
    Usage:
        with session_scope() as session:
            user = User(username='john')
            session.add(user)
            # Auto-commit happens here
    """
    session = get_db_session()
    try:
        yield session
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error during transaction: {e}")
        raise
    
    finally:
        session.close()


def get_engine():
    """Get the SQLAlchemy engine instance."""
    return engine
