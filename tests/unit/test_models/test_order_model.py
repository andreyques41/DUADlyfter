"""
Unit tests for Order models.

Tests cover:
- OrderStatus model creation and validation
- OrderItem model CRUD
- Order model creation and validation
- Order-Cart relationship (one-to-one)
- Order-User relationship
- Order-Status relationship
- OrderItem unique constraint (product_id + order_id)
- Cascading deletes
- Total amount tracking
"""
import pytest
from app.sales.models.order import Order, OrderItem, OrderStatus
from datetime import datetime


@pytest.mark.unit
@pytest.mark.sales
class TestOrderStatusModel:
    """Test suite for OrderStatus model."""
    
    def test_order_status_repr(self, test_order_status_pending):
        """Test OrderStatus string representation and fixture creation."""
        # Act
        repr_string = repr(test_order_status_pending)
        
        # Assert - validates creation AND repr
        assert test_order_status_pending.id is not None
        assert test_order_status_pending.status == "Pending"
        assert "OrderStatus" in repr_string
        assert "Pending" in repr_string
        assert str(test_order_status_pending.id) in repr_string
    
    def test_order_status_unique_constraint(self, db_session, test_order_status_pending):
        """Test that status names must be unique."""
        # Arrange
        duplicate_status = OrderStatus(status="Pending")
        db_session.add(duplicate_status)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()


@pytest.mark.unit
@pytest.mark.sales
class TestOrderItemModel:
    """Test suite for OrderItem model."""
    
    def test_order_item_creation_with_valid_data(self, db_session, test_user, test_cart, test_product, test_order_status_pending):
        """Test creating an order item with valid data - fresh order."""
        # Arrange - Create a new order without items
        order = Order(
            cart_id=test_cart.id,
            user_id=test_user.id,
            order_status_id=test_order_status_pending.id,
            total_amount=29.99
        )
        db_session.add(order)
        db_session.flush()
        
        # Act - Add order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            amount=29.99,
            quantity=1
        )
        db_session.add(order_item)
        db_session.commit()
        
        # Assert
        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == test_product.id
        assert order_item.amount == 29.99
        assert order_item.quantity == 1
    
    def test_order_item_has_order_relationship(self, test_order):
        """Test that OrderItem has valid relationship with Order."""
        # Arrange
        order_item = test_order.items[0]
        
        # Assert
        assert order_item.order is not None
        assert order_item.order.id == test_order.id
    
    def test_order_item_has_product_relationship(self, test_order):
        """Test that OrderItem has valid relationship with Product."""
        # Arrange
        order_item = test_order.items[0]
        
        # Assert
        assert order_item.product is not None
        assert order_item.product.id is not None
        assert order_item.product.sku is not None
    
    def test_order_item_unique_constraint(self, db_session, test_order):
        """Test that (product_id, order_id) must be unique."""
        # Arrange - test_order already has items with specific products
        # Get first item's product_id from test_order
        existing_product_id = test_order.items[0].product_id
        
        duplicate_item = OrderItem(
            order_id=test_order.id,
            product_id=existing_product_id,  # Same product as first item
            amount=15.00,
            quantity=1
        )
        db_session.add(duplicate_item)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_order_item_repr_returns_formatted_string(self, test_order):
        """Test OrderItem string representation."""
        # Arrange
        order_item = test_order.items[0]
        
        # Act
        repr_string = repr(order_item)
        
        # Assert
        assert "OrderItem" in repr_string
        assert str(order_item.id) in repr_string
        assert str(order_item.order_id) in repr_string
        assert str(order_item.product_id) in repr_string
        assert str(order_item.quantity) in repr_string


