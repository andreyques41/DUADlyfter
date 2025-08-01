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

    def to_dict(self):
        """Convert Product object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category.value,
            "pet_type": self.pet_type.value,
            "stock_quantity": self.stock_quantity,
            "brand": self.brand,
            "weight": self.weight,
            "image_url": self.image_url,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        """Create Product object from dictionary"""
        return cls(
            id=data["id"] if isinstance(data["id"], int) else int(data["id"]),
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            category=ProductCategory(data["category"]),
            pet_type=PetType(data["pet_type"]),
            stock_quantity=int(data["stock_quantity"]),
            brand=data.get("brand"),
            weight=data.get("weight"),
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True)
        )
