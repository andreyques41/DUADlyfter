"""
User Test Fixtures
~~~~~~~~~~~~~~~~~

Provides test data for User, Role, RoleUser models using Faker.

Fixtures:
- sample_user_data: Dictionary with fake user data
- test_user: Regular user in database
- test_admin: Admin user in database
- multiple_users: List of test users
- test_role_user: Regular user role
- test_role_admin: Admin role
"""
import pytest
from faker import Faker
from app.auth.models import User, Role, RoleUser
from app.auth.services.security_service import hash_password

fake = Faker()


@pytest.fixture(scope="session")
def test_role_user(test_db_engine):
    """
    Create user role in database (DB assigns ID).
    
    Scope: session (created once for all tests)
    """
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        # Check if role already exists by name (not ID)
        role = session.query(Role).filter_by(name='user').first()
        if not role:
            role = Role(
                # Let database assign ID automatically
                name='user',
                description='Regular user with standard permissions'
            )
            session.add(role)
            session.commit()
            session.refresh(role)
        return role


@pytest.fixture(scope="session")
def test_role_admin(test_db_engine):
    """
    Create admin role (id=2) in database.
    
    Scope: session (created once for all tests)
    """
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        role = session.query(Role).filter_by(id=2).first()
        if not role:
            role = Role(
                id=2,
                name='admin',
                description='Administrator with full permissions'
            )
            session.add(role)
            session.commit()
            session.refresh(role)
        return role


@pytest.fixture
def sample_user_data():
    """
    Generate sample user data dictionary (not persisted).
    
    Scope: function (new data for each test)
    
    Returns:
        dict: User data with fake values
    """
    return {
        'username': fake.user_name(),
        'email': fake.email(),
        'password': 'Test123!@#',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone': fake.phone_number()[:20]  # Limit to 20 chars
    }


@pytest.fixture
def test_user(db_session, test_role_user):
    """
    Create regular test user in database with role assignment.
    
    Scope: function (new user for each test, auto-deleted via rollback)
    
    Credentials:
        username: testuser
        password: password123
        role: user (id=1)
    
    Usage:
        def test_something(test_user):
            assert test_user.username == 'testuser'
    """
    user = User(
        username='testuser',
        email='testuser@example.com',
        password_hash=hash_password('password123'),
        first_name='Test',
        last_name='User',
        phone='555-0100'
    )
    db_session.add(user)
    db_session.flush()  # Get user.id before creating RoleUser
    
    # Assign role via RoleUser
    role_user = RoleUser(
        user_id=user.id,
        role_id=1  # Regular user role
    )
    db_session.add(role_user)
    db_session.commit()
    db_session.refresh(user)
    
    # Store plain password for login tests
    user._plain_password = 'password123'
    
    return user


@pytest.fixture
def test_admin(db_session, test_role_admin):
    """
    Create admin test user in database with role assignment.
    
    Scope: function (new admin for each test, auto-deleted via rollback)
    
    Credentials:
        username: admin
        password: admin123
        role: admin (id=2)
    
    Usage:
        def test_admin_action(test_admin):
            assert test_admin.user_roles[0].role_id == 2
    """
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=hash_password('admin123'),
        first_name='Admin',
        last_name='User',
        phone='555-0101'
    )
    db_session.add(admin)
    db_session.flush()  # Get admin.id
    
    # Assign admin role via RoleUser
    role_user = RoleUser(
        user_id=admin.id,
        role_id=2  # Admin role
    )
    db_session.add(role_user)
    db_session.commit()
    db_session.refresh(admin)
    
    # Store plain password for login tests
    admin._plain_password = 'admin123'
    
    return admin


@pytest.fixture
def multiple_users(db_session, test_role_user):
    """
    Create multiple test users in database with role assignments.
    
    Scope: function (auto-deleted via rollback)
    
    Returns:
        list[User]: 5 test users with fake data
    
    Usage:
        def test_list_users(multiple_users):
            assert len(multiple_users) == 5
    """
    users = []
    for i in range(5):
        user = User(
            username=f'user{i}_{fake.user_name()}',
            email=f'user{i}_{fake.email()}',
            password_hash=hash_password('password123'),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number()[:20]
        )
        db_session.add(user)
        db_session.flush()  # Get user.id
        
        # Assign role
        role_user = RoleUser(
            user_id=user.id,
            role_id=1  # Regular user
        )
        db_session.add(role_user)
        users.append(user)
    
    db_session.commit()
    
    # Refresh all users to get IDs
    for user in users:
        db_session.refresh(user)
    
    return users


@pytest.fixture
def user_with_custom_data(db_session, test_role_user):
    """
    Factory function to create user with custom data.
    
    Scope: function
    
    Usage:
        def test_custom_user(user_with_custom_data):
            user = user_with_custom_data(username='specific_name', email='test@test.com')
            assert user.username == 'specific_name'
    """
    def _create_user(**kwargs):
        defaults = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password_hash': hash_password('password123'),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'phone': fake.phone_number()[:20]
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        db_session.add(user)
        db_session.flush()  # Get user.id
        
        # Assign default role (user)
        role_user_assoc = RoleUser(
            user_id=user.id,
            role_id=1  # Default to regular user
        )
        db_session.add(role_user_assoc)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    return _create_user