@pytest.mark.unit
@pytest.mark.sales
class TestOrderModel:
    """Test suite for Order model."""
    
    def test_order_creation_with_valid_data(self, test_order):
        """Test creating an order with all required fields."""
        # Assert
        assert test_order.id is not None
        assert test_order.cart_id is not None
        assert test_order.user_id is not None
        assert test_order.order_status_id is not None
        assert test_order.total_amount > 0
    
    def test_order_has_cart_relationship(self, test_order, test_cart_with_items):
        """Test that Order has valid one-to-one relationship with Cart."""
        # Assert
        assert test_order.cart is not None
        assert test_order.cart.id == test_cart_with_items.id
        assert test_cart_with_items.order == test_order
    
    def test_order_has_user_relationship(self, test_order, test_user):
        """Test that Order has valid relationship with User."""
        # Assert
        assert test_order.user is not None
        assert test_order.user.id == test_user.id
        assert test_order in test_user.orders
    
    def test_order_has_status_relationship(self, test_order, test_order_status_pending):
        """Test that Order has valid relationship with OrderStatus."""
        # Assert
        assert test_order.status is not None
        assert test_order.status.id == test_order_status_pending.id
        assert test_order.status.status == "Pending"
    
    def test_order_has_items_relationship(self, test_order):
        """Test that Order has valid relationship with OrderItems."""
        # Assert
        assert len(test_order.items) >= 1
        assert all(isinstance(item, OrderItem) for item in test_order.items)
        assert all(item.order_id == test_order.id for item in test_order.items)
    
    def test_order_cart_unique_constraint(self, db_session, test_order, test_user, test_order_status_pending):
        """Test that cart_id must be unique - one order per cart."""
        # Arrange
        duplicate_order = Order(
            cart_id=test_order.cart_id,  # Same cart
            user_id=test_user.id,
            order_status_id=test_order_status_pending.id,
            total_amount=100.00
        )
        db_session.add(duplicate_order)
        
        # Act & Assert
        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.commit()
    
    def test_order_with_shipping_address(self, db_session, test_user, test_cart, test_order_status_pending):
        """Test creating an order with optional shipping address."""
        # Arrange & Act
        order = Order(
            cart_id=test_cart.id,
            user_id=test_user.id,
            order_status_id=test_order_status_pending.id,
            total_amount=50.00,
            shipping_address="123 Main St, City, State 12345"
        )
        db_session.add(order)
        db_session.commit()
        
        # Assert
        assert order.shipping_address == "123 Main St, City, State 12345"
    
    def test_order_with_created_at_timestamp(self, db_session, test_user, test_cart, test_order_status_pending):
        """Test creating an order with optional created_at field."""
        # Arrange & Act
        now = datetime.utcnow()
        order = Order(
            cart_id=test_cart.id,
            user_id=test_user.id,
            order_status_id=test_order_status_pending.id,
            total_amount=75.00,
            created_at=now
        )
        db_session.add(order)
        db_session.commit()
        
        # Assert
        assert order.created_at is not None
        assert order.created_at == now
    
    def test_order_cascade_delete_removes_items(self, db_session, test_order):
        """Test that deleting an order cascades to delete its items."""
        # Arrange
        order_id = test_order.id
        item_ids = [item.id for item in test_order.items]
        assert len(item_ids) >= 1  # Verify we have items
        
        # Act
        db_session.delete(test_order)
        db_session.commit()
        
        # Assert - order items should be deleted
        for item_id in item_ids:
            deleted_item = db_session.query(OrderItem).filter_by(id=item_id).first()
            assert deleted_item is None
    
    def test_order_total_amount_tracking(self, test_order):
        """Test that order correctly tracks total_amount."""
        # Assert
        assert test_order.total_amount > 0
        # Calculate expected total from items
        expected_total = sum(item.amount * item.quantity for item in test_order.items)
        assert test_order.total_amount == expected_total
    
    def test_order_repr_returns_formatted_string(self, test_order):
        """Test Order string representation."""
        # Act
        repr_string = repr(test_order)
        
        # Assert
        assert "Order" in repr_string
        assert str(test_order.id) in repr_string
        assert str(test_order.user_id) in repr_string
        assert str(test_order.total_amount) in repr_string
        assert str(test_order.order_status_id) in repr_string
