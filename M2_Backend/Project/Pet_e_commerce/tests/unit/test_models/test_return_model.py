"""
Unit tests for Return model.
Tests return creation, validation, relationships, and business logic.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.sales.models.returns import Return, ReturnItem, ReturnStatus


@pytest.mark.unit
@pytest.mark.sales
class TestReturnStatusModel:
    """Test suite for the ReturnStatus model."""

    def test_return_status_repr(self, db_session):
        """Test that return status __repr__ returns a formatted string with creation."""
        status = ReturnStatus(status='Pending')
        db_session.add(status)
        db_session.commit()

        repr_str = repr(status)
        assert f"ReturnStatus(id={status.id}" in repr_str
        assert "Pending" in repr_str

    def test_return_status_unique_constraint(self, db_session):
        """Test that status must be unique."""
        status1 = ReturnStatus(status='Pending')
        db_session.add(status1)
        db_session.commit()

        status2 = ReturnStatus(status='Pending')
        db_session.add(status2)

        with pytest.raises(IntegrityError):
            db_session.commit()


@pytest.mark.unit
@pytest.mark.sales
class TestReturnItemModel:
    """Test suite for the ReturnItem model."""

    def test_return_item_creation_with_valid_data(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test creating a return item with valid data - fresh return."""
        # Create a new return without items
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add return item
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        assert return_item.id is not None
        assert return_item.return_id == return_request.id
        assert return_item.product_id == test_product.id
        assert return_item.quantity == 1
        assert return_item.reason == "Defective product"
        assert return_item.amount == 29.99

    def test_return_item_has_return_relationship(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test that return item has a relationship to return."""
        # Create return
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add return item
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        # Test relationship
        assert return_item.return_request is not None
        assert return_item.return_request.id == return_request.id

    def test_return_item_has_product_relationship(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test that return item has a relationship to product."""
        # Create return
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add return item
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        # Test relationship
        assert return_item.product is not None
        assert return_item.product.id == test_product.id
        assert return_item.product.sku == test_product.sku

    def test_return_item_repr_returns_formatted_string(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test that return item __repr__ returns a formatted string."""
        # Create return
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add return item
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        repr_str = repr(return_item)
        assert f"ReturnItem(id={return_item.id}" in repr_str
        assert f"return_id={return_request.id}" in repr_str
        assert f"product_id={test_product.id}" in repr_str


@pytest.mark.unit
@pytest.mark.sales
class TestReturnModel:
    """Test suite for the Return model."""

    def test_return_creation_with_valid_data(self, db_session, test_order, test_user, test_return_status_pending):
        """Test creating a return with valid data."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)
        db_session.commit()

        assert return_request.id is not None
        assert return_request.order_id == test_order.id
        assert return_request.user_id == test_user.id
        assert return_request.return_status_id == test_return_status_pending.id
        assert return_request.total_amount == 99.99

    def test_return_has_order_relationship(self, db_session, test_order, test_user, test_return_status_pending):
        """Test that return has a relationship to order."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)
        db_session.commit()

        # Test relationship
        assert return_request.order is not None
        assert return_request.order.id == test_order.id
        assert return_request.order.cart_id == test_order.cart_id

    def test_return_has_user_relationship(self, db_session, test_order, test_user, test_return_status_pending):
        """Test that return has a relationship to user."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)
        db_session.commit()

        # Test relationship
        assert return_request.user is not None
        assert return_request.user.id == test_user.id
        assert return_request.user.email == test_user.email

    def test_return_has_status_relationship(self, db_session, test_order, test_user, test_return_status_pending):
        """Test that return has a relationship to status."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)
        db_session.commit()

        # Test relationship
        assert return_request.status is not None
        assert return_request.status.id == test_return_status_pending.id
        assert return_request.status.status == 'Pending'

    def test_return_has_items_relationship(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test that return has a relationship to items."""
        # Create return
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add return item
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        # Test relationship
        assert len(return_request.items) == 1
        assert return_request.items[0].id == return_item.id
        assert return_request.items[0].product_id == test_product.id

    def test_return_requires_order_id(self, db_session, test_user, test_return_status_pending):
        """Test that order_id is required."""
        return_request = Return(
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_return_with_created_at_timestamp(self, db_session, test_order, test_user, test_return_status_pending):
        """Test return can have optional created_at timestamp."""
        created_time = datetime.utcnow()
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99,
            created_at=created_time
        )
        db_session.add(return_request)
        db_session.commit()

        assert return_request.created_at is not None
        assert isinstance(return_request.created_at, datetime)
        assert return_request.created_at == created_time

    def test_return_cascade_delete_removes_items(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test that deleting a return cascades to its items."""
        # Create return with items
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=29.99
        )
        db_session.add(return_request)
        db_session.flush()
        
        return_item = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Defective product",
            amount=29.99
        )
        db_session.add(return_item)
        db_session.commit()

        return_id = return_request.id
        item_id = return_item.id

        # Delete return
        db_session.delete(return_request)
        db_session.commit()

        # Verify return item was also deleted
        deleted_return = db_session.query(Return).filter_by(id=return_id).first()
        deleted_item = db_session.query(ReturnItem).filter_by(id=item_id).first()
        
        assert deleted_return is None
        assert deleted_item is None

    def test_return_total_amount_tracking(self, db_session, test_order, test_user, test_product, test_return_status_pending):
        """Test return tracks total refund amount."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=149.98
        )
        db_session.add(return_request)
        db_session.flush()
        
        # Add two return items
        return_item1 = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=2,
            reason="Defective product",
            amount=99.98
        )
        return_item2 = ReturnItem(
            return_id=return_request.id,
            product_id=test_product.id,
            quantity=1,
            reason="Changed mind",
            amount=50.00
        )
        db_session.add_all([return_item1, return_item2])
        db_session.commit()

        # Verify total
        assert return_request.total_amount == 149.98
        assert len(return_request.items) == 2

    def test_return_repr_returns_formatted_string(self, db_session, test_order, test_user, test_return_status_pending):
        """Test that return __repr__ returns a formatted string."""
        return_request = Return(
            order_id=test_order.id,
            user_id=test_user.id,
            return_status_id=test_return_status_pending.id,
            total_amount=99.99
        )
        db_session.add(return_request)
        db_session.commit()

        repr_str = repr(return_request)
        assert f"Return(id={return_request.id}" in repr_str
        assert f"order_id={test_order.id}" in repr_str
        assert "99.99" in repr_str
        assert f"status_id={test_return_status_pending.id}" in repr_str
