"""
Products models package - exports product-related models and enums.
"""

from .product import Product
from app.core.enums import ProductCategory, PetType

# This allows: from app.products.models import Product, ProductCategory
# Instead of: from app.products.models.product import Product, ProductCategory