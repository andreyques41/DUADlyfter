"""
Database Configuration Module

Provides SQLAlchemy Base, engine, session, and schema management.
Database initialization is handled by scripts/init_db.py

Essential Components:
- Base: Declarative base for ORM models
- get_schema(): Returns current schema name
- set_schema(): Changes schema dynamically
- get_db_session(): Creates new database session
- session_scope(): Context manager for transactions (legacy)
- get_db(): Get current request database session

Usage Option 1 (Session per request - RECOMMENDED):
    from app.core.database import get_db
    
    # In routes:
    @bp.route('/users/<int:id>')
    def get_user(id):
        db = get_db()
        user = db.query(User).filter_by(id=id).first()
        return user_schema.dump(user)

Usage Option 2 (Session scope - for background tasks):
    from app.core.database import session_scope
    
    with session_scope() as session:
        user = User(username='john')
        session.add(user)
        # Auto-commit happens here
"""

from flask import g, current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
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
    echo=True,  # ← True: Muestra todos los SQL queries en consola
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


def get_db() -> Session:
    """
    Get the database session for the current request.
    Session is created on first access and stored in Flask's g object.
    Session is automatically closed at the end of the request.
    
    This is the RECOMMENDED approach for Flask applications.
    
    Returns:
        Session: Current request's database session
        
    Example:
        @bp.route('/products')
        def get_products():
            db = get_db()
            products = db.query(Product).all()
            return products_schema.dump(products)
    """
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db


def close_db(exception=None):
    """
    Close the database session at the end of the request.
    This should be registered as a teardown function in your Flask app.
    
    Usage in app/__init__.py:
        app.teardown_appcontext(close_db)
    """
    db = g.pop('db', None)
    
    if db is not None:
        try:
            if exception is None:
                db.commit()
            else:
                db.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Error during session teardown: {e}")
            db.rollback()
        finally:
            db.close()


@contextmanager
def session_scope():
    """
    Context manager for database transactions.
    Automatically commits on success, rolls back on error, and always closes the session.
    
    LEGACY: Use this only for background tasks or scripts outside of request context.
    For request handlers, prefer get_db() instead.
    
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
