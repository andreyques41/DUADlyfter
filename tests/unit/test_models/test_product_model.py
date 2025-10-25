"""
Unit tests for Product models.

Tests cover:
- Product model creation and validation
- ProductCategory model CRUD
- PetType model CRUD
- SKU uniqueness constraints
- Stock and availability validation
- Foreign key relationships
- Optional field handling
"""
import pytest
from app.products.models.product import Product, ProductCategory, PetType


@pytest.mark.unit
@pytest.mark.products
class TestProductCategoryModel:
    """Test suite for ProductCategory model."""
    
    def test_product_category_repr(self, test_category_food):
        """Test ProductCategory string representation and that fixture creates valid category."""
        # Act
        repr_string = repr(test_category_food)
        
        # Assert - validates creation AND repr
        assert test_category_food.id is not None
        assert test_category_food.category == "Food"
        assert "ProductCategory" in repr_string
        assert "Food" in repr_string
        assert str(test_category_food.id) in repr_string
    
    def test_product_category_unique_constraint(self, db_session, test_category_food):
        """Test that category names must be unique."""
        # Arrange
        duplicate_category = ProductCategory(category="Food")
        db_session.add(duplicate_category)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()


@pytest.mark.unit
@pytest.mark.products
class TestPetTypeModel:
    """Test suite for PetType model."""
    
    def test_pet_type_repr(self, test_pet_type_dog):
        """Test PetType string representation and that fixture creates valid pet type."""
        # Act
        repr_string = repr(test_pet_type_dog)
        
        # Assert - validates creation AND repr
        assert test_pet_type_dog.id is not None
        assert test_pet_type_dog.type == "Dog"
        assert "PetType" in repr_string
        assert "Dog" in repr_string
        assert str(test_pet_type_dog.id) in repr_string
    
    def test_pet_type_unique_constraint(self, db_session, test_pet_type_cat):
        """Test that pet type names must be unique."""
        # Arrange
        duplicate_pet_type = PetType(type="Cat")
        db_session.add(duplicate_pet_type)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()


@pytest.mark.unit
@pytest.mark.products
class TestProductModel:
    """Test suite for Product model."""
    
    def test_product_creation_with_valid_data(self, test_product):
        """Test creating a product with all required fields."""
        # Assert
        assert test_product.id is not None
        assert test_product.sku == "DOG01"
        assert test_product.description == "Premium Dog Food"
        assert test_product.stock_quantity == 50
        assert test_product.price == 29.99
        assert test_product.product_category_id is not None
        assert test_product.pet_type_id is not None
    
    def test_product_sku_is_unique(self, db_session, test_product):
        """Test that SKU must be unique across products."""
        # Arrange
        duplicate_product = Product(
            sku="DOG01",  # Same SKU as test_product
            description="Another product",
            product_category_id=test_product.product_category_id,
            pet_type_id=test_product.pet_type_id,
            stock_quantity=10,
            price=25.00
        )
        db_session.add(duplicate_product)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_product_has_category_relationship(self, db_session, test_product):
        """Test that Product has valid relationship with ProductCategory."""
        # Re-query to ensure we're in the same session
        category = db_session.query(ProductCategory).filter_by(id=test_product.product_category_id).first()
        
        # Assert
        assert test_product.category is not None
        assert test_product.category.id == category.id
        assert test_product.category.category == "Food"
    
    def test_product_has_pet_type_relationship(self, db_session, test_product):
        """Test that Product has valid relationship with PetType."""
        # Re-query to ensure we're in the same session
        pet_type = db_session.query(PetType).filter_by(id=test_product.pet_type_id).first()
        
        # Assert
        assert test_product.pet_type is not None
        assert test_product.pet_type.id == pet_type.id
        assert test_product.pet_type.type == "Dog"
    
    def test_product_optional_fields_can_be_null(self, db_session, test_category_food, test_pet_type_cat):
        """Test that optional fields (brand, weight) can be null, is_active has default."""
        # Arrange & Act
        product = Product(
            sku="CT001",
            description="Cat Toy",
            product_category_id=1,
            pet_type_id=2,
            stock_quantity=20,
            price=9.99
            # Optional fields not provided - brand, weight, internal_cost, supplier_info, etc.
        )
        db_session.add(product)
        db_session.commit()
        
        # Assert
        assert product.id is not None
        assert product.brand is None
        assert product.weight is None
        assert product.is_active == True  # Default value from column definition
    
    def test_product_is_available_with_stock(self, test_product):
        """Test is_available() returns True when product has stock and is active."""
        # Arrange
        test_product.is_active = True
        test_product.stock_quantity = 10
        
        # Act
        result = test_product.is_available()
        
        # Assert
        assert result is True
    
    def test_product_is_available_without_stock(self, out_of_stock_product):
        """Test is_available() returns False when product has no stock."""
        # Arrange
        out_of_stock_product.is_active = True
        out_of_stock_product.stock_quantity = 0
        
        # Act
        result = out_of_stock_product.is_available()
        
        # Assert
        assert result is False
    
    def test_product_is_available_when_inactive(self, test_product):
        """Test is_available() returns False when product is inactive."""
        # Arrange
        test_product.is_active = False
        test_product.stock_quantity = 50
        
        # Act
        result = test_product.is_available()
        
        # Assert
        assert result is False
    
    def test_product_repr_returns_formatted_string(self, test_product):
        """Test Product string representation."""
        # Act
        repr_string = repr(test_product)
        
        # Assert
        assert "Product" in repr_string
        assert "DOG01" in repr_string
        assert "Premium Dog Food" in repr_string
        assert str(test_product.id) in repr_string
    
    def test_product_with_all_optional_fields(self, db_session, test_category_toys, test_pet_type_cat):
        """Test creating a product with all optional fields populated."""
        # Arrange & Act
        from datetime import datetime
        product = Product(
            sku="CT002",
            description="Laser Pointer Toy",
            product_category_id=test_category_toys.id,
            pet_type_id=test_pet_type_cat.id,
            stock_quantity=100,
            price=12.99,
            brand="PetPlay",
            weight=0.15,
            is_active=True,
            internal_cost=5.50,
            supplier_info="Supplier ABC - Contact: 555-1234",
            created_by="admin@petstore.com",
            last_updated=datetime.utcnow()
        )
        db_session.add(product)
        db_session.commit()
        
        # Assert
        assert product.id is not None
        assert product.brand == "PetPlay"
        assert product.weight == 0.15
        assert product.is_active is True
        assert product.internal_cost == 5.50
        assert product.supplier_info == "Supplier ABC - Contact: 555-1234"
        assert product.created_by == "admin@petstore.com"
        assert product.last_updated is not None
