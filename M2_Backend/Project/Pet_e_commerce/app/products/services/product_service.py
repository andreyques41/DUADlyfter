"""
Product Service Module

This module provides comprehensive product management functionality including:
- CRUD operations (Create, Read, Update, Delete)
- Advanced filtering and search capabilities
- Data persistence and validation
- Business logic for product management

Used by: Product routes for API operations
Dependencies: Product models, shared CRUD utilities
"""
import logging
from config.logging_config import EXC_INFO_LOG_ERRORS
from app.shared.utils import save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id
from app.products.models.product import Product
from app.shared.enums import ProductCategory, PetType

logger = logging.getLogger(__name__)

class ProdService:
    """
    Service class for product management operations.
    
    Handles all business logic for product CRUD operations, filtering,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./app/shared/json_db/products.json'):
        """Initialize product service with database path."""
        self.db_path = db_path
        self.logger = logger

    # ============ PRODUCT RETRIEVAL METHODS ============

    def get_products(self, product_id=None, request_args=None):
        """
        Unified method to get all products or a specific product by ID with optional filtering.
        
        Args:
            product_id (int, optional): If provided, returns single product
            request_args (ImmutableMultiDict, optional): Flask request.args for filtering
            
        Returns:
            list[Product] or Product or None: Filtered products, single product, or None if not found
            
        Note:
            - Single product queries bypass filtering for performance
            - Filtering only applies to "get all products" requests
            - Supports admin filters (stock levels, status) when applicable
        """
        if product_id:
            return load_single_model_by_field(self.db_path, Product, 'id', product_id)
            
        products = load_models_from_json(self.db_path, Product)

        if request_args:
            # Extract and process filters internally
            raw_filters = _extract_filters_from_request(request_args)
            processed_filters = _process_filters(raw_filters)
            if processed_filters:  # Only apply if there are valid filters
                return _apply_filters(products, processed_filters)
        return products

    # ============ PRODUCT CRUD OPERATIONS ============

    def create_product(self, product_instance):
        """
        Create a new product with Product instance from schema.
        
        Args:
            product_instance (Product): Product instance from schema with @post_load
            
        Returns:
            tuple: (Product, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and handles data persistence
        """
        try:
            # Load existing products to generate next ID
            existing_products = load_models_from_json(self.db_path, Product)
            
            # Set the ID for the new product instance
            product_instance.id = generate_next_id(existing_products)
        
            # Save product to database
            existing_products.append(product_instance)
            save_models_to_json(existing_products, self.db_path)
            
            self.logger.info(f"Product created successfully: {product_instance.name}")
            return product_instance, None
            
        except Exception as e:
            error_msg = f"Error creating product: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    def update_product(self, product_id, product_instance):
        """
        Update an existing product with Product instance from schema.
        
        Args:
            product_id (int): ID of product to update
            product_instance (Product): Updated product instance from schema
            
        Returns:
            tuple: (Product, None) on success, (None, error_message) on failure
            
        Note:
            Updates the entire product with new instance data
        """
        try:
            existing_product = load_single_model_by_field(self.db_path, Product, 'id', product_id)
            if not existing_product:
                return None, "Product not found"
            
            # Set the correct ID on the product instance (preserve existing ID)
            product_instance.id = product_id
            
            # Load all products, replace the specific one, and save
            all_products = load_models_from_json(self.db_path, Product)
            for i, p in enumerate(all_products):
                if p.id == product_id:
                    all_products[i] = product_instance
                    break
            
            save_models_to_json(all_products, self.db_path)
            
            self.logger.info(f"Product updated: {product_instance.name}")
            return product_instance, None
            
        except Exception as e:
            error_msg = f"Error updating product: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg
    
    def delete_product(self, product_id):
        """
        Delete a product by ID.
        
        Args:
            product_id (int): ID of product to delete
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
            
        Note:
            Permanently removes product from database
        """
        try:
            product = load_single_model_by_field(self.db_path, Product, 'id', product_id)
            if not product:
                return False, "Product not found"
            
            # Remove product from database
            all_products = load_models_from_json(self.db_path, Product)
            all_products = [p for p in all_products if p.id != product_id]
            save_models_to_json(all_products, self.db_path)
            
            self.logger.info(f"Product deleted: {product.name}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting product: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return False, error_msg

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)
        
# ============ MODULE-LEVEL FILTERING FUNCTIONS ============

"""
Product Filtering System

These functions handle the complex filtering logic for product searches.
Supports various filter types including price ranges, categories, text search,
and admin-specific filters like stock levels.

Architecture:
1. _extract_filters_from_request: Extracts raw filter parameters from Flask request
2. _process_filters: Validates and converts filter values to proper types
3. _apply_filters: Applies validated filters to product collection
4. _matches_search: Performs text-based search matching
"""

def _extract_filters_from_request(request_args):
    """Extract supported filter parameters from Flask request.args
    
    Args:
        request_args: Flask request.args (ImmutableMultiDict)
        
    Returns:
        dict: Raw filter parameters that need processing
    """
    return {
        'category': request_args.get('category'),
        'pet_type': request_args.get('pet_type'),
        'min_price': request_args.get('min_price'),
        'max_price': request_args.get('max_price'),
        'brand': request_args.get('brand'),
        'min_weight': request_args.get('min_weight'),
        'max_weight': request_args.get('max_weight'),
        'available_only': request_args.get('available_only'),
        'search': request_args.get('search'),  # Text search
        # Admin filters
        'is_active': request_args.get('is_active'),
        'low_stock': request_args.get('low_stock'),  # Products with low inventory
    }

def _process_filters(raw_filters):
    """Clean and validate filter parameters with type conversion."""
    processed = {}    

    for key, value in raw_filters.items():
        if value is None:
            continue

        # Type conversion and validation
        if key in ['min_price', 'max_price', 'min_weight', 'max_weight']:
            try:
                processed[key] = float(value)
            except ValueError:
                continue    # Skip invalid numeric values

        elif key in ['available_only', 'is_active', 'low_stock']:
            processed[key] = value.lower() in ['true', '1', 'yes']

        elif key == 'category':
            # Validate against ProductCategory enum
            try:
                ProductCategory(value.lower())
                processed[key] = value.lower()
            except ValueError:
                    continue  # Skip invalid category
            
        elif key == 'pet_type':
            # Validate against PetType enum
            try:
                PetType(value.lower())
                processed[key] = value.lower()
            except ValueError:
                continue  # Skip invalid pet type
            
        else:
            # String filters (brand, search)
            processed[key] = value.strip()
    
    return processed

def _apply_filters(products, filters):
    """Apply validated filters to product list."""
    filtered_products = products

    for filter_key, filter_value in filters.items():
        if filter_key == 'category':
            filtered_products = [p for p in filtered_products if p.category.value == filter_value]
        elif filter_key == 'pet_type':
            filtered_products = [p for p in filtered_products if p.pet_type.value == filter_value]
        elif filter_key == 'min_price':
            filtered_products = [p for p in filtered_products if p.price >= filter_value]
        elif filter_key == 'max_price':
            filtered_products = [p for p in filtered_products if p.price <= filter_value]
        elif filter_key == 'min_weight':
            filtered_products = [p for p in filtered_products if p.weight and p.weight >= filter_value]
        elif filter_key == 'max_weight':
            filtered_products = [p for p in filtered_products if p.weight and p.weight <= filter_value]
        elif filter_key == 'available_only' and filter_value:
            filtered_products = [p for p in filtered_products if p.is_available()]
        elif filter_key == 'is_active':
            filtered_products = [p for p in filtered_products if p.is_active == filter_value]
        elif filter_key == 'low_stock' and filter_value:
            filtered_products = [p for p in filtered_products if p.stock_quantity <= 10]
        elif filter_key == 'brand' and filter_value:
            filtered_products = [p for p in filtered_products if p.brand and filter_value.lower() in p.brand.lower()]
        elif filter_key == 'search' and filter_value:
            filtered_products = [p for p in filtered_products if _matches_search(p, filter_value)]

    return filtered_products

def _matches_search(product, search_term):
    """Check if product matches text search term."""
    search_term = search_term.lower()
    searchable_text = f"{product.name} {product.description} {product.brand or ''}".lower()
    return search_term in searchable_text