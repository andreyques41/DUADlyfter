"""
Invoice (Bill) Models Module

Defines the ORM models for invoice/billing management.
Now using normalized table for invoice status.

Models:
- InvoiceStatus: Reference table for invoice status (normalized)
- Invoice: Billing information for orders

Features:
- SQLAlchemy ORM with normalized reference tables
- Foreign key relationships for data integrity
- Timestamp tracking for creation and due dates
- Configurable schema support

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- BillStatus enum replaced with InvoiceStatus reference table
- Model renamed from Bill to Invoice (matches SQL schema)
- Serialization handled by Marshmallow schemas
"""
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List
from datetime import datetime


class InvoiceStatus(Base):
    """Reference table for invoice status (normalized)."""
    __tablename__ = "invoice_status"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationship
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="status")
    
    def __repr__(self):
        return f"<InvoiceStatus(id={self.id}, name='{self.name}')>"


class Invoice(Base):
    """Invoice model for order billing."""
    __tablename__ = "invoices"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    order_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.orders.id"),
        unique=True,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.users.id"),
        nullable=False
    )
    invoice_status_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.invoice_status.id"),
        nullable=False
    )
    
    # Invoice details
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Optional fields
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    status: Mapped["InvoiceStatus"] = relationship(back_populates="invoices")
    order: Mapped["Order"] = relationship(back_populates="invoice")
    user: Mapped["User"] = relationship(back_populates="invoices")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, order_id={self.order_id}, total={self.total_amount}, status_id={self.invoice_status_id})>"
