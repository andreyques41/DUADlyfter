"""
Product Test Fixtures
~~~~~~~~~~~~~~~~~~~~

Provides test data for Product, ProductCategory, PetType models using Faker.

Fixtures:
- test_category_food: Food category
- test_category_toys: Toys category
- test_pet_type_dog: Dog pet type
- test_pet_type_cat: Cat pet type
- sample_product_data: Dictionary with fake product data
- test_product: Single product in database
- multiple_products: List of test products
"""
import pytest
from faker import Faker
from app.products.models import Product, ProductCategory, PetType
import random

fake = Faker()


# ========================================
# Reference Data Fixtures (Session Scope)
# ========================================

@pytest.fixture(scope="session")
def test_category_food(test_db_engine):
    """Create Food category (id=1)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        category = session.query(ProductCategory).filter_by(id=1).first()
        if not category:
            category = ProductCategory(id=1, category='Food')
            session.add(category)
            session.commit()
            session.refresh(category)
        return category


@pytest.fixture(scope="session")
def test_category_toys(test_db_engine):
    """Create Toys category (id=2)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        category = session.query(ProductCategory).filter_by(id=2).first()
        if not category:
            category = ProductCategory(id=2, category='Toys')
            session.add(category)
            session.commit()
            session.refresh(category)
        return category


@pytest.fixture(scope="session")
def test_category_accessories(test_db_engine):
    """Create Accessories category (id=3)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        category = session.query(ProductCategory).filter_by(id=3).first()
        if not category:
            category = ProductCategory(id=3, category='Accessories')
            session.add(category)
            session.commit()
            session.refresh(category)
        return category


@pytest.fixture(scope="session")
def test_pet_type_dog(test_db_engine):
    """Create Dog pet type (id=1)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        pet_type = session.query(PetType).filter_by(id=1).first()
        if not pet_type:
            pet_type = PetType(id=1, type='Dog')
            session.add(pet_type)
            session.commit()
            session.refresh(pet_type)
        return pet_type


@pytest.fixture(scope="session")
def test_pet_type_cat(test_db_engine):
    """Create Cat pet type (id=2)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        pet_type = session.query(PetType).filter_by(id=2).first()
        if not pet_type:
            pet_type = PetType(id=2, type='Cat')
            session.add(pet_type)
            session.commit()
            session.refresh(pet_type)
        return pet_type


@pytest.fixture(scope="session")
def test_pet_type_bird(test_db_engine):
    """Create Bird pet type (id=3)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        pet_type = session.query(PetType).filter_by(id=3).first()
        if not pet_type:
            pet_type = PetType(id=3, type='Bird')
            session.add(pet_type)
            session.commit()
            session.refresh(pet_type)
        return pet_type


# ========================================
# Product Data Fixtures
# ========================================

