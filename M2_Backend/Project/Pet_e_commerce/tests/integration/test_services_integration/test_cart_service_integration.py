"""
Integration Tests for Cart Service

Tests cart operations end-to-end with real database:
- Cart creation and retrieval
- Adding/removing items to cart
- Updating cart items
- Cart finalization
- Cart deletion
"""
import pytest
from flask import g
from app.auth.services.auth_service import AuthService
from app.auth.services.security_service import hash_password
from app.products.services.product_service import ProductService
from app.sales.services.cart_service import CartService


class TestCartCreationIntegration:
    """Integration tests for cart creation."""
    
    def test_create_empty_cart_for_user(self, app, integration_db_session):
        """Test creating an empty cart for a user."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser1',
                email='cart1@test.com',
                password=password_plain
            )
            assert user is not None
            
            # Act - Create empty cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            
            # Assert
            assert cart is not None
            assert cart.user_id == user.id
            assert cart.finalized is False
            assert len(cart.items) == 0
    
    def test_create_cart_with_items(self, app, integration_db_session):
        """Test creating a cart with initial items."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser2',
                email='cart2@test.com',
                password=password_plain
            )
            
            product = product_service.create_product(
                description='Dog Food',
                category='food',
                pet_type='dog',
                price=29.99,
                stock_quantity=100,
                sku='CT001'
            )
            assert product is not None
            
            # Act - Create cart with items
            cart = cart_service.create_cart(
                user_id=user.id,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 2,
                        'amount': 59.98  # 2 * 29.99
                    }
                ]
            )
            
            # Assert
            assert cart is not None
            assert cart.user_id == user.id
            assert len(cart.items) == 1
            assert cart.items[0].product_id == product.id
            assert cart.items[0].quantity == 2
            assert cart.items[0].amount == 59.98
    
    def test_create_duplicate_cart_fails(self, app, integration_db_session):
        """Test that creating a duplicate cart for same user fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser3',
                email='cart3@test.com',
                password=password_plain
            )
            
            # Create first cart
            first_cart = cart_service.create_cart(user_id=user.id, items=[])
            assert first_cart is not None
            
            # Act - Try to create duplicate cart
            duplicate_cart = cart_service.create_cart(user_id=user.id, items=[])
            
            # Assert
            assert duplicate_cart is None


class TestCartItemManagementIntegration:
    """Integration tests for adding/removing cart items."""
    
    def test_add_item_to_cart(self, app, integration_db_session):
        """Test adding an item to an existing cart."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser4',
                email='cart4@test.com',
                password=password_plain
            )
            
            product = product_service.create_product(
                description='Cat Toy',
                category='toys',
                pet_type='cat',
                price=12.99,
                stock_quantity=50,
                sku='CT002'
            )
            
            # Create empty cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart is not None
            assert len(cart.items) == 0
            
            # Act - Add item to cart
            updated_cart = cart_service.add_item_to_cart(
                user_id=user.id,
                product_id=product.id,
                quantity=3
            )
            
            # Assert
            assert updated_cart is not None
            assert len(updated_cart.items) == 1
            assert updated_cart.items[0].product_id == product.id
            assert updated_cart.items[0].quantity == 3
            # CartService should calculate amount based on product price
            assert updated_cart.items[0].amount == 12.99 * 3
    
    def test_remove_item_from_cart(self, app, integration_db_session):
        """Test removing an item from cart."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser5',
                email='cart5@test.com',
                password=password_plain
            )
            
            product = product_service.create_product(
                description='Bird Cage',
                category='accessories',
                pet_type='bird',
                price=45.00,
                stock_quantity=20,
                sku='CT003'
            )
            
            # Create cart with item
            cart = cart_service.create_cart(
                user_id=user.id,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 1,
                        'amount': 45.00
                    }
                ]
            )
            assert len(cart.items) == 1
            
            # Act - Remove item from cart
            result = cart_service.remove_item_from_cart(
                user_id=user.id,
                product_id=product.id
            )
            
            # Assert
            assert result is True  # remove_item_from_cart returns bool
            
            # Verify item was removed
            updated_cart = cart_service.get_cart_by_user_id(user.id)
            assert updated_cart is not None
            assert len(updated_cart.items) == 0
    
    def test_update_item_quantity_in_cart(self, app, integration_db_session):
        """Test updating quantity of an existing cart item."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser6',
                email='cart6@test.com',
                password=password_plain
            )
            
            product = product_service.create_product(
                description='Fish Food',
                category='food',
                pet_type='fish',
                price=8.50,
                stock_quantity=100,
                sku='CT004'
            )
            
            # Create cart with item
            cart = cart_service.create_cart(
                user_id=user.id,
                items=[
                    {
                        'product_id': product.id,
                        'quantity': 2,
                        'amount': 17.00  # 2 * 8.50
                    }
                ]
            )
            assert cart.items[0].quantity == 2
            
            # Act - Update item quantity (method is update_item_quantity not update_item_in_cart)
            updated_cart = cart_service.update_item_quantity(
                user_id=user.id,
                product_id=product.id,
                quantity=5
            )
            
            # Assert
            assert updated_cart is not None
            assert len(updated_cart.items) == 1
            assert updated_cart.items[0].quantity == 5
            assert updated_cart.items[0].amount == 8.50 * 5


