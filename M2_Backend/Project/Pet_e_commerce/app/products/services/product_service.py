"""
Product Service Module

Business logic layer for product management with proper handling of normalized reference tables.

Key Changes:
1. Converts category/pet_type names → IDs before database operations
2. Validates reference data exists
3. Handles both creation and updates with proper conversions
4. Integrates Redis caching for improved performance

Responsibilities:
- Product CRUD operations with validation
- Advanced filtering and search
- Business logic and validation rules
- Orchestrates repository operations
- Cache management for frequently accessed data

Dependencies:
- ProductRepository: Database operations
- ReferenceData: Name ↔ ID conversions for reference tables
- CacheManager: Redis caching for performance optimization

Usage:
    service = ProductService()
    product = service.get_product_by_id(1)
    products = service.get_products_by_filters({'category': 'food'})
"""
import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.products.repositories import ProductRepository
from app.products.models.product import Product
from app.core.reference_data import ReferenceData
from app.core.cache_manager import get_cache
from app.core.middleware.cache_decorators import cache_invalidate, CacheHelper

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product management business logic with caching support."""
    
    def __init__(self):
        self.product_repo = ProductRepository()
        self.logger = logger
        # Get global cache manager instance (singleton pattern)
        self.cache_manager = get_cache()
        # Initialize cache helper for reusable schema-based caching
        self.cache_helper = CacheHelper(resource_name="product", version="v1")
    
    # ============ CACHE KEY GENERATION METHODS ============
    
    def _get_product_cache_key(self, *args, **kwargs):
        """Generate cache key for a single product by ID."""
        product_id = args[0] if args else kwargs.get('product_id')
        return f"product:{product_id}"
    
    def _get_all_products_cache_key(self, *args, **kwargs):
        """Generate cache key for all products."""
        return "products:all"
    
    def _get_filters_cache_key(self, *args, **kwargs):
        """Generate cache key for filtered products."""
        filters = args[0] if args else kwargs.get('filters', {})
        # Sort filters for consistent cache keys
        filter_str = json.dumps(filters, sort_keys=True)
        return f"products:filters:{filter_str}"
    
    def _get_sku_cache_key(self, *args, **kwargs):
        """Generate cache key for product by SKU."""
        sku = args[0] if args else kwargs.get('sku')
        return f"product:sku:{sku}"

    # ============ PRODUCT RETRIEVAL METHODS ============
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Get a product by ID (returns ORM object).
        Note: Caching is bypassed - use get_product_by_id_cached() for cached access.
        
        Args:
            product_id: Product ID to fetch
        
        Returns:
            Product object or None if not found
        """
        self.logger.debug(f"Fetching product with id {product_id}")
        return self.product_repo.get_by_id(product_id)
    
    def get_product_by_id_cached(self, product_id: int, 
                                   include_admin_data: bool = False,
                                   show_exact_stock: bool = False) -> Optional[dict]:
        """
        Get product by ID with schema-based caching (RECOMMENDED).
        Returns serialized dict ready for JSON response.
        
        Args:
            product_id: Product ID to fetch
            include_admin_data: Include admin-only fields
            show_exact_stock: Show exact stock quantity
        
        Returns:
            Serialized product dict or None if not found
        """
        from app.products.schemas.product_schema import ProductResponseSchema
        
        return self.cache_helper.get_or_set(
            cache_key=f"{product_id}:admin={include_admin_data}",
            fetch_func=lambda: self.product_repo.get_by_id(product_id),
            schema_class=ProductResponseSchema,
            schema_kwargs={
                'include_admin_data': include_admin_data,
                'show_exact_stock': show_exact_stock
            },
            ttl=300  # 5 minutes
        )
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get a product by SKU (returns ORM object).
        Note: Caching is bypassed - consider adding schema-cached version if needed.
        
        Args:
            sku: Product SKU to search for
            
        Returns:
            Product object or None if not found
        """
        self.logger.debug(f"Fetching product with SKU {sku}")
        return self.product_repo.get_by_sku(sku)
    
    def get_all_products(self) -> List[Product]:
        """
        Get all products (returns ORM objects).
        Note: Caching is bypassed - use get_all_products_cached() for cached access.
        
        Returns:
            List of all products
        """
        self.logger.debug("Fetching all products")
        return self.product_repo.get_all()
    
    def get_all_products_cached(self, include_admin_data: bool = False,
                                 show_exact_stock: bool = False) -> List[dict]:
        """
        Get all products with schema-based caching (RECOMMENDED).
        Returns list of serialized dicts ready for JSON response.
        
        Args:
            include_admin_data: Include admin-only fields
            show_exact_stock: Show exact stock quantities
        
        Returns:
            List of serialized product dicts
        """
        from app.products.schemas.product_schema import ProductResponseSchema
        
        return self.cache_helper.get_or_set(
            cache_key=f"all:admin={include_admin_data}",
            fetch_func=lambda: self.product_repo.get_all(),
            schema_class=ProductResponseSchema,
            schema_kwargs={
                'include_admin_data': include_admin_data,
                'show_exact_stock': show_exact_stock
            },
            ttl=180,  # 3 minutes (shorter for lists)
            many=True
        )
    
    def get_products_by_filters(self, filters: Dict[str, Any]) -> List[Product]:
        """
        Get products with filters applied.
        Converts filter names (category, pet_type) to IDs if needed.
        Note: Filtering is not cached due to dynamic nature of filters.
        
        Args:
            filters: Dictionary with filter criteria
                Can include 'category' and 'pet_type' as strings
                These will be converted to 'category_id' and 'pet_type_id'
                - brand: str
                - min_stock: int
                - is_active: bool
                - search: str
            
        Returns:
            List of filtered products
        """
        self.logger.debug(f"Fetching products with filters: {filters}")
        
        # Convert category name to ID if present
        if 'category' in filters:
            category_name = filters.pop('category')
            category_id = ReferenceData.get_product_category_id(category_name)
            if category_id:
                filters['category_id'] = category_id  # Changed from 'product_category_id'
            else:
                self.logger.warning(f"Invalid category filter: {category_name}")
                return []  # Return empty if invalid category
        
        # Convert pet_type name to ID if present
        if 'pet_type' in filters:
            pet_type_name = filters.pop('pet_type')
            pet_type_id = ReferenceData.get_pet_type_id(pet_type_name)
            if pet_type_id:
                filters['pet_type_id'] = pet_type_id  # This one is correct
            else:
                self.logger.warning(f"Invalid pet_type filter: {pet_type_name}")
                return []  # Return empty if invalid pet type
        
        return self.product_repo.get_by_filters(filters)

    # ============ PRODUCT VALIDATION METHODS ============
    
    def check_sku_exists(self, sku: str) -> bool:
        """Check if SKU already exists."""
        return self.product_repo.exists_by_sku(sku)

    # ============ PRODUCT CRUD OPERATIONS ============
    
    @cache_invalidate([
        lambda self, **kwargs: "product:v1:all:admin=True",
        lambda self, **kwargs: "product:v1:all:admin=False",
    ])
    def create_product(self, **product_data) -> Optional[Product]:
        """
        Create a new product with cache invalidation.
        Converts category and pet_type names to IDs before database insert.
        Invalidates all product list caches after successful creation.
        
        Args:
            **product_data: Product fields including:
                - name (required): Product name
                - description (required): Product description
                - category (required): Category name (e.g., "food", "toys")
                - pet_type (required): Pet type name (e.g., "dog", "cat")
                - price (required): Product price
                - stock_quantity (required): Initial stock quantity
                - brand (optional): Brand name
                - weight (optional): Product weight
                - is_active (optional): Product active status (default: True)
                - internal_cost (optional): Internal cost (admin only)
                - supplier_info (optional): Supplier information (admin only)
                - created_by (optional): Username of creator
            
        Returns:
            Created Product object or None on error
        """
        try:
            # === CONVERT REFERENCE DATA NAMES TO IDS ===
            
            # Convert category name to ID
            if 'category' in product_data:
                category_name = product_data.pop('category')
                category_id = ReferenceData.get_product_category_id(category_name)
                
                if category_id is None:
                    self.logger.error(f"Invalid category: {category_name}")
                    return None
                
                product_data['product_category_id'] = category_id
                self.logger.debug(f"Converted category '{category_name}' to ID {category_id}")
            
            # Convert pet_type name to ID
            if 'pet_type' in product_data:
                pet_type_name = product_data.pop('pet_type')
                pet_type_id = ReferenceData.get_pet_type_id(pet_type_name)
                
                if pet_type_id is None:
                    self.logger.error(f"Invalid pet_type: {pet_type_name}")
                    return None
                
                product_data['pet_type_id'] = pet_type_id
                self.logger.debug(f"Converted pet_type '{pet_type_name}' to ID {pet_type_id}")
            
            # === VALIDATE REQUIRED FIELDS ===
            
            # Generate SKU if not provided
            if 'sku' not in product_data:
                import random
                category_prefix = category_name[:2].upper() if 'category_name' in locals() else 'PR'
                product_data['sku'] = f"{category_prefix}{random.randint(100, 999)}"
            
            # Validate SKU uniqueness
            sku = product_data.get('sku')
            if not sku:
                self.logger.error("SKU is required")
                return None
                
            if self.check_sku_exists(sku):
                self.logger.warning(f"SKU {sku} already exists")
                return None
            
            # Set default values and timestamp
            product_data.setdefault('is_active', True)
            product_data['last_updated'] = datetime.utcnow()
            
            # === CREATE PRODUCT ===
            
            # Create product instance (now with IDs instead of names)
            product = Product(**product_data)
            
            created_product = self.product_repo.create(product)
            
            if created_product:
                self.logger.info(f"Product created successfully: {sku}")
            else:
                self.logger.error(f"Failed to create product: {sku}")
            
            return created_product
            
        except Exception as e:
            self.logger.error(f"Error creating product: {e}", exc_info=True)
            return None
    
    @cache_invalidate([
        lambda self, product_id, **kwargs: f"product:v1:{product_id}:admin=True",
        lambda self, product_id, **kwargs: f"product:v1:{product_id}:admin=False",
        lambda self, product_id, **kwargs: "products:v1:all:admin=True",
        lambda self, product_id, **kwargs: "products:v1:all:admin=False",
    ])
    def update_product(self, product_id: int, **updates) -> Optional[Product]:
        """
        Update an existing product with cache invalidation.
        Converts category and pet_type names to IDs if present in update data.
        Invalidates specific product cache and all list caches after successful update.
        
        Args:
            product_id: ID of product to update
            **updates: Fields to update (can include 'category' and 'pet_type' as names)
            
        Returns:
            Updated Product object or None on error
        """
        try:
            # Get existing product
            product = self.product_repo.get_by_id(product_id)
            if not product:
                self.logger.warning(f"Product {product_id} not found")
                return None
            
            # === CONVERT REFERENCE DATA NAMES TO IDS ===
            
            # Convert category name to ID if present
            if 'category' in updates:
                category_name = updates.pop('category')
                category_id = ReferenceData.get_product_category_id(category_name)
                
                if category_id is None:
                    self.logger.error(f"Invalid category: {category_name}")
                    return None
                
                updates['product_category_id'] = category_id
                self.logger.debug(f"Converted category '{category_name}' to ID {category_id}")
            
            # Convert pet_type name to ID if present
            if 'pet_type' in updates:
                pet_type_name = updates.pop('pet_type')
                pet_type_id = ReferenceData.get_pet_type_id(pet_type_name)
                
                if pet_type_id is None:
                    self.logger.error(f"Invalid pet_type: {pet_type_name}")
                    return None
                
                updates['pet_type_id'] = pet_type_id
                self.logger.debug(f"Converted pet_type '{pet_type_name}' to ID {pet_type_id}")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            # Update last_updated timestamp
            product.last_updated = datetime.utcnow()
            
            updated_product = self.product_repo.update(product)
            
            if updated_product:
                self.logger.info(f"Product {product_id} updated successfully")
            else:
                self.logger.error(f"Failed to update product {product_id}")
            
            return updated_product
            
        except Exception as e:
            self.logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
            return None
    
    @cache_invalidate([
        lambda self, product_id: f"product:v1:{product_id}:admin=True",
        lambda self, product_id: f"product:v1:{product_id}:admin=False",
        lambda self, product_id: "products:v1:all:admin=True",
        lambda self, product_id: "products:v1:all:admin=False",
    ])
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product by ID with cache invalidation.
        Invalidates specific product cache and all list caches after successful deletion.
        
        Args:
            product_id: ID of product to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Check if product exists
            product = self.product_repo.get_by_id(product_id)
            if not product:
                self.logger.warning(f"Product {product_id} not found")
                return False
            
            success = self.product_repo.delete(product_id)
            
            if success:
                self.logger.info(f"Product {product_id} deleted successfully")
            else:
                self.logger.error(f"Failed to delete product {product_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting product {product_id}: {e}")
            return False

    # ============ REFERENCE DATA HELPER METHODS ============
    
    def get_category_id_by_name(self, category_name: str) -> Optional[int]:
        """
        Get category ID by name.
        
        Args:
            category_name: Category name
            
        Returns:
            Category ID or None if not found
        """
        category = self.product_repo.get_category_by_name(category_name)
        return category.id if category else None
    
    def get_pet_type_id_by_name(self, pet_type_name: str) -> Optional[int]:
        """
        Get pet type ID by name.
        
        Args:
            pet_type_name: Pet type name
            
        Returns:
            Pet type ID or None if not found
        """
        pet_type = self.product_repo.get_pet_type_by_name(pet_type_name)
        return pet_type.id if pet_type else None