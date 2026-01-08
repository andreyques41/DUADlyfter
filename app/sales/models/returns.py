"""
Return Models Module

Defines the ORM models for return/refund management.
Now using normalized table for return status and join table for items.

Models:
- ReturnStatus: Reference table for return status (normalized)
- ReturnItem: Join table for return-product relationship
- Return: Product return request with relationships

Features:
- SQLAlchemy ORM with normalized reference tables
- Foreign key relationships for data integrity
- Cascading deletes for return items
- Timestamp tracking for creation
- Configurable schema support

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- ReturnStatus enum replaced with reference table
- ReturnItem now a proper join table
- Serialization handled by Marshmallow schemas
"""
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List
from datetime import datetime


class ReturnStatus(Base):
    """Reference table for return status (normalized)."""
    __tablename__ = "return_status"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relationship
    returns: Mapped[List["Return"]] = relationship(back_populates="status")
    
    def __repr__(self):
        return f"<ReturnStatus(id={self.id}, status='{self.status}')>"


class ReturnItem(Base):
    """Join table for return-product relationship."""
    __tablename__ = "return_item"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.products.id"),
        nullable=False
    )
    return_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.returns.id"),
        nullable=False
    )
    
    # Item details
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # Refund amount for this item
    
    # Relationships
    return_request: Mapped["Return"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="return_items")
    
    def __repr__(self):
        return f"<ReturnItem(id={self.id}, return_id={self.return_id}, product_id={self.product_id})>"


class Return(Base):
    """Return model for product returns and refunds."""
    __tablename__ = "returns"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    order_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.orders.id"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.users.id"),
        nullable=False
    )
    return_status_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.return_status.id"),
        nullable=False
    )
    
    # Return details
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)  # Total refund amount
    
    # Optional fields
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    status: Mapped["ReturnStatus"] = relationship(back_populates="returns")
    order: Mapped["Order"] = relationship(back_populates="returns")
    user: Mapped["User"] = relationship(back_populates="returns")
    items: Mapped[List["ReturnItem"]] = relationship(
        back_populates="return_request",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Return(id={self.id}, order_id={self.order_id}, total={self.total_amount}, status_id={self.return_status_id})>"
