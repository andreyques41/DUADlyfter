from dataclasses import dataclass
from enum import Enum
from typing import Optional

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

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    category: ProductCategory
    pet_type: PetType
    stock_quantity: int
    brand: Optional[str] = None
    weight: Optional[float] = None
    image_url: Optional[str] = None
    is_active: bool = True
    # Admin-only fields
    internal_cost: Optional[float] = None
    supplier_info: Optional[str] = None
    created_by: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self, include_admin_fields=False):
        """Convert Product object to dictionary for JSON serialization
        
        Args:
            include_admin_fields: If True, includes admin-only fields like internal_cost
        """
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category.value,
            "pet_type": self.pet_type.value,
            "stock_quantity": self._get_public_stock_info(),  # Public stock info
            "brand": self.brand,
            "weight": self.weight,
            "image_url": self.image_url,
            "is_active": self.is_active
        }
        
        # Add admin fields if requested
        if include_admin_fields:
            result.update({
                "internal_cost": self.internal_cost,
                "supplier_info": self.supplier_info,
                "created_by": self.created_by,
                "last_updated": self.last_updated,
                "actual_stock_quantity": self.stock_quantity  # Real number for admins
            })
        
        return result
    
    def _get_public_stock_info(self):
        """Return user-friendly stock information instead of exact numbers"""
        if self.stock_quantity <= 0:
            return {"status": "out_of_stock", "message": "Out of Stock", "available": False}
        elif self.stock_quantity <= 5:
            return {"status": "low_stock", "message": "Only a few left!", "available": True, "urgency": "high"}
        elif self.stock_quantity <= 20:
            return {"status": "limited_stock", "message": "Limited quantity available", "available": True, "urgency": "medium"}
        elif self.stock_quantity <= 50:
            return {"status": "good_stock", "message": "In Stock", "available": True, "urgency": "low"}
        else:
            return {"status": "plenty_stock", "message": "Plenty in Stock", "available": True, "urgency": "none"}
    
    def is_available(self):
        """Check if product is available for purchase"""
        return self.is_active and self.stock_quantity > 0
    
    def can_fulfill_quantity(self, requested_quantity):
        """Check if we can fulfill a specific quantity request"""
        return self.is_available() and self.stock_quantity >= requested_quantity
    
    def get_max_purchasable_quantity(self, max_per_customer=10):
        """Get maximum quantity a customer can purchase"""
        if not self.is_available():
            return 0
        return min(self.stock_quantity, max_per_customer)
    
    def reserve_stock(self, quantity):
        """Reserve stock for a purchase (decrease available quantity)"""
        if self.can_fulfill_quantity(quantity):
            self.stock_quantity -= quantity
            return True
        return False
    
    def release_stock(self, quantity):
        """Release reserved stock back to inventory (e.g., cancelled order)"""
        self.stock_quantity += quantity

    @classmethod
    def from_dict(cls, data, id=None):
        """Create Product object from dictionary
        
        Args:
            data: Dictionary containing product data (without id)
            id: Optional ID to assign (used for updates), if None, id must be set later
        """
        return cls(
            id=id if id is not None else 0,  # Temporary ID, should be set by caller
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            category=ProductCategory(data["category"]),
            pet_type=PetType(data["pet_type"]),
            stock_quantity=int(data["stock_quantity"]),
            brand=data.get("brand"),
            weight=data.get("weight"),
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True),
            # Admin fields (optional)
            internal_cost=data.get("internal_cost"),
            supplier_info=data.get("supplier_info"),
            created_by=data.get("created_by"),
            last_updated=data.get("last_updated")
        )
