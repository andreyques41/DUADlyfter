from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuotationItem(Base):
    """
    QuotationItem model - Line items in a quotation
    Can reference a dish or be a custom item
    Schema: core
    """
    __tablename__ = 'quotation_items'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    quotation_id = Column(Integer, ForeignKey('core.quotations.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Item details (simplified - no dish reference in DB)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0.00)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00)

    # Relationships
    quotation = relationship("Quotation", back_populates="items")
    
    def __repr__(self):
        return f"<QuotationItem(id={self.id}, quotation_id={self.quotation_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'quotation_id': self.quotation_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': str(self.unit_price) if self.unit_price else '0.00',
            'subtotal': str(self.subtotal) if self.subtotal else '0.00'
        }
