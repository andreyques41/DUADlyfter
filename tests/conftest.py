"""
Pytest Configuration and Global Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides global fixtures for all test modules:
- Flask application factory
- PostgreSQL test database setup/teardown
- Database session management
- Flask test client
- Authentication helpers

Coverage targets:
- auth: 90-95% (critical security)
- sales: 85-90% (money involved)
- products: 80-85% (standard CRUD)
- core: 75-80% (infrastructure)
- overall: 85%+ (industry standard)
"""
import pytest
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database, drop_database

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.core.database import Base, get_schema

# Import all fixtures to make them available globally
pytest_plugins = [
    'tests.fixtures.reference_data_fixtures',  # Must be first for integration tests
    'tests.fixtures.user_fixtures',
    'tests.fixtures.product_fixtures',
    'tests.fixtures.cart_order_fixtures',
]


@pytest.fixture(scope="session")
def app():
    """
    Create Flask application for testing.
    
    Scope: session (created once for all tests)
    """
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DB_NAME'] = 'test_pet_ecommerce'
    
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    return flask_app


@pytest.fixture(scope="session")
def test_db_url():
    """
    Generate test database URL from environment variables.
    
    Scope: session
    """
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'test_pet_ecommerce'
    }
    
    return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"


@pytest.fixture(scope="session")
def test_db_engine(test_db_url):
    """
    Create PostgreSQL test database and engine.
    
    Scope: session (created once, cleaned up after all tests)
    
    This fixture:
    1. Creates test database if not exists
    2. Creates all tables (schema: lyfter_backend_project)
    3. Yields engine for tests
    4. Drops all tables and database after tests
    """
    # Create test database if not exists
    if not database_exists(test_db_url):
        create_database(test_db_url)
        print(f"\n[OK] Created test database: {test_db_url}")
    
    # Create engine
    engine = create_engine(test_db_url, echo=False)
    
    # Create schema if not exists
    schema_name = get_schema()
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(engine)
    print(f"[OK] Created all tables in schema: {schema_name}")
    
    yield engine
    
    # Cleanup after all tests
    print("\n[CLEANUP] Cleaning up test database...")
    Base.metadata.drop_all(engine)
    engine.dispose()
    
    # Drop test database
    if database_exists(test_db_url):
        drop_database(test_db_url)
        print("[OK] Dropped test database")


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Provide database session with automatic rollback.
    
    Scope: function (new session for each test, rolled back after)
    
    This ensures test isolation - each test starts with clean state.
    Changes made in one test don't affect others.
    """
    # Create session
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    Session = scoped_session(sessionmaker(bind=connection))
    session = Session()
    
    yield session
    
    # Rollback transaction (undo all changes)
    session.close()
    Session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app):
    """
    Flask test client for API testing.
    
    Scope: function (new client for each test)
    
    Usage:
        response = client.get('/products')
        response = client.post('/auth/login', json={'username': 'test'})
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Flask CLI test runner.
    
    Scope: function
    """
    return app.test_cli_runner()


# ========================================
# Authentication Helpers
# ========================================

@pytest.fixture
def auth_headers(client, test_user):
    """
    Get authentication headers with JWT token for test user.
    
    Usage:
        response = client.get('/sales/orders', headers=auth_headers)
    
    Requires: test_user fixture (from user_fixtures.py)
    """
    response = client.post('/auth/login', json={
        'username': test_user.username,
        'password': 'password123'  # Default test password
    })
    
    if response.status_code == 200:
        token = response.get_json()['token']
        return {'Authorization': f'Bearer {token}'}
    else:
        pytest.fail(f"Failed to get auth token: {response.get_json()}")


@pytest.fixture
def admin_headers(client, test_admin):
    """
    Get authentication headers with JWT token for admin user.
    
    Usage:
        response = client.post('/products', headers=admin_headers, json=product_data)
    
    Requires: test_admin fixture (from user_fixtures.py)
    """
    response = client.post('/auth/login', json={
        'username': test_admin.username,
        'password': 'admin123'  # Default admin password
    })
    
    if response.status_code == 200:
        token = response.get_json()['token']
        return {'Authorization': f'Bearer {token}'}
    else:
        pytest.fail(f"Failed to get admin token: {response.get_json()}")


# ========================================
# Test Markers Configuration
# ========================================

def pytest_configure(config):
    """
    Configure custom pytest markers.
    
    Markers allow selective test running:
    - pytest -m unit          # Only unit tests
    - pytest -m integration   # Only integration tests
    - pytest -m "not slow"    # Skip slow tests
    - pytest -m critical      # Only critical path tests
    """
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (database)")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "e2e: End-to-end workflow tests")
    config.addinivalue_line("markers", "slow: Tests that take > 1 second")
    config.addinivalue_line("markers", "auth: Authentication related tests")
    config.addinivalue_line("markers", "products: Product module tests")
    config.addinivalue_line("markers", "sales: Sales module tests")
    config.addinivalue_line("markers", "critical: Critical paths requiring 100% coverage")


# ========================================
# Test Reporting Hooks
# ========================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add custom summary information after test run.
    """
    if hasattr(terminalreporter.config, '_metadata'):
        terminalreporter.config._metadata['Python'] = sys.version.split()[0]
        terminalreporter.config._metadata['Database'] = 'PostgreSQL (test_pet_ecommerce)'
        terminalreporter.config._metadata['Coverage Target'] = '85%+'
