from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Ingredient(Base):
    """
    Ingredient model - Ingredients for a dish
    Schema: core
    """
    __tablename__ = 'ingredients'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey('core.dishes.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)  # DB uses VARCHAR - stores like "2.5", "1/2 cup", etc
    unit = Column(String(50), nullable=True)  # e.g., "kg", "lbs", "cups", "tablespoons" (standardized to 50)
    is_optional = Column(Boolean, default=False, nullable=False)  # Native BOOLEAN type (migrated from INTEGER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    dish = relationship("Dish", back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}', dish_id={self.dish_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'name': self.name,
            'quantity': float(self.quantity) if self.quantity else None,
            'unit': self.unit,
            'is_optional': self.is_optional,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
