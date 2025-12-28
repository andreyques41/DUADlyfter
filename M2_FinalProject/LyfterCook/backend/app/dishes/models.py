"""
Dish and Ingredient Models
Dish catalog with ingredients for chefs.
"""

from app.core.lib.time_utils import utcnow_naive
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dish(Base):
    """
    Dish model for chef's menu items.
    
    Attributes:
        id: Primary key
        chef_id: Foreign key to Chef
        name: Dish name
        description: Dish description
        price: Base price
        category: Dish category (appetizer, main, dessert, etc.)
        preparation_steps: Cooking instructions
        prep_time: Preparation time in minutes
        servings: Number of servings
        photo_url: Cloudinary URL for dish photo
        is_active: Dish availability status
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'dishes'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=True)
    preparation_steps = Column(Text, nullable=True)
    prep_time = Column(Integer, nullable=True)  # in minutes
    servings = Column(Integer, nullable=True, default=1)
    photo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)  # Native BOOLEAN type
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    chef = relationship("Chef", backref="dishes")
    ingredients = relationship("Ingredient", back_populates="dish", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dish {self.name} - Chef {self.chef_id}>"
    
    def to_dict(self, include_ingredients=False):
        """Convert dish to dictionary."""
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
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_ingredients:
            data['ingredients'] = [ing.to_dict() for ing in self.ingredients]
        
        return data


class Ingredient(Base):
    """
    Ingredient model for dishes.
    
    Attributes:
        id: Primary key
        dish_id: Foreign key to Dish
        name: Ingredient name
        quantity: Amount needed
        unit: Unit of measurement (cups, grams, etc.)
        is_optional: Whether ingredient is optional
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'ingredients'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey('core.dishes.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)
    unit = Column(String(20), nullable=True)
    is_optional = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    dish = relationship("Dish", back_populates="ingredients")
    
    def __repr__(self):
        return f"<Ingredient {self.name} - Dish {self.dish_id}>"
    
    def to_dict(self):
        """Convert ingredient to dictionary."""
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'is_optional': bool(self.is_optional),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
