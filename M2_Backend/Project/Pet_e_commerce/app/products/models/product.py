"""
Product Model Module

Defines the Product data model for the e-commerce pet store.
Includes category and pet type enums for classification and filtering.

Features:
- ProductCategory enum for product types (food, toys, accessories, etc.)
- PetType enum for target animals (dog, cat, bird, etc.)
- Stock management and availability tracking
- Admin-specific fields (cost, supplier info, created_by)
- JSON serialization for API responses
"""
from dataclasses import dataclass
from app.shared.enums import ProductCategory, PetType
from typing import Optional

# ProductCategory is now imported from app.shared.enums

# PetType is now imported from app.shared.enums

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

    def to_dict_for_db(self):
        result = self.to_dict(include_admin_fields=True)
        result["stock_quantity"] = self.stock_quantity  # Always int for DB
        return result

    def _get_public_stock_info(self):
        """Return user-friendly stock information instead of exact numbers."""
        if self.stock_quantity <= 0:
            return {"status": "out_of_stock", "message": "Out of stock"}
        elif self.stock_quantity <= 5:
            return {"status": "low_stock", "message": "Limited availability"}
        elif self.stock_quantity <= 20:
            return {"status": "in_stock", "message": "In stock"}
        else:
            return {"status": "in_stock", "message": "Available"}

    def is_available(self):
        """Check if product is available for purchase."""
        return self.is_active and self.stock_quantity > 0


    @classmethod
    def from_dict(cls, data):
        """Create Product instance from dictionary data."""
        return cls(
            id=int(data.get("id", 0)),
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            category=ProductCategory(data["category"]),
            pet_type=PetType(data["pet_type"]),
            stock_quantity=int(data["stock_quantity"]),
            brand=data.get("brand"),
            weight=float(data["weight"]) if data.get("weight") is not None else None,
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True),
            internal_cost=float(data["internal_cost"]) if data.get("internal_cost") is not None else None,
            supplier_info=data.get("supplier_info"),
            created_by=data.get("created_by"),
            last_updated=data.get("last_updated")
        )
