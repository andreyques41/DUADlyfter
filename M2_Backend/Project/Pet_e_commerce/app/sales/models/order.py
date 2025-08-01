from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    product_id: int
    product_name: str
    price: float
    quantity: int
    
    def subtotal(self) -> float:
        return self.price * self.quantity
    
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=int(data["product_id"]),
            product_name=data["product_name"],
            price=float(data["price"]),
            quantity=int(data["quantity"])
        )

@dataclass
class Order:
    id: int
    user_id: int
    items: List[OrderItem]
    status: OrderStatus
    total_amount: float
    created_at: Optional[datetime] = None
    shipping_address: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "total_amount": self.total_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "shipping_address": self.shipping_address
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=int(data["id"]),
            user_id=int(data["user_id"]),
            items=[OrderItem.from_dict(item) for item in data["items"]],
            status=OrderStatus(data["status"]),
            total_amount=float(data["total_amount"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            shipping_address=data.get("shipping_address")
        )
