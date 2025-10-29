"""
Integration Tests: Product Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests product service with real database operations.
Validates complete flows: creation, retrieval, filtering, updates.

These tests use a real database (PostgreSQL test) to ensure:
- Services and repositories work together correctly
- Reference data (categories, pet types) is validated properly
- Database constraints are respected
- Transactions commit properly
- Foreign keys and relationships work
"""
import pytest
from flask import g
from app.products.services.product_service import ProductService
from app.products.repositories.product_repository import ProductRepository


class TestProductCreationIntegration:
    """Integration tests for product creation flow."""
    
    def test_create_product_with_valid_data(self, app, integration_db_session):
        """Test complete product creation with category and pet_type validation."""
        with app.app_context():
            # Inject test database session
            g.db = integration_db_session
            
            # Force ReferenceDataCache to use test database
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            product_data = {
                'description': 'Premium Dog Food - High-quality food for adult dogs',
                'category': 'food',  # String description (will be converted to ID)
                'pet_type': 'dog',   # String description (will be converted to ID)
                'price': 29.99,
                'stock_quantity': 100,
                'brand': 'PetNutrition',
                'weight': 5.0,
                'sku': 'DF001'
            }
            
            # Act
            new_product = product_service.create_product(**product_data)
            
            # Assert
            assert new_product is not None
            assert new_product.description == 'Premium Dog Food - High-quality food for adult dogs'
            assert new_product.sku == 'DF001'
            assert new_product.price == 29.99
            assert new_product.stock_quantity == 100
            assert new_product.is_active is True
            
            # Verify category and pet_type were converted to IDs
            assert new_product.product_category_id is not None
            assert new_product.pet_type_id is not None
            
            # Verify relationships work
            assert new_product.category is not None
            assert new_product.category.category == 'food'
            assert new_product.pet_type is not None
            assert new_product.pet_type.type == 'dog'
    
    def test_create_product_with_invalid_category(self, app, integration_db_session):
        """Test that creating product with invalid category fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            product_data = {
                'description': 'Test Product',
                'category': 'invalid_category',  # Invalid category
                'pet_type': 'dog',
                'price': 19.99,
                'stock_quantity': 50,
                'sku': 'TE001'
            }
            
            # Act
            new_product = product_service.create_product(**product_data)
            
            # Assert
            assert new_product is None  # Should fail validation
    
    def test_create_product_with_invalid_pet_type(self, app, integration_db_session):
        """Test that creating product with invalid pet_type fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            product_data = {
                'description': 'Test Product',
                'category': 'food',
                'pet_type': 'dinosaur',  # Invalid pet type
                'price': 19.99,
                'stock_quantity': 50,
                'sku': 'TE002'
            }
            
            # Act
            new_product = product_service.create_product(**product_data)
            
            # Assert
            assert new_product is None  # Should fail validation
    
    def test_create_product_with_duplicate_sku(self, app, integration_db_session):
        """Test that creating product with duplicate SKU fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            product_data = {
                'description': 'First Product',
                'category': 'toys',
                'pet_type': 'cat',
                'price': 15.99,
                'stock_quantity': 30,
                'sku': 'DUPSK'
            }
            
            # Act - Create first product
            first_product = product_service.create_product(**product_data)
            assert first_product is not None
            
            # Act - Try to create second product with same SKU
            product_data['description'] = 'Second Product'
            second_product = product_service.create_product(**product_data)
            
            # Assert
            assert second_product is None  # Should fail due to duplicate SKU


class TestProductRetrievalIntegration:
    """Integration tests for product retrieval."""
    
    def test_get_product_by_id(self, app, integration_db_session):
        """Test retrieving product by ID."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create a product first
            product_service = ProductService()
            product_data = {
                'description': 'Cat Toy - Fun toy for cats',
                'category': 'toys',
                'pet_type': 'cat',
                'price': 9.99,
                'stock_quantity': 50,
                'sku': 'CT001'
            }
            created_product = product_service.create_product(**product_data)
            assert created_product is not None
            product_id = created_product.id
            
            # Act - Retrieve by ID
            retrieved_product = product_service.get_product_by_id(product_id)
            
            # Assert
            assert retrieved_product is not None
            assert retrieved_product.id == product_id
            assert 'Cat Toy' in retrieved_product.description
            assert retrieved_product.sku == 'CT001'
    
    def test_get_product_by_sku(self, app, integration_db_session):
        """Test retrieving product by SKU."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create a product first
            product_service = ProductService()
            product_data = {
                'description': 'Bird Food - Nutritious food for birds',
                'category': 'food',
                'pet_type': 'bird',
                'price': 12.99,
                'stock_quantity': 75,
                'sku': 'BF001'
            }
            created_product = product_service.create_product(**product_data)
            assert created_product is not None
            
            # Act - Retrieve by SKU
            retrieved_product = product_service.get_product_by_sku('BF001')
            
            # Assert
            assert retrieved_product is not None
            assert retrieved_product.sku == 'BF001'
            assert 'Bird Food' in retrieved_product.description
    
    def test_get_nonexistent_product(self, app, integration_db_session):
        """Test retrieving non-existent product returns None."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            
            # Act
            product = product_service.get_product_by_id(99999)
            
            # Assert
            assert product is None


