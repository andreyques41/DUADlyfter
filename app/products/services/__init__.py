"""
Products services package - exports product-related schemas.
"""

from .product_service import ProdService

# This allows: from app.products.services import ProdService
# Instead of: from app.products.services.product_service import ProdService