from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Dish(Base):
    """
    Dish model - Chef's dish/recipe with ingredients
    Schema: core
    """
    __tablename__ = 'dishes'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)  # Optional pricing
    category = Column(String(50), nullable=True)  # e.g., "Appetizer", "Main Course", "Dessert"
    preparation_steps = Column(Text, nullable=True)
    prep_time = Column(Integer, nullable=True)  # Minutes
    servings = Column(Integer, nullable=True, default=1)
    photo_url = Column(String(500), nullable=True)  # Cloudinary URL
    is_active = Column(Boolean, default=True, nullable=False)  # Native BOOLEAN type (migrated from INTEGER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chef = relationship("Chef", backref="dishes")
    ingredients = relationship("Ingredient", back_populates="dish", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dish(id={self.id}, name='{self.name}', chef_id={self.chef_id})>"
    
    def to_dict(self, include_ingredients=True):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'chef_id': self.chef_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'category': self.category,
            'preparation_steps': self.preparation_steps,
            'prep_time': self.prep_time,
            'servings': self.servings,
            'photo_url': self.photo_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_ingredients and self.ingredients:
            data['ingredients'] = [ing.to_dict() for ing in self.ingredients]
        
        return data
