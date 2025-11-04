"""
Integration Tests Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides fixtures for integration testing using the existing PostgreSQL test database.
Leverages the test database setup from main conftest.py.

Key fixtures:
- integration_db_session: Uses the session-scoped test database with reference data already loaded
"""
import pytest

# Automatically use setup_reference_data fixture for all integration tests
pytestmark = pytest.mark.usefixtures("setup_reference_data")


@pytest.fixture(scope="function")
def integration_db_session(app, db_session, setup_reference_data):
    """
    Provide a real database session for integration tests.
    
    Reuses the existing test database from conftest.py.
    Reference data is already loaded and cache initialized by setup_reference_data fixture.
    
    Tests can now use g.db to direct their queries to the test database session with rollback.
    """
    # Cache is already initialized with test data by setup_reference_data fixture
    # No additional setup needed here
    
    yield db_session


