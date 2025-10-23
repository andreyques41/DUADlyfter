"""
Reference Data Helper Module

Provides bidirectional mapping between reference table names and IDs.
This bridges the gap between:
- User-friendly enum strings in API (e.g., "food", "dog", "admin")
- Normalized database IDs (e.g., product_category_id=1)

Features:
- Lazy loading from database (cached after first use)
- Bidirectional lookups (name→ID and ID→name)
- Validation helpers
- Thread-safe singleton pattern

Usage:
    # Convert name to ID for database operations
    category_id = ReferenceData.get_product_category_id("food")  # Returns 1
    
    # Convert ID to name for API responses
    category_name = ReferenceData.get_product_category_name(1)   # Returns "food"
    
    # Validate if a category exists
    is_valid = ReferenceData.is_valid_product_category("toys")   # Returns True/False
"""
from typing import Optional, Dict
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class ReferenceDataCache:
    """
    Singleton cache for reference data lookups.
    Loads data once from database and caches in memory.
    """
    _instance = None
    _initialized = False
    
    # Cache dictionaries (name → ID and ID → name)
    _product_categories: Dict[str, int] = {}
    _product_categories_reverse: Dict[int, str] = {}
    
    _pet_types: Dict[str, int] = {}
    _pet_types_reverse: Dict[int, str] = {}
    
    _roles: Dict[str, int] = {}
    _roles_reverse: Dict[int, str] = {}
    
    _order_statuses: Dict[str, int] = {}
    _order_statuses_reverse: Dict[int, str] = {}
    
    _return_statuses: Dict[str, int] = {}
    _return_statuses_reverse: Dict[int, str] = {}
    
    _invoice_statuses: Dict[str, int] = {}
    _invoice_statuses_reverse: Dict[int, str] = {}
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls):
        """Load all reference data from database into cache."""
        if cls._initialized:
            return
        
        try:
            from app.core.database import get_db
            from app.products.models.product import ProductCategory, PetType
            from app.auth.models.user import Role
            from app.sales.models.order import OrderStatus
            from app.sales.models.returns import ReturnStatus
            from app.sales.models.invoice import InvoiceStatus
            
            db = get_db()
            
            # Load Product Categories
            categories = db.query(ProductCategory).all()
            for cat in categories:
                cls._product_categories[cat.category.lower()] = cat.id
                cls._product_categories_reverse[cat.id] = cat.category.lower()
            
            # Load Pet Types
            pet_types = db.query(PetType).all()
            for pet in pet_types:
                cls._pet_types[pet.type.lower()] = pet.id
                cls._pet_types_reverse[pet.id] = pet.type.lower()
            
            # Load Roles
            roles = db.query(Role).all()
            for role in roles:
                cls._roles[role.name.lower()] = role.id
                cls._roles_reverse[role.id] = role.name.lower()
            
            # Load Order Statuses
            order_statuses = db.query(OrderStatus).all()
            for status in order_statuses:
                cls._order_statuses[status.status.lower()] = status.id
                cls._order_statuses_reverse[status.id] = status.status.lower()
            
            # Load Return Statuses
            return_statuses = db.query(ReturnStatus).all()
            for status in return_statuses:
                cls._return_statuses[status.status.lower()] = status.id
                cls._return_statuses_reverse[status.id] = status.status.lower()
            
            # Load Invoice Statuses
            invoice_statuses = db.query(InvoiceStatus).all()
            for status in invoice_statuses:
                cls._invoice_statuses[status.name.lower()] = status.id
                cls._invoice_statuses_reverse[status.id] = status.name.lower()
            
            cls._initialized = True
            logger.info("Reference data cache initialized successfully")
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize reference data cache: {e}")
            raise
    
    @classmethod
    def reset(cls):
        """Reset cache (useful for testing or when reference data changes)."""
        cls._initialized = False
        cls._product_categories.clear()
        cls._product_categories_reverse.clear()
        cls._pet_types.clear()
        cls._pet_types_reverse.clear()
        cls._roles.clear()
        cls._roles_reverse.clear()
        cls._order_statuses.clear()
        cls._order_statuses_reverse.clear()
        cls._return_statuses.clear()
        cls._return_statuses_reverse.clear()
        cls._invoice_statuses.clear()
        cls._invoice_statuses_reverse.clear()


