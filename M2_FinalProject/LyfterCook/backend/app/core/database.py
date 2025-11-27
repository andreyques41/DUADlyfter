"""
Database Configuration Module
Handles database connection and session management.
"""

import logging
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_db() -> Session:
    """
    Get the database session for the current request.
    Session is created on first access and stored in Flask's g object.
    Session is automatically closed at the end of the request.
    
    Returns:
        Session: Current request's database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    if 'db' not in g:
        g.db = SessionLocal()
    
    return g.db


def close_db(exception=None):
    """
    Close the database session at the end of the request.
    This should be registered as a teardown function in your Flask app.
    
    Automatically commits or rolls back based on whether an exception occurred.
    """
    db = g.pop('db', None)
    
    if db is not None:
        try:
            if exception is None:
                db.commit()
            else:
                logger.warning("Rolling back transaction due to exception")
                db.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Error during session teardown: {e}")
            db.rollback()
        finally:
            db.close()


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
