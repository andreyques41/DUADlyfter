"""
Shared Enums Module

Defines Python enums for business logic validation and type safety.
These enums correspond to normalized reference tables in the database.

Key Points:
- Enum values MUST match the string values stored in database reference tables
- Used for type hints, validation, and business logic
- Database uses normalized tables (roles, order_status, etc.)
- This provides type safety without sacrificing normalization

Usage:
    # In business logic
    if user.role == UserRole.ADMIN:
        # admin logic
    
    # In ORM queries (comparing with string values from DB)
    from app.shared.enums import OrderStatus
    pending_orders = session.query(Order).join(OrderStatus).filter(
        OrderStatus.status == OrderStatus.PENDING.value
    ).all()
"""
from enum import Enum

# ===========================================
# USER ROLES
# ===========================================

class UserRole(Enum):
    """User role types - corresponds to roles table"""
    USER = "user"
    ADMIN = "admin"
    
    @classmethod
    def get_role_id_map(cls):
        """Helper to map role names to expected IDs (convention: user=1, admin=2)"""
        return {
            cls.USER.value: 1,
            cls.ADMIN.value: 2
        }


# ===========================================
# PRODUCT ENUMS
# ===========================================

class ProductCategory(Enum):
    """Product categories - corresponds to product_categories table"""
    FOOD = "food"
    TOYS = "toys"
    ACCESSORIES = "accessories"
    HEALTH = "health"
    GROOMING = "grooming"


class PetType(Enum):
    """Pet types - corresponds to pet_types table"""
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"


# ===========================================
# ORDER ENUMS
# ===========================================

class OrderStatus(Enum):
    """Order status types - corresponds to order_status table"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ===========================================
# RETURN ENUMS
# ===========================================

class ReturnStatus(Enum):
    """Return status types - corresponds to return_status table"""
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"


# ===========================================
# INVOICE ENUMS
# ===========================================

class InvoiceStatus(Enum):
    """Invoice status types - corresponds to invoice_status table"""
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    REFUNDED = "refunded"


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def get_enum_values(enum_class):
    """Get all values from an enum as a list"""
    return [e.value for e in enum_class]


def is_valid_enum_value(enum_class, value):
    """Check if a value is valid for a given enum"""
    return value in get_enum_values(enum_class)
