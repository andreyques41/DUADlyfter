"""
Product Repository Module

Handles all database operations for Product model using SQLAlchemy ORM.
Provides CRUD operations and query methods for product management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- Product lookups by different fields (id, sku)
- Advanced filtering capabilities
- Transaction management via session_scope

Usage:
    repo = ProductRepository()
    product = repo.get_by_id(1)
    all_products = repo.get_all()
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from app.core.database import session_scope
from app.products.models.product import Product, ProductCategory, PetType
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    """Repository for Product database operations."""
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: Product ID to search for
            
        Returns:
            Product object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Product).filter_by(id=product_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching product by id {product_id}: {e}")
            return None
    
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU to search for
            
        Returns:
            Product object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Product).filter_by(sku=sku).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching product by SKU {sku}: {e}")
            return None
    
    def get_all(self) -> List[Product]:
        """
        Get all products.
        
        Returns:
            List of all Product objects
        """
        try:
            with session_scope() as session:
                return session.query(Product).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all products: {e}")
            return []
    
    def get_by_filters(self, filters: Dict[str, Any]) -> List[Product]:
        """
        Get products by filters.
        
        Args:
            filters: Dictionary with filter criteria
                - category_id: int
                - pet_type_id: int
                - brand: str
                - min_stock: int
                - is_active: bool
                - search: str (searches in description and brand)
                
        Returns:
            List of filtered Product objects
        """
        try:
            with session_scope() as session:
                query = session.query(Product)
                
                # Apply filters
                if 'category_id' in filters:
                    query = query.filter(Product.product_category_id == filters['category_id'])
                
                if 'pet_type_id' in filters:
                    query = query.filter(Product.pet_type_id == filters['pet_type_id'])
                
                if 'brand' in filters:
                    query = query.filter(Product.brand.ilike(f"%{filters['brand']}%"))
                
                if 'min_stock' in filters:
                    query = query.filter(Product.stock_quantity >= filters['min_stock'])
                
                if 'is_active' in filters:
                    query = query.filter(Product.is_active == filters['is_active'])
                
                if 'search' in filters:
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            Product.description.ilike(search_term),
                            Product.brand.ilike(search_term)
                        )
                    )
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching products with filters: {e}")
            return []
    
    def create(self, product: Product) -> Optional[Product]:
        """
        Create a new product in the database.
        
        Args:
            product: Product object to create (without ID)
            
        Returns:
            Created Product object with ID, or None on error
        """
        try:
            with session_scope() as session:
                session.add(product)
                session.flush()  # Get the ID before commit
                session.refresh(product)  # Refresh to load relationships
                return product
        except SQLAlchemyError as e:
            logger.error(f"Error creating product {product.sku}: {e}")
            return None
    
    def update(self, product: Product) -> Optional[Product]:
        """
        Update an existing product.
        
        Args:
            product: Product object with updated data
            
        Returns:
            Updated Product object or None on error
        """
        try:
            with session_scope() as session:
                # Merge the detached product object into the session
                updated_product = session.merge(product)
                session.flush()
                session.refresh(updated_product)
                return updated_product
        except SQLAlchemyError as e:
            logger.error(f"Error updating product {product.id}: {e}")
            return None
    
    def delete(self, product_id: int) -> bool:
        """
        Delete a product by ID.
        
        Args:
            product_id: ID of product to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            with session_scope() as session:
                product = session.query(Product).filter_by(id=product_id).first()
                if product:
                    session.delete(product)
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            return False
    
    def exists_by_sku(self, sku: str) -> bool:
        """
        Check if a product exists by SKU.
        
        Args:
            sku: Product SKU to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            with session_scope() as session:
                return session.query(Product).filter_by(sku=sku).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if SKU {sku} exists: {e}")
            return False
    
    def get_category_by_name(self, category_name: str) -> Optional[ProductCategory]:
        """
        Get product category by name.
        
        Args:
            category_name: Category name to search for
            
        Returns:
            ProductCategory object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(ProductCategory).filter_by(category=category_name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching category {category_name}: {e}")
            return None
    
    def get_pet_type_by_name(self, pet_type_name: str) -> Optional[PetType]:
        """
        Get pet type by name.
        
        Args:
            pet_type_name: Pet type name to search for
            
        Returns:
            PetType object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(PetType).filter_by(type=pet_type_name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching pet type {pet_type_name}: {e}")
            return None
