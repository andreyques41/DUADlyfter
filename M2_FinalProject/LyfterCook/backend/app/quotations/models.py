"""
Quotation Models
Quotation and quotation items management.
"""

from datetime import timedelta
from app.core.lib.time_utils import utcnow_naive
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class QuotationStatus(enum.Enum):
    """Quotation status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Quotation(Base):
    """
    Quotation model for chef quotes to clients.
    
    Attributes:
        id: Primary key
        chef_id: Foreign key to Chef
        client_id: Foreign key to Client
        menu_id: Foreign key to Menu (optional)
        quotation_number: Unique quotation identifier
        total_amount: Total quotation amount
        status: Quotation status
        valid_until: Quotation validity date
        notes: Additional notes
        pdf_url: Generated PDF URL
        created_at, sent_at, updated_at: Timestamps
    """
    __tablename__ = 'quotations'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False)
    client_id = Column(Integer, ForeignKey('core.clients.id', ondelete='SET NULL'), nullable=True)
    menu_id = Column(Integer, ForeignKey('core.menus.id', ondelete='SET NULL'), nullable=True)
    
    quotation_number = Column(String(50), unique=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(SQLEnum(QuotationStatus), nullable=False, default=QuotationStatus.DRAFT)
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    sent_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    chef = relationship("Chef", backref="quotations")
    client = relationship("Client", backref="quotations")
    menu = relationship("Menu", backref="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quotation {self.quotation_number}>"
    
    def to_dict(self, include_items=False):
        """Convert quotation to dictionary."""
        data = {
            'id': self.id,
            'chef_id': self.chef_id,
            'client_id': self.client_id,
            'menu_id': self.menu_id,
            'quotation_number': self.quotation_number,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'status': self.status.value,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'notes': self.notes,
            'pdf_url': self.pdf_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data


class QuotationItem(Base):
    """
    Quotation item model for additional items/services.
    
    Attributes:
        id: Primary key
        quotation_id: Foreign key to Quotation
        description: Item description
        quantity: Item quantity
        unit_price: Price per unit
        subtotal: Quantity * unit_price
    """
    __tablename__ = 'quotation_items'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    quotation_id = Column(Integer, ForeignKey('core.quotations.id', ondelete='CASCADE'), nullable=False)
    
    description = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    quotation = relationship("Quotation", back_populates="items")
    
    def __repr__(self):
        return f"<QuotationItem {self.description}>"
    
    def to_dict(self):
        """Convert quotation item to dictionary."""
        return {
            'id': self.id,
            'quotation_id': self.quotation_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0
        }
