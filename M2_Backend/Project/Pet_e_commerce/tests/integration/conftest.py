"""
Integration Tests Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides fixtures for integration testing using the existing PostgreSQL test database.
Leverages the test database setup from main conftest.py.

Key fixtures:
- integration_db_session: Uses the session-scoped test database with reference data already loaded
"""
import pytest


@pytest.fixture(scope="function")
def integration_db_session(db_session):
    """
    Provide a real database session for integration tests.
    
    Reuses the existing test database from conftest.py.
    Reference data is already loaded by the reference_data_fixtures plugin.
    
    IMPORTANT: Resets and re-initializes ReferenceDataCache to ensure it uses
    the test database session with correct reference data.
    """
    from app.core.reference_data import ReferenceDataCache
    from flask import g
    
    # Reset cache to clear any production data
    ReferenceDataCache.reset()
    
    # Initialize cache with test database session
    # This will use g.db if available (which we'll set in tests)
    ReferenceDataCache._initialized = False  # Force re-init
    
    return db_session

