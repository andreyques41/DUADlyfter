"""
Database Configuration Module
Handles database connection and session management.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None

# Base class for models
Base = declarative_base()


def init_db():
    """
    Initialize database connection and create engine.
    Should be called once at application startup.
    """
    global engine, SessionLocal
    
    try:
        database_url = settings.get_database_url()
        logger.info(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20,
            echo=settings.FLASK_DEBUG  # Log SQL queries in debug mode
        )
        
        SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        ))
        
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_db():
    """
    Get database session for direct use (not as context manager).
    
    Returns:
        Session: SQLAlchemy database session
        
    Note:
        Caller is responsible for closing the session.
        For Flask request context, session is automatically closed on teardown.
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    return SessionLocal()


def close_db(e=None):
    """
    Close database session.
    Called automatically on request teardown.
    """
    if SessionLocal:
        SessionLocal.remove()


def create_tables():
    """
    Create all database tables.
    Should only be used in development or migrations.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_tables():
    """
    Drop all database tables.
    WARNING: Only use in development!
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped")
