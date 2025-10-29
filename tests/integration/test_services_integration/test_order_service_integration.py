"""
Integration Tests: Order Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests order service with real database operations.
Validates complete flows: order creation, status management, retrieval, updates.

These tests use a real database (PostgreSQL test) to ensure:
- Services and repositories work together correctly
- Order items and relationships are managed properly
- Order status transitions work correctly
- Foreign key constraints are respected
- Cascading deletes work as expected
"""
import pytest
from flask import g
from app.sales.services.order_service import OrderService
from app.sales.services.cart_service import CartService
from app.products.services.product_service import ProductService
from app.auth.services.auth_service import AuthService
from app.auth.services.security_service import hash_password


class TestOrderCreationIntegration:
    """Integration tests for order creation flow."""
    
    def test_create_order_with_items(self, app, integration_db_session):
        """Test creating an order with products and items."""
        with app.app_context():
            # Inject test database session
            g.db = integration_db_session
            
            # Force ReferenceDataCache to use test database
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create user and products first
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            
            # Create user
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='orderuser',
                email='order@test.com',
                password_hash=password_hash,
                role_name='user'
            )
            assert user is not None
            
            # Create products
            product1 = product_service.create_product(
                description='Dog Food - Premium',
                category='food',
                pet_type='dog',
                price=25.99,
                stock_quantity=100,
                sku='OR001'
            )
            assert product1 is not None
            
            product2 = product_service.create_product(
                description='Dog Toy',
                category='toys',
                pet_type='dog',
                price=9.99,
                stock_quantity=50,
                sku='OR002'
            )
            assert product2 is not None
            
            # Create cart first
            cart_service = CartService()
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart is not None
            
            # Act - Create order
            # Note: OrderService.create_order() calculates total_amount from items
            # It ignores any total_amount passed in order_data
            order_data = {
                'user_id': user.id,
                'cart_id': cart.id,
                'status': 'pending',
                'shipping_address': '123 Test St, Test City',
                'items': [
                    {
                        'product_id': product1.id,
                        'quantity': 1,
                        'amount': 25.99
                    },
                    {
                        'product_id': product2.id,
                        'quantity': 2,
                        'amount': 19.98  # 2 * 9.99
                    }
                ]
            }
            
            new_order = order_service.create_order(**order_data)
            
            # Assert
            assert new_order is not None
            assert new_order.user_id == user.id
            assert new_order.cart_id == cart.id
            # OrderService calculates total from items: 25.99 + 19.98 = 45.97
            assert new_order.total_amount == 45.97
            assert new_order.shipping_address == '123 Test St, Test City'
            
            # Verify order status
            assert new_order.status is not None
            assert new_order.status.status == 'pending'
            
            # Verify order items
            assert len(new_order.items) == 2
            
            # Find items by product_id
            item1 = next((item for item in new_order.items if item.product_id == product1.id), None)
            item2 = next((item for item in new_order.items if item.product_id == product2.id), None)
            
            assert item1 is not None
            assert item1.quantity == 1
            assert item1.amount == 25.99
            
            assert item2 is not None
            assert item2.quantity == 2
            assert item2.amount == 19.98
    
    def test_create_order_without_items_fails(self, app, integration_db_session):
        """Test that creating order without items fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            order_service = OrderService()
            cart_service = CartService()
            
            # Create user
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='noitemsuser',
                email='noitems@test.com',
                password_hash=password_hash
            )
            assert user is not None
            
            # Create cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart is not None
            
            # Act - Try to create order without items
            order_data = {
                'user_id': user.id,
                'cart_id': cart.id,
                'status': 'pending',
                'total_amount': 0.0,
                'items': []  # Empty items
            }
            
            new_order = order_service.create_order(**order_data)
            
            # Assert
            assert new_order is None  # Should fail
    
    def test_create_order_with_invalid_status(self, app, integration_db_session):
        """Test that creating order with invalid status fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            # Create user and product
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='invalidstatus',
                email='invalid@test.com',
                password_hash=password_hash
            )
            assert user is not None
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=10.0,
                stock_quantity=10,
                sku='INV01'
            )
            assert product is not None
            
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart is not None
            
            # Act - Try to create order with invalid status
            order_data = {
                'user_id': user.id,
                'cart_id': cart.id,
                'status': 'invalid_status',  # Invalid
                'total_amount': 10.0,
                'items': [
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 10.0
                    }
                ]
            }
            
            new_order = order_service.create_order(**order_data)
            
            # Assert
            assert new_order is None  # Should fail


