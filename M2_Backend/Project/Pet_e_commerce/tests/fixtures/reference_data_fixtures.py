"""
Reference Data Fixtures
~~~~~~~~~~~~~~~~~~~~~~~

Provides reference data seeding for integration tests.
Seeds all lookup tables (roles, product categories, pet types, statuses).
"""
import pytest
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def seed_reference_data(test_db_engine):
    """
    Seed all reference data tables for integration tests.
    
    Scope: session (created once for all tests)
    
    Populates:
    - roles (user, admin, manager)
    - product_category (food, toys, accessories, grooming, health, bedding)
    - pet_type (dog, cat, bird, fish, rabbit, hamster)
    - order_status (pending, processing, shipped, delivered, cancelled)
    - invoice_status (pending, paid, overdue, refunded)
    - return_status (pending, approved, rejected, completed)
    """
    from app.auth.models import Role
    from app.products.models import ProductCategory, PetType
    from app.sales.models import OrderStatus, InvoiceStatus, ReturnStatus
    
    with Session(test_db_engine) as session:
        # Seed Roles
        roles_data = [
            {'id': 1, 'name': 'user', 'description': 'Regular user with standard permissions'},
            {'id': 2, 'name': 'admin', 'description': 'Administrator with full permissions'},
            {'id': 3, 'name': 'manager', 'description': 'Manager with elevated permissions'},
        ]
        
        for role_data in roles_data:
            if not session.query(Role).filter_by(id=role_data['id']).first():
                role = Role(**role_data)
                session.add(role)
        
        # Seed Product Categories
        categories_data = [
            {'id': 1, 'category': 'food'},
            {'id': 2, 'category': 'toys'},
            {'id': 3, 'category': 'accessories'},
            {'id': 4, 'category': 'grooming'},
            {'id': 5, 'category': 'health'},
            {'id': 6, 'category': 'bedding'},
        ]
        
        for cat_data in categories_data:
            if not session.query(ProductCategory).filter_by(id=cat_data['id']).first():
                category = ProductCategory(**cat_data)
                session.add(category)
        
        # Seed Pet Types
        pet_types_data = [
            {'id': 1, 'type': 'dog'},
            {'id': 2, 'type': 'cat'},
            {'id': 3, 'type': 'bird'},
            {'id': 4, 'type': 'fish'},
            {'id': 5, 'type': 'rabbit'},
            {'id': 6, 'type': 'hamster'},
        ]
        
        for pet_data in pet_types_data:
            if not session.query(PetType).filter_by(id=pet_data['id']).first():
                pet_type = PetType(**pet_data)
                session.add(pet_type)
        
        # Seed Order Statuses
        order_statuses_data = [
            {'id': 1, 'status': 'pending'},
            {'id': 2, 'status': 'processing'},
            {'id': 3, 'status': 'shipped'},
            {'id': 4, 'status': 'delivered'},
            {'id': 5, 'status': 'cancelled'},
        ]
        
        for status_data in order_statuses_data:
            if not session.query(OrderStatus).filter_by(id=status_data['id']).first():
                status = OrderStatus(**status_data)
                session.add(status)
        
        # Seed Invoice Statuses
        invoice_statuses_data = [
            {'id': 1, 'name': 'pending'},
            {'id': 2, 'name': 'paid'},
            {'id': 3, 'name': 'overdue'},
            {'id': 4, 'name': 'refunded'},
        ]
        
        for status_data in invoice_statuses_data:
            if not session.query(InvoiceStatus).filter_by(id=status_data['id']).first():
                status = InvoiceStatus(**status_data)
                session.add(status)
        
        # Seed Return Statuses
        return_statuses_data = [
            {'id': 1, 'status': 'requested'},
            {'id': 2, 'status': 'approved'},
            {'id': 3, 'status': 'rejected'},
            {'id': 4, 'status': 'processing'},
            {'id': 5, 'status': 'completed'},
        ]
        
        for status_data in return_statuses_data:
            if not session.query(ReturnStatus).filter_by(id=status_data['id']).first():
                status = ReturnStatus(**status_data)
                session.add(status)
        
        session.commit()
        print("[OK] Reference data seeded successfully")


@pytest.fixture(scope="session", autouse=True)
def setup_reference_data(app, test_db_engine, seed_reference_data):
    """
    Auto-use fixture that ensures reference data is seeded before any integration tests.
    
    autouse=True means this runs automatically for all integration tests.
    """
    # Initialize ReferenceDataCache after seeding, within Flask app context
    with app.app_context():
        from app.core.reference_data import ReferenceDataCache
        ReferenceDataCache.initialize()
        print("[OK] ReferenceDataCache initialized")
    
    yield
    
    # Cleanup handled by test_db_engine fixture
