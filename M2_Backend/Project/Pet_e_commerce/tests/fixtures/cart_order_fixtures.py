"""
Cart and Order Test Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides test data for Cart, CartItem, Order, OrderItem, Invoice, and Return models.

Fixtures:
- test_cart: Empty cart for test_user
- test_cart_with_items: Cart with products
- test_order_status_pending/confirmed/shipped/cancelled: Order statuses
- test_invoice_status_pending/paid/cancelled: Invoice statuses
- test_return_status_pending/approved/rejected: Return statuses
- test_order: Complete order
"""
import pytest
from app.sales.models.cart import Cart, CartItem
from app.sales.models.order import Order, OrderItem, OrderStatus
from app.sales.models.invoice import Invoice, InvoiceStatus
from app.sales.models.returns import Return, ReturnItem, ReturnStatus
from datetime import datetime


# ========================================
# Order Status Reference Data
# ========================================

@pytest.fixture(scope="session")
def test_order_status_pending(test_db_engine):
    """Create Pending order status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(status='Pending').first()
        if not status:
            status = OrderStatus(status='Pending')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_confirmed(test_db_engine):
    """Create Confirmed order status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(status='Confirmed').first()
        if not status:
            status = OrderStatus(status='Confirmed')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_shipped(test_db_engine):
    """Create Shipped order status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(status='Shipped').first()
        if not status:
            status = OrderStatus(status='Shipped')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_order_status_cancelled(test_db_engine):
    """Create Cancelled order status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(OrderStatus).filter_by(status='Cancelled').first()
        if not status:
            status = OrderStatus(status='Cancelled')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


# ========================================
# Invoice Status Reference Data
# ========================================

@pytest.fixture(scope="session")
def test_invoice_status_pending(test_db_engine):
    """Create Pending invoice status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(InvoiceStatus).filter_by(name='Pending').first()
        if not status:
            status = InvoiceStatus(name='Pending')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_invoice_status_paid(test_db_engine):
    """Create Paid invoice status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(InvoiceStatus).filter_by(name='Paid').first()
        if not status:
            status = InvoiceStatus(name='Paid')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_invoice_status_cancelled(test_db_engine):
    """Create Cancelled invoice status."""
    from sqlalchemy.orm import Session
    
    with Session(test_db_engine) as session:
        status = session.query(InvoiceStatus).filter_by(name='Cancelled').first()
        if not status:
            status = InvoiceStatus(name='Cancelled')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


# ========================================
# Return Status Reference Data
# ========================================

@pytest.fixture(scope="session")
def test_return_status_pending(test_db_engine):
    """Create Pending return status."""
    from sqlalchemy.orm import Session
    from app.sales.models.returns import ReturnStatus
    
    with Session(test_db_engine) as session:
        status = session.query(ReturnStatus).filter_by(status='Pending').first()
        if not status:
            status = ReturnStatus(status='Pending')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_return_status_approved(test_db_engine):
    """Create Approved return status."""
    from sqlalchemy.orm import Session
    from app.sales.models.returns import ReturnStatus
    
    with Session(test_db_engine) as session:
        status = session.query(ReturnStatus).filter_by(status='Approved').first()
        if not status:
            status = ReturnStatus(status='Approved')
            session.add(status)
            session.commit()
            session.refresh(status)
        return status


@pytest.fixture(scope="session")
def test_return_status_rejected(test_db_engine):
    """Create Rejected return status."""
    from sqlalchemy.orm import Session
    from app.sales.models.returns import ReturnStatus
    
    with Session(test_db_engine) as session:
        status = session.query(ReturnStatus).filter_by(status='Rejected').first()
        if not status:
            status = ReturnStatus(status='Rejected')
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
    - Total: 75.97 (calculated from items)
    """
    cart = Cart(
        user_id=test_user.id,
        finalized=False,
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
def test_order(db_session, test_user, test_cart_with_items, test_product, test_order_status_pending):
    """
    Create order for test_user with items from test_cart_with_items.
    
    Order:
        status: Pending
        total_amount: 75.97 (calculated from cart items)
        items: 2 products from cart
    """
    # Calculate total from cart items
    total = sum(item.amount * item.quantity for item in test_cart_with_items.items)
    
    order = Order(
        cart_id=test_cart_with_items.id,
        user_id=test_user.id,
        order_status_id=test_order_status_pending.id,
        total_amount=total,
        created_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.flush()
    
    # Create order items from cart items
    for cart_item in test_cart_with_items.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            amount=cart_item.amount,
            quantity=cart_item.quantity
        )
        db_session.add(order_item)
    
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