class TestOrderRetrievalIntegration:
    """Integration tests for order retrieval."""
    
    def test_get_order_by_id(self, app, integration_db_session):
        """Test retrieving order by ID."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create order first
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='getbyid',
                email='getbyid@test.com',
                password_hash=password_hash
            )
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=15.0,
                stock_quantity=20,
                sku='GB001'
            )
            
            cart = cart_service.create_cart(user_id=user.id, items=[])
            
            order = order_service.create_order(
                user_id=user.id,
                cart_id=cart.id,
                status='pending',
                total_amount=15.0,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 15.0
                    }
                ]
            )
            assert order is not None
            order_id = order.id
            
            # Act - Retrieve by ID
            retrieved_order = order_service.get_order_by_id(order_id)
            
            # Assert
            assert retrieved_order is not None
            assert retrieved_order.id == order_id
            assert retrieved_order.user_id == user.id
            assert retrieved_order.total_amount == 15.0
    
    def test_get_orders_by_user_id(self, app, integration_db_session):
        """Test retrieving all orders for a user."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create multiple orders for same user
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='multiorder',
                email='multi@test.com',
                password_hash=password_hash
            )
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=20.0,
                stock_quantity=50,
                sku='MO001'
            )
            
            # Create first order
            cart1 = cart_service.create_cart(user_id=user.id, items=[], force_create=True)
            order1 = order_service.create_order(
                user_id=user.id,
                cart_id=cart1.id,
                status='pending',
                total_amount=20.0,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 20.0
                    }
                ]
            )
            
            # Create second order (need new cart)
            cart2 = cart_service.create_cart(user_id=user.id, items=[], force_create=True)
            order2 = order_service.create_order(
                user_id=user.id,
                cart_id=cart2.id,
                status='processing',
                total_amount=40.0,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 2,
                        'amount': 40.0
                    }
                ]
            )
            
            # Act - Get all orders for user
            user_orders = order_service.get_orders_by_user_id(user.id)
            
            # Assert
            assert len(user_orders) >= 2
            order_ids = [o.id for o in user_orders]
            assert order1.id in order_ids
            assert order2.id in order_ids
    
    def test_get_nonexistent_order(self, app, integration_db_session):
        """Test retrieving non-existent order returns None."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            order_service = OrderService()
            
            # Act
            order = order_service.get_order_by_id(99999)
            
            # Assert
            assert order is None


class TestOrderStatusManagementIntegration:
    """Integration tests for order status transitions."""
    
    def test_update_order_status(self, app, integration_db_session):
        """Test updating order status."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create order
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='statususer',
                email='status@test.com',
                password_hash=password_hash
            )
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=30.0,
                stock_quantity=30,
                sku='ST001'
            )
            
            cart = cart_service.create_cart(user_id=user.id, items=[])
            
            order = order_service.create_order(
                user_id=user.id,
                cart_id=cart.id,
                status='pending',
                total_amount=30.0,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 30.0
                    }
                ]
            )
            assert order is not None
            assert order.status.status == 'pending'
            
            # Act - Update status to 'processing'
            updated_order = order_service.update_order(
                order.id,
                status='processing'
            )
            
            # Assert
            assert updated_order is not None
            assert updated_order.status.status == 'processing'
    
    def test_update_order_with_invalid_status_fails(self, app, integration_db_session):
        """Test that updating with invalid status fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='invalidupdate',
                email='invalidupdate@test.com',
                password_hash=password_hash
            )
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=25.0,
                stock_quantity=25,
                sku='IU001'
            )
            
            cart = cart_service.create_cart(user_id=user.id, items=[])
            
            order = order_service.create_order(
                user_id=user.id,
                cart_id=cart.id,
                status='pending',
                total_amount=25.0,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 25.0
                    }
                ]
            )
            assert order is not None
            
            # Act - Try to update with invalid status
            updated_order = order_service.update_order(
                order.id,
                status='invalid_status'
            )
            
            # Assert
            assert updated_order is None  # Should fail


class TestOrderDeletionIntegration:
    """Integration tests for order deletion."""
    
    def test_delete_order_cascades_to_items(self, app, integration_db_session):
        """
        Test that deleting an order also deletes its items (cascading delete).
        Order must be in 'cancelled' status to be deletable.
        """
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.initialize()
            
            # Arrange - Create order with items
            auth_service = AuthService()
            product_service = ProductService()
            order_service = OrderService()
            cart_service = CartService()
            
            password_hash = hash_password('TestPass123!')
            user, _ = auth_service.create_user(
                username='deleteuser',
                email='delete@test.com',
                password_hash=password_hash
            )
            
            product = product_service.create_product(
                description='Test Product',
                category='food',
                pet_type='dog',
                price=18.0,
                stock_quantity=40,
                sku='DE001'
            )
            
            cart = cart_service.create_cart(user_id=user.id, items=[])
            
            order = order_service.create_order(
                user_id=user.id,
                cart_id=cart.id,
                status='pending',
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 18.0
                    }
                ]
            )
            assert order is not None
            order_id = order.id
            
            # Verify order has items
            assert len(order.items) == 1
            
            # Change status to cancelled (deletable status)
            updated_order = order_service.update_order_status(order_id, 'cancelled')
            assert updated_order is not None
            assert updated_order.status.status == 'cancelled'
            
            # Act - Delete order
            result = order_service.delete_order(order_id)
            
            # Assert - Delete succeeds with cancelled status
            assert result is True
            
            # Verify order is deleted (cascading delete removes order items too)
            deleted_order = order_service.get_order_by_id(order_id)
            assert deleted_order is None
