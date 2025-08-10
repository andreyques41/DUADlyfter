"""
Products schemas package - exports product-related schemas.
"""

from .product_schema import (
    product_registration_schema,
    product_response_schema,
    products_response_schema,
    ProductResponseSchema
)

# This allows: from app.products.schemas import product_registration_schema
# Instead of: from app.products.schemas.product_schema import product_registration_schema