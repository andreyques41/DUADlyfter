"""
Invoice Models Module

Defines the ORM models for invoice management.
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
- InvoiceStatus reference table for normalized status values
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
    
    def is_overdue(self) -> bool:
        """
        Check if invoice is overdue.
        
        Returns:
            True if invoice is past due date and not paid, False otherwise
        """
        if not self.due_date:
            return False
        
        # Get current time
        from datetime import datetime
        now = datetime.utcnow()
        
        # Invoice is overdue if due_date has passed and status is not 'paid'
        from app.core.reference_data import ReferenceData
        paid_status_id = ReferenceData.get_invoice_status_id('paid')
        
        return now > self.due_date and self.invoice_status_id != paid_status_id
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, order_id={self.order_id}, total={self.total_amount}, status_id={self.invoice_status_id})>"
