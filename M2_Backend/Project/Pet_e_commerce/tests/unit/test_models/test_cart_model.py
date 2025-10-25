"""
Unit tests for Cart models.

Tests cover:
- Cart model creation and validation
- CartItem model CRUD
- User-Cart relationship
- Cart-Product relationships via CartItem
- CartItem unique constraint (product_id + cart_id)
- Finalized flag behavior
- Cascading deletes
"""
import pytest
from app.sales.models.cart import Cart, CartItem
from datetime import datetime


@pytest.mark.unit
@pytest.mark.sales
class TestCartItemModel:
    """Test suite for CartItem model."""
    
    def test_cart_item_creation_with_valid_data(self, db_session, test_cart, test_product):
        """Test creating a cart item with valid data."""
        # Arrange & Act
        cart_item = CartItem(
            cart_id=test_cart.id,
            product_id=test_product.id,
            amount=29.99,
            quantity=2
        )
        db_session.add(cart_item)
        db_session.commit()
        
        # Assert
        assert cart_item.id is not None
        assert cart_item.cart_id == test_cart.id
        assert cart_item.product_id == test_product.id
        assert cart_item.amount == 29.99
        assert cart_item.quantity == 2
    
    def test_cart_item_has_cart_relationship(self, test_cart_with_items):
        """Test that CartItem has valid relationship with Cart."""
        # Arrange
        cart_item = test_cart_with_items.items[0]
        
        # Assert
        assert cart_item.cart is not None
        assert cart_item.cart.id == test_cart_with_items.id
    
    def test_cart_item_has_product_relationship(self, test_cart_with_items):
        """Test that CartItem has valid relationship with Product."""
        # Arrange
        cart_item = test_cart_with_items.items[0]
        
        # Assert
        assert cart_item.product is not None
        assert cart_item.product.id is not None
        assert cart_item.product.sku is not None
    
    def test_cart_item_unique_constraint(self, db_session, test_cart_with_items, test_product):
        """Test that (product_id, cart_id) must be unique - can't add same product twice."""
        # Arrange
        # test_cart_with_items already has test_product
        duplicate_item = CartItem(
            cart_id=test_cart_with_items.id,
            product_id=test_product.id,  # Same product
            amount=15.00,
            quantity=1
        )
        db_session.add(duplicate_item)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_cart_item_repr_returns_formatted_string(self, test_cart_with_items):
        """Test CartItem string representation."""
        # Arrange
        cart_item = test_cart_with_items.items[0]
        
        # Act
        repr_string = repr(cart_item)
        
        # Assert
        assert "CartItem" in repr_string
        assert str(cart_item.id) in repr_string
        assert str(cart_item.cart_id) in repr_string
        assert str(cart_item.product_id) in repr_string
        assert str(cart_item.quantity) in repr_string


@pytest.mark.unit
@pytest.mark.sales
class TestCartModel:
    """Test suite for Cart model."""
    
    def test_cart_creation_with_valid_data(self, db_session, test_user):
        """Test creating a cart with required fields."""
        # Arrange & Act
        cart = Cart(
            user_id=test_user.id,
            finalized=False
        )
        db_session.add(cart)
        db_session.commit()
        
        # Assert
        assert cart.id is not None
        assert cart.user_id == test_user.id
        assert cart.finalized is False
    
    def test_cart_has_user_relationship(self, test_cart, test_user):
        """Test that Cart has valid relationship with User."""
        # Assert
        assert test_cart.user is not None
        assert test_cart.user.id == test_user.id
        assert test_cart in test_user.carts
    
    def test_cart_default_finalized_is_false(self, db_session, test_user):
        """Test that finalized defaults to False."""
        # Arrange & Act
        cart = Cart(user_id=test_user.id)
        db_session.add(cart)
        db_session.commit()
        
        # Assert
        assert cart.finalized is False
    
    def test_cart_with_created_at_timestamp(self, db_session, test_user):
        """Test creating a cart with optional created_at field."""
        # Arrange & Act
        now = datetime.utcnow()
        cart = Cart(
            user_id=test_user.id,
            finalized=False,
            created_at=now
        )
        db_session.add(cart)
        db_session.commit()
        
        # Assert
        assert cart.created_at is not None
        assert cart.created_at == now
    
    def test_cart_has_items_relationship(self, test_cart_with_items):
        """Test that Cart has valid relationship with CartItems."""
        # Assert
        assert len(test_cart_with_items.items) == 2
        assert all(isinstance(item, CartItem) for item in test_cart_with_items.items)
        assert all(item.cart_id == test_cart_with_items.id for item in test_cart_with_items.items)
    
    def test_cart_cascade_delete_removes_items(self, db_session, test_cart_with_items):
        """Test that deleting a cart cascades to delete its items."""
        # Arrange
        cart_id = test_cart_with_items.id
        item_ids = [item.id for item in test_cart_with_items.items]
        assert len(item_ids) == 2  # Verify we have items
        
        # Act
        db_session.delete(test_cart_with_items)
        db_session.commit()
        
        # Assert - cart items should be deleted
        for item_id in item_ids:
            deleted_item = db_session.query(CartItem).filter_by(id=item_id).first()
            assert deleted_item is None
    
    def test_cart_finalized_can_be_set_to_true(self, db_session, test_cart):
        """Test that finalized flag can be updated to True."""
        # Arrange
        test_cart.finalized = False
        db_session.commit()
        
        # Act
        test_cart.finalized = True
        db_session.commit()
        db_session.refresh(test_cart)
        
        # Assert
        assert test_cart.finalized is True
    
    def test_cart_repr_returns_formatted_string(self, test_cart):
        """Test Cart string representation."""
        # Act
        repr_string = repr(test_cart)
        
        # Assert
        assert "Cart" in repr_string
        assert str(test_cart.id) in repr_string
        assert str(test_cart.user_id) in repr_string
        assert str(test_cart.finalized) in repr_string
