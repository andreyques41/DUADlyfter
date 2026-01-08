"""
Product Model Module

Defines the Product ORM models for the e-commerce pet store.
Now using normalized tables for categories and pet types.

Models:
- ProductCategory: Reference table for product categories (food, toys, etc.)
- PetType: Reference table for pet types (dog, cat, bird, etc.)
- Product: Main product catalog with relationships

Features:
- SQLAlchemy ORM with normalized reference tables
- Foreign key relationships for data integrity
- Stock management and availability tracking
- Admin-specific fields (cost, supplier info)
- Configurable schema support

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- Enums replaced with reference tables (normalized design)
- Serialization now handled by Marshmallow schemas
"""
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List
from datetime import datetime


class ProductCategory(Base):
    """Reference table for product categories (normalized)."""
    __tablename__ = "product_categories"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Relationship
    products: Mapped[List["Product"]] = relationship(back_populates="category")
    
    def __repr__(self):
        return f"<ProductCategory(id={self.id}, category='{self.category}')>"


class PetType(Base):
    """Reference table for pet types (normalized)."""
    __tablename__ = "pet_types"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Relationship
    products: Mapped[List["Product"]] = relationship(back_populates="pet_type")
    
    def __repr__(self):
        return f"<PetType(id={self.id}, type='{self.type}')>"


class Product(Base):
    """Product model for e-commerce pet store catalog."""
    __tablename__ = "products"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Product identification
    sku: Mapped[str] = mapped_column(CHAR(5), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Foreign keys (normalized)
    product_category_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.product_categories.id"), 
        nullable=False
    )
    pet_type_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.pet_types.id"), 
        nullable=False
    )
    
    # Inventory and pricing
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Optional fields
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=True)
    
    # Admin-only fields
    internal_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    supplier_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    category: Mapped["ProductCategory"] = relationship(back_populates="products")
    pet_type: Mapped["PetType"] = relationship(back_populates="products")
    
    # Relationships with sales models
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")
    return_items: Mapped[List["ReturnItem"]] = relationship(back_populates="product")
    
    def is_available(self) -> bool:
        """
        Check if product is available for purchase.
        
        Returns:
            bool: True if product is active and has stock, False otherwise
        """
        return self.is_active and self.stock_quantity > 0
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', description='{self.description}')>"
