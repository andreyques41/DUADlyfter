from enum import Enum

# --- User ---
class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

# --- Sales ---
class ReturnStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"

class BillStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    REFUNDED = "refunded"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# --- Products ---
class ProductCategory(Enum):
    FOOD = "food"
    TOYS = "toys"
    ACCESSORIES = "accessories"
    HEALTH = "health"
    GROOMING = "grooming"

class PetType(Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    OTHER = "other"
