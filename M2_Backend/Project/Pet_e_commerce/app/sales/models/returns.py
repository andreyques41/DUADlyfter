from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

class ReturnStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"

@dataclass
class ReturnItem:
    product_id: int
    product_name: str
    quantity: int
    reason: str
    refund_amount: float
    
    def to_dict(self):
        """Convert ReturnItem object to dictionary for JSON serialization"""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "reason": self.reason,
            "refund_amount": self.refund_amount
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create ReturnItem object from dictionary"""
        return cls(
            product_id=int(data["product_id"]),
            product_name=data["product_name"],
            quantity=int(data["quantity"]),
            reason=data["reason"],
            refund_amount=float(data["refund_amount"])
        )

@dataclass
class Return:
    id: int
    bill_id: int
    order_id: int
    user_id: int
    items: List[ReturnItem]
    status: ReturnStatus
    total_refund: float
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        """Convert Return object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "total_refund": self.total_refund,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Return object from dictionary"""
        return cls(
            id=int(data["id"]),
            bill_id=int(data["bill_id"]),
            order_id=int(data["order_id"]),
            user_id=int(data["user_id"]),
            items=[ReturnItem.from_dict(item) for item in data["items"]],
            status=ReturnStatus(data["status"]),
            total_refund=float(data["total_refund"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