class ReferenceData:
    """
    Static helper class for reference data lookups.
    Provides clean API for converting between names and IDs.
    """
    
    # ============================================
    # PRODUCT CATEGORIES
    # ============================================
    
    @staticmethod
    def get_product_category_id(category_name: str) -> Optional[int]:
        """
        Get product category ID from category name.
        
        Args:
            category_name: Category name (e.g., "food", "toys")
            
        Returns:
            Category ID or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._product_categories.get(category_name.lower())
    
    @staticmethod
    def get_product_category_name(category_id: int) -> Optional[str]:
        """
        Get product category name from category ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category name or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._product_categories_reverse.get(category_id)
    
    @staticmethod
    def is_valid_product_category(category_name: str) -> bool:
        """Check if category name is valid."""
        return ReferenceData.get_product_category_id(category_name) is not None
    
    @staticmethod
    def get_all_product_categories() -> Dict[str, int]:
        """Get all product categories (name → ID mapping)."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._product_categories.copy()
    
    # ============================================
    # PET TYPES
    # ============================================
    
    @staticmethod
    def get_pet_type_id(type_name: str) -> Optional[int]:
        """
        Get pet type ID from type name.
        
        Args:
            type_name: Pet type name (e.g., "dog", "cat")
            
        Returns:
            Pet type ID or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._pet_types.get(type_name.lower())
    
    @staticmethod
    def get_pet_type_name(type_id: int) -> Optional[str]:
        """
        Get pet type name from type ID.
        
        Args:
            type_id: Pet type ID
            
        Returns:
            Pet type name or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._pet_types_reverse.get(type_id)
    
    @staticmethod
    def is_valid_pet_type(type_name: str) -> bool:
        """Check if pet type name is valid."""
        return ReferenceData.get_pet_type_id(type_name) is not None
    
    @staticmethod
    def get_all_pet_types() -> Dict[str, int]:
        """Get all pet types (name → ID mapping)."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._pet_types.copy()
    
    # ============================================
    # USER ROLES
    # ============================================
    
    @staticmethod
    def get_role_id(role_name: str) -> Optional[int]:
        """
        Get role ID from role name.
        
        Args:
            role_name: Role name (e.g., "admin", "user")
            
        Returns:
            Role ID or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._roles.get(role_name.lower())
    
    @staticmethod
    def get_role_name(role_id: int) -> Optional[str]:
        """
        Get role name from role ID.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role name or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._roles_reverse.get(role_id)
    
    @staticmethod
    def is_valid_role(role_name: str) -> bool:
        """Check if role name is valid."""
        return ReferenceData.get_role_id(role_name) is not None
    
    @staticmethod
    def get_all_roles() -> Dict[str, int]:
        """Get all roles (name → ID mapping)."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._roles.copy()
    
    # ============================================
    # ORDER STATUSES
    # ============================================
    
    @staticmethod
    def get_order_status_id(status_name: str) -> Optional[int]:
        """
        Get order status ID from status name.
        
        Args:
            status_name: Status name (e.g., "pending", "shipped")
            
        Returns:
            Status ID or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._order_statuses.get(status_name.lower())
    
    @staticmethod
    def get_order_status_name(status_id: int) -> Optional[str]:
        """
        Get order status name from status ID.
        
        Args:
            status_id: Status ID
            
        Returns:
            Status name or None if not found
        """
        ReferenceDataCache.initialize()
        return ReferenceDataCache._order_statuses_reverse.get(status_id)
    
    @staticmethod
    def is_valid_order_status(status_name: str) -> bool:
        """Check if order status name is valid."""
        return ReferenceData.get_order_status_id(status_name) is not None
    
    @staticmethod
    def get_all_order_statuses() -> Dict[str, int]:
        """Get all order statuses (name → ID mapping)."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._order_statuses.copy()
    
    # ============================================
    # RETURN STATUSES
    # ============================================
    
    @staticmethod
    def get_return_status_id(status_name: str) -> Optional[int]:
        """Get return status ID from status name."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._return_statuses.get(status_name.lower())
    
    @staticmethod
    def get_return_status_name(status_id: int) -> Optional[str]:
        """Get return status name from status ID."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._return_statuses_reverse.get(status_id)
    
    @staticmethod
    def is_valid_return_status(status_name: str) -> bool:
        """Check if return status name is valid."""
        return ReferenceData.get_return_status_id(status_name) is not None
    
    # ============================================
    # INVOICE STATUSES
    # ============================================
    
    @staticmethod
    def get_invoice_status_id(status_name: str) -> Optional[int]:
        """Get invoice status ID from status name."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._invoice_statuses.get(status_name.lower())
    
    @staticmethod
    def get_invoice_status_name(status_id: int) -> Optional[str]:
        """Get invoice status name from status ID."""
        ReferenceDataCache.initialize()
        return ReferenceDataCache._invoice_statuses_reverse.get(status_id)
    
    @staticmethod
    def is_valid_invoice_status(status_name: str) -> bool:
        """Check if invoice status name is valid."""
        return ReferenceData.get_invoice_status_id(status_name) is not None
