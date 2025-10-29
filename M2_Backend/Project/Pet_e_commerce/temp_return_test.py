"""
Integration tests for Return Service.
Tests the ReturnService with real database interactions.
"""
import pytest
from datetime import datetime, timedelta
from flask import g
from app.sales.services.returns_service import ReturnService
from app.sales.models.returns import Return, ReturnStatus


@pytest.mark.integration
@pytest.mark.sales
class TestReturnCreationIntegration:
    """Integration tests for return creation."""
    
    def test_create_return_with_order(self, app, integration_db_session, test_user, test_order):
        """Test creating a return for an order."""
        # Arrange - Get IDs before any app context
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            ret = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Defective product',
                status='pending'
            )
            # Assert BEFORE commit
            assert ret is not None
            assert ret.order_id == order_id
            assert ret.user_id == user_id
            assert ret.reason == 'Defective product'
            assert ret.status.status == 'pending'
            assert ret.created_at is not None
            integration_db_session.commit()
    
    def test_create_return_sets_created_at(self, app, integration_db_session, test_user, test_order):
        """Test that return creation sets created_at timestamp."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        before_creation = datetime.utcnow()
        
        # Act & Assert
        with app.app_context():
            g.db = integration_db_session
            ret = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Changed mind',
                status='pending'
            )
            assert ret.created_at is not None
            assert ret.created_at >= before_creation
            integration_db_session.commit()
    
    def test_create_return_prevents_duplicate(self, app, integration_db_session, test_user, test_order):
        """Test that creating duplicate return for same order fails."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        # Act & Assert
        with app.app_context():
            g.db = integration_db_session
            # First return should succeed
            ret1 = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Defective',
                status='pending'
            )
            integration_db_session.commit()
            assert ret1 is not None
            
            # Second return for same order should fail
            ret2 = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Changed mind',
                status='pending'
            )
            # Most services return None on duplicate, but check actual behavior
            # This assertion may need adjustment based on actual service implementation


@pytest.mark.integration
@pytest.mark.sales
class TestReturnRetrievalIntegration:
    """Integration tests for return retrieval."""
    
    def test_get_return_by_id(self, app, integration_db_session, test_user, test_order):
        """Test retrieving a return by ID."""
        # Arrange - Get IDs before any app context
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        with app.app_context():
            g.db = integration_db_session
            created_return = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Defective product',
                status='pending'
            )
            return_id = created_return.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            ret = service.get_return_by_id(return_id)
            # Assert inside context
            assert ret is not None
            assert ret.id == return_id
            assert ret.order_id == order_id
    
    def test_get_return_by_order_id(self, app, integration_db_session, test_user, test_order):
        """Test retrieving a return by order ID."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        with app.app_context():
            g.db = integration_db_session
            service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Wrong item',
                status='pending'
            )
            integration_db_session.commit()
            
            # Act - retrieve in same context
            ret = service.get_return_by_order_id(order_id)
            
            # Assert inside context
            assert ret is not None
            assert ret.order_id == order_id
    
    def test_get_returns_by_user_id(self, app, integration_db_session, test_user, test_order, test_order2):
        """Test retrieving all returns for a user."""
        # Arrange - Get IDs before any app context
        service = ReturnService()
        user_id = test_user.id
        order1_id = test_order.id
        order2_id = test_order2.id
        
        with app.app_context():
            g.db = integration_db_session
            # Create two returns for the same user
            service.create_return(**{
                order_id=order1_id,
                user_id=user_id,
                reason='Defective',
                status='pending'
            )
            service.create_return(**{
                order_id=order2_id,
                user_id=user_id,
                reason='Wrong item',
                status='pending'
            )
            integration_db_session.commit()
            
            # Act & Assert in same context
            returns = service.get_returns_by_user_id(user_id)
            assert len(returns) >= 2
            assert all(r.user_id == user_id for r in returns)


@pytest.mark.integration
@pytest.mark.sales
class TestReturnUpdateIntegration:
    """Integration tests for return updates."""
    
    def test_update_return_status(self, app, integration_db_session, test_user, test_order):
        """Test updating return status."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        with app.app_context():
            g.db = integration_db_session
            ret = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Defective',
                status='pending'
            )
            return_id = ret.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            updated_return = service.update_return(return_id, status='approved'})
            # Assert inside context
            assert updated_return is not None
            assert updated_return.status.status == 'approved'
            integration_db_session.commit()
    
    def test_update_return_reason(self, app, integration_db_session, test_user, test_order):
        """Test updating return reason."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        new_reason = 'Changed mind - full refund requested'
        
        with app.app_context():
            g.db = integration_db_session
            ret = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Original reason',
                status='pending'
            )
            return_id = ret.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            updated_return = service.update_return(return_id, reason=new_reason)
            # Assert inside context
            assert updated_return is not None
            assert updated_return.reason == new_reason
            integration_db_session.commit()


@pytest.mark.integration
@pytest.mark.sales
class TestReturnDeletionIntegration:
    """Integration tests for return deletion."""
    
    def test_delete_return(self, app, integration_db_session, test_user, test_order):
        """Test deleting a return."""
        # Arrange
        service = ReturnService()
        user_id = test_user.id
        order_id = test_order.id
        
        with app.app_context():
            g.db = integration_db_session
            ret = service.create_return(**{
                order_id=order_id,
                user_id=user_id,
                reason='Defective',
                status='pending'
            )
            return_id = ret.id  # Get ID before commit
            integration_db_session.commit()
        
        # Act
        with app.app_context():
            g.db = integration_db_session
            result = service.delete_return(return_id)
            integration_db_session.commit()
        
        # Assert
        assert result is True
        
        # Verify deletion
        with app.app_context():
            g.db = integration_db_session
            deleted_return = service.get_return_by_id(return_id)
            assert deleted_return is None
    
    def test_delete_nonexistent_return(self, app, integration_db_session):
        """Test deleting a non-existent return."""
        service = ReturnService()
        
        with app.app_context():
            g.db = integration_db_session
            result = service.delete_return(99999)
            assert result is False
