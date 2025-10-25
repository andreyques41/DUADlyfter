"""
Unit tests for Product Schemas.
Tests Marshmallow schema validation, serialization, and deserialization.
"""
import pytest
from marshmallow import ValidationError
from app.products.schemas.product_schema import (
    ProductRegistrationSchema,
    ProductResponseSchema
)


@pytest.mark.unit
@pytest.mark.products
class TestProductRegistrationSchema:
    """Test suite for ProductRegistrationSchema."""

    def test_valid_product_data(self, mocker):
        """Test schema accepts valid product registration data."""
        # Mock ReferenceData validators
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Premium Dog Food',
            'description': 'High-quality dog food for adult dogs',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': 100,
            'brand': 'PetBrand',
            'weight': 5.0
        }
        
        result = schema.load(data)
        
        assert result['name'] == 'Premium Dog Food'
        assert result['description'] == 'High-quality dog food for adult dogs'
        assert result['price'] == 29.99
        assert result['category'] == 'food'
        assert result['pet_type'] == 'dog'
        assert result['stock_quantity'] == 100
        assert result['is_active'] is True  # Default value

    def test_required_fields_missing(self, mocker):
        """Test schema rejects data with missing required fields."""
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product'
            # Missing description, price, category, pet_type, stock_quantity
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        errors = exc_info.value.messages
        assert 'description' in errors
        assert 'price' in errors
        assert 'category' in errors
        assert 'pet_type' in errors
        assert 'stock_quantity' in errors

    def test_price_must_be_non_negative(self, mocker):
        """Test schema rejects negative price."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': -10.99,  # Negative price
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': 10
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'price' in exc_info.value.messages

    def test_stock_quantity_must_be_non_negative(self, mocker):
        """Test schema rejects negative stock quantity."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': -5  # Negative stock
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'stock_quantity' in exc_info.value.messages

    def test_invalid_category(self, mocker):
        """Test schema rejects invalid category."""
        # Mock to return False for invalid category
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=False)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_all_product_categories', return_value={'food': 1, 'toy': 2})
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'invalid_category',
            'pet_type': 'dog',
            'stock_quantity': 10
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'category' in exc_info.value.messages

    def test_invalid_pet_type(self, mocker):
        """Test schema rejects invalid pet type."""
        # Mock to return False for invalid pet type
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=False)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_all_pet_types', return_value={'dog': 1, 'cat': 2})
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'invalid_pet',
            'stock_quantity': 10
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'pet_type' in exc_info.value.messages

    def test_optional_fields_can_be_omitted(self, mocker):
        """Test schema accepts data without optional fields."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': 10
            # Omitting brand, weight, image_url, internal_cost, etc.
        }
        
        result = schema.load(data)
        
        assert result['name'] == 'Test Product'
        assert 'brand' not in result or result.get('brand') is None

    def test_is_active_defaults_to_true(self, mocker):
        """Test that is_active defaults to True when not provided."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': 10
        }
        
        result = schema.load(data)
        
        assert result['is_active'] is True

    def test_admin_fields_are_optional(self, mocker):
        """Test that admin fields (internal_cost, supplier_info) are optional."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_product_category', return_value=True)
        mocker.patch('app.products.schemas.product_schema.ReferenceData.is_valid_pet_type', return_value=True)
        
        schema = ProductRegistrationSchema()
        data = {
            'name': 'Test Product',
            'description': 'Test description',
            'price': 29.99,
            'category': 'food',
            'pet_type': 'dog',
            'stock_quantity': 10,
            'internal_cost': 15.00,
            'supplier_info': 'Supplier XYZ'
        }
        
        result = schema.load(data)
        
        assert result['internal_cost'] == 15.00
        assert result['supplier_info'] == 'Supplier XYZ'


@pytest.mark.unit
@pytest.mark.products
class TestProductResponseSchema:
    """Test suite for ProductResponseSchema."""

    def test_serialization_includes_all_fields(self, test_product, mocker):
        """Test that all expected fields are in serialized response."""
        # Mock ReferenceData methods
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        schema = ProductResponseSchema()
        
        result = schema.dump(test_product)
        
        assert 'id' in result
        assert 'sku' in result
        assert 'description' in result
        assert 'price' in result
        assert 'category' in result
        assert 'pet_type' in result
        assert 'stock_quantity' in result
        assert 'is_active' in result

    def test_category_converted_to_name(self, test_product, mocker):
        """Test that category ID is converted to name."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        schema = ProductResponseSchema()
        
        result = schema.dump(test_product)
        
        assert result['category'] == 'Food'

    def test_pet_type_converted_to_name(self, test_product, mocker):
        """Test that pet_type ID is converted to name."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        schema = ProductResponseSchema()
        
        result = schema.dump(test_product)
        
        assert result['pet_type'] == 'Dog'

    def test_admin_data_not_included_by_default(self, test_product, mocker):
        """Test that admin data is not included by default."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        schema = ProductResponseSchema(include_admin_data=False)
        
        result = schema.dump(test_product)
        
        assert 'admin_data' not in result
        assert 'internal_cost' not in result

    def test_admin_data_included_when_requested(self, test_product, mocker):
        """Test that admin data is included when requested."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        # Set admin fields on test product
        test_product.internal_cost = 15.00
        test_product.supplier_info = 'Supplier XYZ'
        
        schema = ProductResponseSchema(include_admin_data=True)
        
        result = schema.dump(test_product)
        
        assert 'admin_data' in result
        assert result['admin_data']['internal_cost'] == 15.00

    def test_exact_stock_not_shown_by_default(self, test_product, mocker):
        """Test that exact stock is not shown by default."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        schema = ProductResponseSchema(show_exact_stock=False)
        
        result = schema.dump(test_product)
        
        assert 'exact_stock_quantity' not in result

    def test_exact_stock_shown_when_requested(self, test_product, mocker):
        """Test that exact stock is shown when requested."""
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_product_category_name', return_value='Food')
        mocker.patch('app.products.schemas.product_schema.ReferenceData.get_pet_type_name', return_value='Dog')
        
        test_product.stock_quantity = 42
        
        schema = ProductResponseSchema(show_exact_stock=True)
        
        result = schema.dump(test_product)
        
        assert 'exact_stock_quantity' in result
        assert result['exact_stock_quantity'] == 42
