from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class CartItem:
    product_id: int
    product_name: str
    price: float
    quantity: int
    
    def subtotal(self) -> float:
        return self.price * self.quantity
    
    def to_dict(self):
        """Convert CartItem object to dictionary for JSON serialization"""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create CartItem object from dictionary"""
        return cls(
            product_id=int(data["product_id"]),
            product_name=data["product_name"],
            price=float(data["price"]),
            quantity=int(data["quantity"])
        )

@dataclass
class Cart:
    id: int
    user_id: int
    items: List[CartItem]
    created_at: Optional[datetime] = None
    
    def total(self) -> float:
        return sum(item.subtotal() for item in self.items)
    
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
    
    def to_dict(self):
        """Convert Cart object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "total": self.total(),
            "item_count": self.item_count(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data, id=None):
        """Create Cart object from dictionary
        
        Args:
            data: Dictionary containing cart data (without id)
            id: Optional ID to assign (used for updates), if None, id must be set later
        """
        return cls(
            id=id if id is not None else 0,  # Temporary ID, should be set by caller
            user_id=int(data["user_id"]),
            items=[CartItem.from_dict(item) for item in data["items"]],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
