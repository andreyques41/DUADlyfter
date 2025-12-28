"""
Test Configuration and Fixtures
Provides shared fixtures and setup for all tests.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta
import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# IMPORTANT: Set test environment variables BEFORE importing app/config modules.
# Many modules read config at import time.
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('TESTING', 'True')
# Namespace Redis keys per test session to avoid cross-run cache poisoning.
os.environ.setdefault('REDIS_KEY_PREFIX', f"lyftercook:test:{os.getpid()}")

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.core.database import Base, engine, SessionLocal, init_db
from app.auth.models import User, UserRole
from app.chefs.models import Chef
from app.clients.models import Client
from app.dishes.models import Dish, Ingredient
from app.menus.models import Menu, MenuDish
from app.menus.models.menu_model import MenuStatus
from app.quotations.models import Quotation, QuotationItem
from app.appointments.models import Appointment
from app.scrapers.models import PriceSource, ScrapedPrice
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM
import bcrypt


# Test database configuration
# Use PostgreSQL for testing to maintain schema compatibility
TEST_DATABASE_URI = 'postgresql://postgres:andyshadow41@localhost:5432/lyftercook_test'


@pytest.fixture(scope='session')
def app():
    """
    Create application instance for testing.
    Uses in-memory SQLite database.
    """
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    
    # Create app with test config
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DEBUG': True,
        'PROPAGATE_EXCEPTIONS': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Establish application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()


@pytest.fixture(scope='session')
def database(app):
    """
    Create database schema for testing.
    Session-scoped to create once per test session.
    Uses PostgreSQL test database to support schemas.
    """
    from sqlalchemy import create_engine, text
    test_engine = create_engine(TEST_DATABASE_URI)
    
    # Create schemas (ensure a clean slate for the session)
    with test_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS auth CASCADE"))
        conn.execute(text("DROP SCHEMA IF EXISTS core CASCADE"))
        conn.execute(text("DROP SCHEMA IF EXISTS integrations CASCADE"))
        conn.commit()

        conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS core"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS integrations"))

        # Ensure enum types exist with expected values
        # Note: PostgreSQL enums are not schema-scoped and won't be removed by dropping schemas.
        conn.execute(text("DROP TYPE IF EXISTS menustatus CASCADE"))
        # SQLAlchemy's Enum(MenuStatus) stores enum *names* by default (DRAFT/PUBLISHED/...)
        # while the API exposes lowercase values via MenuStatus.value.
        conn.execute(text("CREATE TYPE menustatus AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED', 'SEASONAL')"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup - drop schemas cascade
    with test_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS auth CASCADE"))
        conn.execute(text("DROP SCHEMA IF EXISTS core CASCADE"))
        conn.execute(text("DROP SCHEMA IF EXISTS integrations CASCADE"))
        conn.commit()
    
    test_engine.dispose()


@pytest.fixture(scope='function')
def db_session(database):
    """
    Create a new database session for each test.
    Rolls back changes after each test to maintain isolation.
    """
    from sqlalchemy.orm import sessionmaker, scoped_session
    
    connection = database.connect()
    transaction = connection.begin()
    
    # Use a nested session for the test
    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    session = Session()
    
    yield session
    
    # Rollback and cleanup
    session.close()
    Session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def client(app, db_session, monkeypatch):
    """
    Create Flask test client.
    Monkeypatches get_db to return test session.
    """
    # Disable Redis cache for unit tests to avoid cross-test/cross-run contamination
    # (e.g., cached user roles causing unexpected 403s).
    from app.core import cache_manager as cm

    class _DisabledCache:
        enabled = False

        def get(self, key):
            return None

        def set(self, key, value, ttl=3600):
            return False

        def delete(self, key):
            return False

        def delete_pattern(self, pattern):
            return 0

    monkeypatch.setattr(cm, 'get_cache', lambda: _DisabledCache())

    # Monkeypatch get_db to return our test session
    def mock_get_db():
        return db_session
    
    from app.core import database
    monkeypatch.setattr(database, 'get_db', mock_get_db)
    
    # Also ensure g.db is set
    with app.test_request_context():
        from flask import g
        g.db = db_session
        
        test_client = app.test_client()
        yield test_client


@pytest.fixture
def auth_headers(test_user):
    """
    Generate authentication headers with valid JWT token.
    """
    token = generate_token(test_user.id, test_user.email, test_user.role)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def chef_headers(test_chef_user, test_chef):
    """
    Generate authentication headers for chef user.
    """
    token = generate_token(test_chef_user.id, test_chef_user.email, test_chef_user.role)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_user(db_session):
    """
    Create a dedicated admin user for admin endpoints.
    """
    hashed_password = bcrypt.hashpw('adminpass123'.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username='admin_user',
        email='admin_user@test.com',
        password_hash=hashed_password.decode('utf-8'),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    """
    Authentication headers for admin user.
    """
    token = generate_token(admin_user.id, admin_user.email, admin_user.role)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def test_user(db_session):
    """
    Create a test user (admin role).
    """
    hashed_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username='admin',
        email='admin@test.com',
        password_hash=hashed_password.decode('utf-8'),
        role=UserRole.CHEF,  # Using CHEF as admin role doesn't exist
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_chef_user(db_session):
    """
    Create a test chef user.
    """
    hashed_password = bcrypt.hashpw('chef123'.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username='testchef',
        email='chef@test.com',
        password_hash=hashed_password.decode('utf-8'),
        role=UserRole.CHEF,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_chef(db_session, test_chef_user):
    """
    Create a test chef profile.
    """
    chef = Chef(
        user_id=test_chef_user.id,
        phone='+1-555-0101',
        location='Miami, FL',
        specialty='Italian Cuisine',
        bio='Test bio for chef',
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(chef)
    db_session.commit()
    db_session.refresh(chef)
    return chef


@pytest.fixture
def test_client_profile(db_session, test_chef):
    """
    Create a test client profile (client OF a chef, not a user).
    """
    client_profile = Client(
        chef_id=test_chef.id,
        name='Test Client',
        email='testclient@example.com',
        phone='+1-555-0102',
        company='Test Company',
        notes='Test client notes',
        created_at=datetime.utcnow()
    )
    db_session.add(client_profile)
    db_session.commit()
    db_session.refresh(client_profile)
    return client_profile


@pytest.fixture
def test_dish(db_session, test_chef):
    """
    Create a test dish.
    """
    dish = Dish(
        chef_id=test_chef.id,
        name='Test Pasta',
        description='Delicious test pasta',
        category='Main Course',
        price=15.99,
        prep_time=30,
        servings=2,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(dish)
    db_session.commit()
    db_session.refresh(dish)
    
    # Add ingredient
    ingredient = Ingredient(
        dish_id=dish.id,
        name='Pasta',
        quantity=200,
        unit='g'
    )
    db_session.add(ingredient)
    db_session.commit()
    
    return dish


@pytest.fixture
def test_menu(db_session, test_chef):
    """
    Create a test menu.
    """
    menu = Menu(
        chef_id=test_chef.id,
        name='Test Menu',
        description='Test menu description',
        status=MenuStatus.PUBLISHED,
        created_at=datetime.utcnow()
    )
    db_session.add(menu)
    db_session.commit()
    db_session.refresh(menu)
    return menu


@pytest.fixture
def test_quotation(db_session, test_chef, test_client_profile):
    """
    Create a test quotation.
    """
    quotation = Quotation(
        chef_id=test_chef.id,
        client_id=test_client_profile.id,
        quotation_number=f'QT-{datetime.utcnow().timestamp()}',
        event_date=(datetime.utcnow() + timedelta(days=30)).date(),
        number_of_people=50,
        total_price=550.00,
        status='draft',
        notes='Test quotation',
        created_at=datetime.utcnow()
    )
    db_session.add(quotation)
    db_session.commit()
    db_session.refresh(quotation)
    return quotation


@pytest.fixture
def test_appointment(db_session, test_chef, test_client_profile):
    """
    Create a test appointment.
    """
    appointment = Appointment(
        chef_id=test_chef.id,
        client_id=test_client_profile.id,
        title='Menu Planning Session',
        description='Discuss menu options for upcoming event',
        scheduled_at=datetime.utcnow() + timedelta(days=7),
        duration_minutes=60,
        location='Chef Office',
        status='scheduled',
        notes='Test appointment',
        created_at=datetime.utcnow()
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment


@pytest.fixture
def other_chef_user(db_session):
    """
    Create an additional chef user for ownership tests.
    """
    hashed_password = bcrypt.hashpw('otherchef123'.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username='secondchef',
        email='secondchef@test.com',
        password_hash=hashed_password.decode('utf-8'),
        role=UserRole.CHEF,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_chef(db_session, other_chef_user):
    """
    Create a chef profile linked to the additional user.
    """
    chef = Chef(
        user_id=other_chef_user.id,
        phone='+1-555-0201',
        location='Orlando, FL',
        specialty='BBQ',
        bio='Other chef profile for ownership tests',
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(chef)
    db_session.commit()
    db_session.refresh(chef)
    return chef


@pytest.fixture
def other_dish(db_session, other_chef):
    """
    Create a dish that belongs to the other chef.
    """
    dish = Dish(
        chef_id=other_chef.id,
        name='Other Chef Dish',
        description='Dish owned by another chef',
        category='Main Course',
        price=12.50,
        prep_time=20,
        servings=2,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(dish)
    db_session.commit()
    db_session.refresh(dish)
    return dish


@pytest.fixture
def other_chef_headers(other_chef_user):
    """
    Authentication headers for the additional chef.
    """
    token = generate_token(other_chef_user.id, other_chef_user.email, other_chef_user.role)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def test_price_source(db_session):
    """
    Create a test price source.
    """
    price_source = PriceSource(
        name='Test Supermarket',
        base_url='https://example.com',
        search_url_template='https://example.com/search?q={ingredient}',
        product_name_selector='.product-name',
        price_selector='.price',
        image_selector='.product-img',
        is_active=True,
        notes='Test price source',
        created_at=datetime.utcnow()
    )
    db_session.add(price_source)
    db_session.commit()
    db_session.refresh(price_source)
    return price_source


def generate_token(user_id, email, role):
    """
    Generate JWT token for testing.
    Uses the same secret key as the test app configuration.
    """
    # Convert UserRole enum to string if needed
    role_str = role.value if hasattr(role, 'value') else role
    
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role_str,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    # Use test secret key to match app config
    return jwt.encode(payload, 'test-secret-key', algorithm='HS256')


@pytest.fixture
def sample_dish_data():
    """
    Sample data for creating a dish.
    """
    return {
        'name': 'Spaghetti Carbonara',
        'description': 'Classic Italian pasta',
        'category': 'Main Course',
        'price': 18.99,
        'prep_time': 25,
        'servings': 2,
        'ingredients': [
            {'name': 'Spaghetti', 'quantity': 200, 'unit': 'g'},
            {'name': 'Eggs', 'quantity': 3, 'unit': 'units'},
            {'name': 'Guanciale', 'quantity': 100, 'unit': 'g'}
        ]
    }


@pytest.fixture
def sample_menu_data():
    """
    Sample data for creating a menu.
    """
    return {
        'name': 'Italian Night',
        'description': '3-course Italian dinner',
        'status': 'published'
    }


@pytest.fixture
def sample_quotation_data():
    """
    Sample data for creating a quotation.
    """
    future_date = (datetime.utcnow() + timedelta(days=15)).date()
    return {
        'event_date': future_date.isoformat(),
        'number_of_people': 25,
        'notes': 'Outdoor setup required',
        'items': [
            {
                'dish_id': 1,
                'item_name': 'Pasta Carbonara',
                'description': 'Classic Italian pasta',
                'quantity': 25,
                'unit_price': 15.99
            }
        ]
    }


@pytest.fixture
def sample_client_data():
    """
    Sample data for creating a client.
    """
    return {
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'phone': '+1-555-0199',
        'company': 'Doe Enterprises',
        'notes': 'Prefers organic ingredients'
    }