@pytest.fixture
def sample_product_data():
    """
    Generate sample product data dictionary (not persisted).
    
    Returns:
        dict: Product data with fake values
    """
    return {
        'sku': fake.bothify(text='?####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'description': f'{fake.word().capitalize()} Pet Product',
        'product_category_id': random.randint(1, 3),
        'pet_type_id': random.randint(1, 3),
        'stock_quantity': random.randint(10, 100),
        'price': round(random.uniform(5.99, 99.99), 2),
        'brand': fake.company(),
        'weight': round(random.uniform(0.1, 10.0), 2),
        'is_active': True
    }


@pytest.fixture
def test_product(db_session, test_category_food, test_pet_type_dog):
    """
    Create single test product in database.
    
    Scope: function (auto-deleted via rollback)
    
    Product:
        sku: 'DOG01'
        description: 'Premium Dog Food'
        category: Food (id=1)
        pet_type: Dog (id=1)
        stock: 50
        price: 29.99
    """
    product = Product(
        sku='DOG01',
        description='Premium Dog Food',
        product_category_id=1,  # Food
        pet_type_id=1,  # Dog
        stock_quantity=50,
        price=29.99,
        brand='PetPro',
        weight=5.0,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_product_cat_toy(db_session, test_category_toys, test_pet_type_cat):
    """
    Create cat toy product in database.
    
    Scope: function (auto-deleted via rollback)
    """
    product = Product(
        sku='CAT01',
        description='Interactive Cat Toy',
        product_category_id=2,  # Toys
        pet_type_id=2,  # Cat
        stock_quantity=30,
        price=15.99,
        brand='FelineF un',
        weight=0.3,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def multiple_products(db_session, test_category_food, test_category_toys, test_category_accessories,
                      test_pet_type_dog, test_pet_type_cat, test_pet_type_bird):
    """
    Create multiple test products in database.
    
    Scope: function (auto-deleted via rollback)
    
    Returns:
        list[Product]: 10 test products with varied data
    """
    products = []
    
    # Predefined realistic pet products
    product_templates = [
        {'sku': 'DF001', 'description': 'Premium Dry Dog Food 10kg', 'category_id': 1, 'pet_id': 1, 'price': 45.99, 'stock': 50, 'brand': 'PetPro', 'weight': 10.0},
        {'sku': 'CF001', 'description': 'Gourmet Wet Cat Food 12-Pack', 'category_id': 1, 'pet_id': 2, 'price': 24.99, 'stock': 40, 'brand': 'FelineChoice', 'weight': 1.2},
        {'sku': 'DT001', 'description': 'Rope Tug Toy for Dogs', 'category_id': 2, 'pet_id': 1, 'price': 12.99, 'stock': 75, 'brand': 'PlayPaws', 'weight': 0.5},
        {'sku': 'CT001', 'description': 'Laser Pointer Cat Toy', 'category_id': 2, 'pet_id': 2, 'price': 9.99, 'stock': 100, 'brand': 'KittyFun', 'weight': 0.1},
        {'sku': 'DA001', 'description': 'Adjustable Dog Collar', 'category_id': 3, 'pet_id': 1, 'price': 18.99, 'stock': 60, 'brand': 'PawGear', 'weight': 0.2},
        {'sku': 'CA001', 'description': 'Luxury Cat Bed', 'category_id': 3, 'pet_id': 2, 'price': 39.99, 'stock': 25, 'brand': 'CozyPets', 'weight': 2.0},
        {'sku': 'BF001', 'description': 'Bird Seed Mix 5kg', 'category_id': 1, 'pet_id': 3, 'price': 19.99, 'stock': 35, 'brand': 'AvianChoice', 'weight': 5.0},
        {'sku': 'BT001', 'description': 'Bird Swing Toy', 'category_id': 2, 'pet_id': 3, 'price': 7.99, 'stock': 80, 'brand': 'BirdPlay', 'weight': 0.15},
        {'sku': 'DF002', 'description': 'Organic Dog Treats 500g', 'category_id': 1, 'pet_id': 1, 'price': 14.99, 'stock': 90, 'brand': 'NaturalPaws', 'weight': 0.5},
        {'sku': 'CF002', 'description': 'Cat Scratching Post', 'category_id': 3, 'pet_id': 2, 'price': 32.99, 'stock': 45, 'brand': 'ScratchMaster', 'weight': 3.5},
    ]
    
    for template in product_templates:
        product = Product(
            sku=template['sku'],
            description=template['description'],
            product_category_id=template['category_id'],
            pet_type_id=template['pet_id'],
            stock_quantity=template['stock'],
            price=template['price'],
            brand=template['brand'],
            weight=template['weight'],
            is_active=True
        )
        db_session.add(product)
        products.append(product)
    
    db_session.commit()
    
    # Refresh all products to get IDs
    for product in products:
        db_session.refresh(product)
    
    return products


@pytest.fixture
def product_with_custom_data(db_session, test_category_food, test_pet_type_dog):
    """
    Factory function to create product with custom data.
    
    Usage:
        def test_custom_product(product_with_custom_data):
            product = product_with_custom_data(sku='CUSTOM', price=99.99)
            assert product.sku == 'CUSTOM'
    """
    def _create_product(**kwargs):
        defaults = {
            'sku': fake.bothify(text='?####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            'description': f'{fake.word().capitalize()} Pet Product',
            'product_category_id': 1,
            'pet_type_id': 1,
            'stock_quantity': 50,
            'price': 29.99,
            'brand': fake.company(),
            'weight': 1.0,
            'is_active': True
        }
        defaults.update(kwargs)
        
        product = Product(**defaults)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product
    
    return _create_product


@pytest.fixture
def out_of_stock_product(db_session, test_category_food, test_pet_type_dog):
    """
    Create product with zero stock for testing stock validation.
    """
    product = Product(
        sku='OOS01',
        description='Out of Stock Product',
        product_category_id=1,
        pet_type_id=1,
        stock_quantity=0,  # Zero stock
        price=19.99,
        brand='TestBrand',
        weight=1.0,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product