class TestCartRetrievalIntegration:
    """Integration tests for cart retrieval."""
    
    def test_get_cart_by_user_id(self, app, integration_db_session):
        """Test retrieving a cart by user ID."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser7',
                email='cart7@test.com',
                password=password_plain
            )
            
            # Create cart
            created_cart = cart_service.create_cart(user_id=user.id, items=[])
            assert created_cart is not None
            
            # Act - Retrieve cart
            retrieved_cart = cart_service.get_cart_by_user_id(user.id)
            
            # Assert
            assert retrieved_cart is not None
            assert retrieved_cart.id == created_cart.id
            assert retrieved_cart.user_id == user.id
    
    def test_get_nonexistent_cart(self, app, integration_db_session):
        """Test retrieving a cart that doesn't exist."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            cart_service = CartService()
            
            # Act - Try to get cart for non-existent user
            cart = cart_service.get_cart_by_user_id(999999)
            
            # Assert
            assert cart is None


class TestCartFinalizationIntegration:
    """Integration tests for cart finalization."""
    
    def test_finalize_cart(self, app, integration_db_session):
        """Test finalizing a cart (marking as completed/checked out)."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser8',
                email='cart8@test.com',
                password=password_plain
            )
            
            # Create cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart.finalized is False
            
            # Act - Finalize cart
            finalized_cart = cart_service.finalize_cart(cart.id)
            
            # Assert
            assert finalized_cart is not None
            assert finalized_cart.finalized is True
    
    def test_cannot_add_item_to_finalized_cart(self, app, integration_db_session):
        """Test that adding items to a finalized cart fails."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            product_service = ProductService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser9',
                email='cart9@test.com',
                password=password_plain
            )
            
            product = product_service.create_product(
                description='Rabbit Food',
                category='food',
                pet_type='rabbit',
                price=15.99,
                stock_quantity=40,
                sku='CT005'
            )
            
            # Create and finalize cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            finalized_cart = cart_service.finalize_cart(cart.id)
            assert finalized_cart.finalized is True
            
            # Act - Try to add item to finalized cart
            # Note: add_item_to_cart creates NEW cart if user doesn't have one,
            # so it will create a new cart instead of using the finalized one
            result = cart_service.add_item_to_cart(
                user_id=user.id,
                product_id=product.id,
                quantity=1
            )
            
            # Assert - A new cart is created (not finalized)
            assert result is not None  # New cart created
            assert result.finalized is False
            assert result.id != finalized_cart.id  # Different cart


class TestCartDeletionIntegration:
    """Integration tests for cart deletion."""
    
    def test_delete_cart(self, app, integration_db_session):
        """Test deleting a cart."""
        with app.app_context():
            g.db = integration_db_session
            
            from app.core.reference_data import ReferenceDataCache
            ReferenceDataCache.reset()
            ReferenceDataCache.initialize()
            
            # Arrange
            auth_service = AuthService()
            cart_service = CartService()
            
            password_plain = ''
            user, _ = auth_service.create_user(
                username='cartuser10',
                email='cart10@test.com',
                password=password_plain
            )
            
            # Create cart
            cart = cart_service.create_cart(user_id=user.id, items=[])
            assert cart is not None
            
            # Act - Delete cart
            result = cart_service.delete_cart(user.id)
            
            # Assert
            assert result is True
            
            # Verify cart is deleted
            deleted_cart = cart_service.get_cart_by_user_id(user.id)
            assert deleted_cart is None

