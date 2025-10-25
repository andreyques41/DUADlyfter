"""
Cart and Order Test Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides test data for Cart, CartItem, Order, OrderItem models.

Fixtures:
- test_cart: Empty cart for test_user
- test_cart_with_items: Cart with products
- test_order_status_pending: Pending status
- test_order: Complete order
"""
import pytest
from app.sales.models.cart import Cart, CartItem
from app.sales.models.order import Order, OrderItem, OrderStatus
from datetime import datetime


# ========================================
# Order Status Reference Data
# ========================================

@pytest.fixture(scope="session")
def test_order_status_pending(test_db_engine):
    """Create Pending order status (id=1)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(id=1).first()
        if not status:
            status = OrderStatus(id=1, status='pending')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_confirmed(test_db_engine):
    """Create Confirmed order status (id=2)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(id=2).first()
        if not status:
            status = OrderStatus(id=2, status='confirmed')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_shipped(test_db_engine):
    """Create Shipped order status (id=3)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(id=3).first()
        if not status:
            status = OrderStatus(id=3, status='shipped')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_cancelled(test_db_engine):
    """Create Cancelled order status (id=4)."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(id=4).first()
        if not status:
            status = OrderStatus(id=4, status='cancelled')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


# ========================================
# Cart Fixtures
# ========================================

@pytest.fixture
def test_cart(db_session, test_user):
    """
    Create empty cart for test_user.
    
    Scope: function (auto-deleted via rollback)
    """
    cart = Cart(
        user_id=test_user.id,
        finalized=False,
        total_amount=0.0,
        created_at=datetime.utcnow()
    )
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    return cart


@pytest.fixture
def test_cart_with_items(db_session, test_user, test_product, test_product_cat_toy):
    """
    Create cart with 2 products for test_user.
    
    Cart contains:
    - Product 1 (Dog Food): qty=2, price=29.99
    - Product 2 (Cat Toy): qty=1, price=15.99
    - Total: 75.97
    """
    cart = Cart(
        user_id=test_user.id,
        finalized=False,
        total_amount=75.97,
        created_at=datetime.utcnow()
    )
    db_session.add(cart)
    db_session.flush()  # Get cart.id
    
    # Add cart items
    item1 = CartItem(
        cart_id=cart.id,
        product_id=test_product.id,
        amount=test_product.price,
        quantity=2
    )
    item2 = CartItem(
        cart_id=cart.id,
        product_id=test_product_cat_toy.id,
        amount=test_product_cat_toy.price,
        quantity=1
    )
    
    db_session.add_all([item1, item2])
    db_session.commit()
    db_session.refresh(cart)
    
    return cart


@pytest.fixture
def test_finalized_cart(db_session, test_user, test_product):
    """
    Create finalized cart (after checkout).
    """
    cart = Cart(
        user_id=test_user.id,
        finalized=True,
        total_amount=29.99,
        created_at=datetime.utcnow()
    )
    db_session.add(cart)
    db_session.flush()
    
    item = CartItem(
        cart_id=cart.id,
        product_id=test_product.id,
        amount=test_product.price,
        quantity=1
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(cart)
    
    return cart


# ========================================
# Order Fixtures
# ========================================

@pytest.fixture
def test_order(db_session, test_user, test_product, test_order_status_pending):
    """
    Create order for test_user with 1 product.
    
    Order:
        status: pending
        total_amount: 59.98 (2 x 29.99)
        items: 1 product, qty=2
    """
    order = Order(
        user_id=test_user.id,
        order_status_id=1,  # pending
        total_amount=59.98,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.flush()
    
    # Add order item
    item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        amount=test_product.price,
        quantity=2
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(order)
    
    return order


@pytest.fixture
def test_order_with_multiple_items(db_session, test_user, multiple_products, test_order_status_confirmed):
    """
    Create order with multiple products (confirmed status).
    
    Order:
        status: confirmed
        items: 3 products with varied quantities
    """
    # Use first 3 products
    products = multiple_products[:3]
    
    total = sum(p.price * 2 for p in products)  # qty=2 for each
    
    order = Order(
        user_id=test_user.id,
        order_status_id=2,  # confirmed
        total_amount=total,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.flush()
    
    # Add order items
    for product in products:
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            amount=product.price,
            quantity=2
        )
        db_session.add(item)
    
    db_session.commit()
    db_session.refresh(order)
    
    return order


@pytest.fixture
def test_cancelled_order(db_session, test_user, test_product, test_order_status_cancelled):
    """
    Create cancelled order.
    """
    order = Order(
        user_id=test_user.id,
        order_status_id=4,  # cancelled
        total_amount=29.99,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.flush()
    
    item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        amount=test_product.price,
        quantity=1
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(order)
    
    return order
