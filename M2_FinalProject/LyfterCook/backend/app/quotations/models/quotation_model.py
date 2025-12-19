from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Quotation(Base):
    """
    Quotation model - Price quotes for chef services
    Schema: core
    """
    __tablename__ = 'quotations'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('core.clients.id', ondelete='SET NULL'), nullable=True, index=True)
    menu_id = Column(Integer, ForeignKey('core.menus.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Quotation details
    quotation_number = Column(String(50), unique=True, nullable=False, index=True)
    event_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)  # Matches DB column name
    valid_until = Column(Date, nullable=True)  # Quotation expiration date
    pdf_url = Column(String(500), nullable=True)  # URL to generated PDF
    
    # Status workflow
    status = Column(String(20), default='draft', nullable=False)  # 'draft', 'sent', 'accepted', 'rejected', 'expired'
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)

    # Relationships
    chef = relationship("Chef", backref="quotations")
    client = relationship("Client", backref="quotations")
    menu = relationship("Menu", backref="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan", order_by="QuotationItem.id")
    
    def __repr__(self):
        return f"<Quotation(id={self.id}, number='{self.quotation_number}', status='{self.status}')>"
    
    def to_dict(self, include_items=True):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'chef_id': self.chef_id,
            'client_id': self.client_id,
            'menu_id': self.menu_id,
            'quotation_number': self.quotation_number,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'total_amount': str(self.total_amount) if self.total_amount else '0.00',
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'pdf_url': self.pdf_url,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
        
        if include_items and self.items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
