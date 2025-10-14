"""
Cart Models Module

Defines the ORM models for shopping cart management.
Now using normalized join table for cart-product relationships.

Models:
- CartItem: Join table for cart-product many-to-many relationship
- Cart: Shopping cart with relationships to user and items

Features:
- SQLAlchemy ORM with join table pattern
- Foreign key relationships for data integrity
- Unique constraint on (product_id, cart_id)
- Cascading deletes for cart items
- Finalized flag to prevent modifications after checkout
- Configurable schema support

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- CartItem now a proper join table with its own ID
- Serialization handled by Marshmallow schemas
"""
from sqlalchemy import Integer, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List
from datetime import datetime


class CartItem(Base):
    """Join table for cart-product relationship with quantity and pricing."""
    __tablename__ = "cart_item"
    
    @declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint('product_id', 'cart_id', name='uq_product_cart'),
            {'schema': get_schema()}
        )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.products.id"),
        nullable=False
    )
    cart_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.carts.id"),
        nullable=False
    )
    
    # Item details
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Unit price
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    cart: Mapped["Cart"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, qty={self.quantity})>"


class Cart(Base):
    """Shopping cart model for user purchases."""
    __tablename__ = "carts"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key (one cart per user)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.users.id"),
        unique=True,
        nullable=False
    )
    
    # Cart status
    finalized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Optional fields
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="carts")
    items: Mapped[List["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan"
    )
    order: Mapped[Optional["Order"]] = relationship(back_populates="cart", uselist=False)
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, finalized={self.finalized})>"
