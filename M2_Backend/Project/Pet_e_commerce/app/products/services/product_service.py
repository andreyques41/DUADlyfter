"""
Product Service Module

Business logic layer for product management.
Handles validation, filtering, and product operations.

Responsibilities:
- Product CRUD operations with validation
- Advanced filtering and search
- Business logic and validation rules
- Orchestrates repository operations

Dependencies:
- ProductRepository: Database operations

Usage:
    service = ProductService()
    product = service.get_product_by_id(1)
    products = service.get_products_by_filters({'category_id': 1})
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.products.repositories import ProductRepository
from app.products.models.product import Product

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product management business logic."""
    
    def __init__(self):
        self.product_repo = ProductRepository()
        self.logger = logger

    # ============ PRODUCT RETRIEVAL METHODS ============
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Get a product by ID.
        
        Args:
            product_id: Product ID to fetch
        
        Returns:
            Product object or None if not found
        """
        self.logger.debug(f"Fetching product with id {product_id}")
        return self.product_repo.get_by_id(product_id)
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get a product by SKU.
        
        Args:
            sku: Product SKU to search for
            
        Returns:
            Product object or None if not found
        """
        self.logger.debug(f"Fetching product with SKU {sku}")
        return self.product_repo.get_by_sku(sku)
    
    def get_all_products(self) -> List[Product]:
        """
        Get all products.
        
        Returns:
            List of all products
        """
        self.logger.debug("Fetching all products")
        return self.product_repo.get_all()
    
    def get_products_by_filters(self, filters: Dict[str, Any]) -> List[Product]:
        """
        Get products with filters applied.
        
        Args:
            filters: Dictionary with filter criteria
                - category_id: int
                - pet_type_id: int
                - brand: str
                - min_stock: int
                - is_active: bool
                - search: str
            
        Returns:
            List of filtered products
        """
        self.logger.debug(f"Fetching products with filters: {filters}")
        return self.product_repo.get_by_filters(filters)

    # ============ PRODUCT VALIDATION METHODS ============
    
    def check_sku_exists(self, sku: str) -> bool:
        """Check if SKU already exists."""
        return self.product_repo.exists_by_sku(sku)

    # ============ PRODUCT CRUD OPERATIONS ============
    
    def create_product(self, **product_data) -> Optional[Product]:
        """
        Create a new product.
        
        Args:
            **product_data: Product fields including:
                - sku (required): Product SKU (must be unique)
                - description (required): Product description
                - product_category_id (required): Category ID
                - pet_type_id (required): Pet type ID
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
            
            # Create product instance
            product = Product(**product_data)
            
            created_product = self.product_repo.create(product)
            
            if created_product:
                self.logger.info(f"Product created successfully: {sku}")
            else:
                self.logger.error(f"Failed to create product: {sku}")
            
            return created_product
            
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return None
    
    def update_product(self, product_id: int, **updates) -> Optional[Product]:
        """
        Update an existing product.
        
        Args:
            product_id: ID of product to update
            **updates: Fields to update
            
        Returns:
            Updated Product object or None on error
        """
        try:
            # Get existing product
            product = self.product_repo.get_by_id(product_id)
            if not product:
                self.logger.warning(f"Product {product_id} not found")
                return None
            
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
            self.logger.error(f"Error updating product {product_id}: {e}")
            return None
    
    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product by ID.
        
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

    # ============ HELPER METHODS ============
    
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