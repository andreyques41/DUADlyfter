"""
Order Models Module

Defines the ORM models for order management in the e-commerce system.
Now using normalized tables for order status and item relationships.

Models:
- OrderStatus: Reference table for order workflow states (normalized)
- OrderItem: Join table for order-product many-to-many relationship
- Order: Complete order with relationships and metadata

Features:
- SQLAlchemy ORM with normalized reference tables
- Foreign key relationships for data integrity
- Automatic timestamp tracking
- Cascading deletes for order items
- Configurable schema support

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- OrderStatus enum replaced with reference table
- OrderItem now a proper join table with columns
- Serialization handled by Marshmallow schemas
"""
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List
from datetime import datetime


class OrderStatus(Base):
    """Reference table for order status (normalized)."""
    __tablename__ = "order_status"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relationship
    orders: Mapped[List["Order"]] = relationship(back_populates="status")
    
    def __repr__(self):
        return f"<OrderStatus(id={self.id}, status='{self.status}')>"


class OrderItem(Base):
    """Join table for order-product relationship with quantity and pricing."""
    __tablename__ = "order_item"
    
    @declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint('product_id', 'order_id', name='uq_product_order'),
            {'schema': get_schema()}
        )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.products.id"),
        nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.orders.id"),
        nullable=False
    )
    
    # Item details
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Unit price at time of order
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"


class Order(Base):
    """Order model for customer purchases."""
    __tablename__ = "orders"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    cart_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.carts.id"),
        unique=True,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.users.id"),
        nullable=False
    )
    order_status_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.order_status.id"),
        nullable=False
    )
    
    # Order details
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Optional fields
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    shipping_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    status: Mapped["OrderStatus"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")
    cart: Mapped["Cart"] = relationship(back_populates="order")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )
    invoice: Mapped[Optional["Invoice"]] = relationship(back_populates="order", uselist=False)
    returns: Mapped[List["Return"]] = relationship(back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount}, status_id={self.order_status_id})>"
