"""
Products Domain Imports Module

Centralized imports for the products domain to reduce import complexity
and provide a single source for all product-related dependencies.

Usage:
    from app.products.imports import (
        Product, ProductService,
        product_registration_schema, product_response_schema,
        PRODUCTS_DB_PATH, ProductCategory, PetType
    )
"""

# Models
from app.products.models.product import Product

# Services
from app.products.services.product_service import ProdService

# Schemas
from app.products.schemas.product_schema import (
    ProductRegistrationSchema,
    ProductResponseSchema
)

# Create schema instances for easy use
product_registration_schema = ProductRegistrationSchema()
product_response_schema = ProductResponseSchema()
product_update_schema = ProductRegistrationSchema()  # Reuse registration schema for updates
products_response_schema = ProductResponseSchema(many=True)

# Database paths
from app.shared.json_db import PRODUCTS_DB_PATH

# Enums
from app.shared.enums import ProductCategory, PetType

# Shared utilities
from app.shared.utils.crud_utils import (
    save_models_to_json,
    load_models_from_json,
    load_single_model_by_field,
    generate_next_id
)

# Export all product-related items
__all__ = [
    # Models
    'Product',
    
    # Services
    'ProdService',
    
    # Schemas
    'ProductRegistrationSchema', 'ProductResponseSchema',
    'product_registration_schema', 'product_response_schema',
    'product_update_schema', 'products_response_schema',
    
    # Database
    'PRODUCTS_DB_PATH',
    
    # Enums
    'ProductCategory', 'PetType',
    
    # Utilities
    'save_models_to_json', 'load_models_from_json',
    'load_single_model_by_field', 'generate_next_id'
]
