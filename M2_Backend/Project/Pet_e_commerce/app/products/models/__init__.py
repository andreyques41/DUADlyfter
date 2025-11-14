"""
Products models package - exports product-related models.
"""

from .product import Product, ProductCategory, PetType

# This allows: from app.products.models import Product, ProductCategory, PetType
# Instead of: from app.products.models.product import Product, ProductCategory, PetType