class TestProductFilteringIntegration:
    """Integration tests for product filtering."""
    
    def test_filter_products_by_category(self, app, integration_db_session):
        """Test filtering products by category description."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create products in different categories
            product_service = ProductService()
            
            # Food product
            product_service.create_product(
                description='Dog Food - Premium nutrition',
                category='food',
                pet_type='dog',
                price=25.99,
                stock_quantity=100,
                sku='FO001'
            )
            
            # Toy product
            product_service.create_product(
                description='Dog Toy - Squeaky ball',
                category='toys',
                pet_type='dog',
                price=8.99,
                stock_quantity=50,
                sku='TO001'
            )
            
            # Act - Filter by 'food' category
            food_products = product_service.get_products_by_filters({'category': 'food'})
            
            # Assert
            assert len(food_products) >= 1
            assert all(p.category.category == 'food' for p in food_products)
    
    def test_filter_products_by_pet_type(self, app, integration_db_session):
        """Test filtering products by pet type description."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create products for different pets
            product_service = ProductService()
            
            # Dog product
            product_service.create_product(
                description='Dog Collar - Adjustable',
                category='accessories',
                pet_type='dog',
                price=15.99,
                stock_quantity=30,
                sku='DC001'
            )
            
            # Cat product
            product_service.create_product(
                description='Cat Collar - With bell',
                category='accessories',
                pet_type='cat',
                price=12.99,
                stock_quantity=40,
                sku='CC001'
            )
            
            # Act - Filter by 'cat' pet type
            cat_products = product_service.get_products_by_filters({'pet_type': 'cat'})
            
            # Assert
            assert len(cat_products) >= 1
            assert all(p.pet_type.type == 'cat' for p in cat_products)
    
    def test_filter_products_with_invalid_category(self, app, integration_db_session):
        """Test that filtering with invalid category returns empty list."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            product_service = ProductService()
            
            # Act - Filter by invalid category
            products = product_service.get_products_by_filters({'category': 'invalid_category'})
            
            # Assert
            assert products == []


class TestProductUpdateIntegration:
    """Integration tests for product updates."""
    
    def test_update_product_basic_fields(self, app, integration_db_session):
        """Test updating basic product fields."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create a product
            product_service = ProductService()
            product_data = {
                'description': 'Fish Food - Tropical blend',
                'category': 'food',
                'pet_type': 'fish',
                'price': 8.99,
                'stock_quantity': 60,
                'sku': 'FF001'
            }
            created_product = product_service.create_product(**product_data)
            assert created_product is not None
            product_id = created_product.id
            
            # Act - Update price and stock
            updated_product = product_service.update_product(
                product_id,
                price=10.99,
                stock_quantity=80
            )
            
            # Assert
            assert updated_product is not None
            assert updated_product.price == 10.99
            assert updated_product.stock_quantity == 80
            assert 'Fish Food' in updated_product.description  # Unchanged
    
    def test_update_product_category(self, app, integration_db_session):
        """Test updating product category (description → ID conversion)."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create a product
            product_service = ProductService()
            product_data = {
                'description': 'Pet Bed - Comfortable and warm',
                'category': 'bedding',
                'pet_type': 'dog',
                'price': 35.99,
                'stock_quantity': 20,
                'sku': 'PB001'
            }
            created_product = product_service.create_product(**product_data)
            assert created_product is not None
            product_id = created_product.id
            
            # Act - Update category to 'accessories'
            updated_product = product_service.update_product(
                product_id,
                category='accessories'
            )
            
            # Assert
            assert updated_product is not None
            assert updated_product.category.category == 'accessories'
