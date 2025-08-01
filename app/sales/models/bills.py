from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class BillStatus(Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    REFUNDED = "refunded"

@dataclass
class Bill:
    id: int
    order_id: int
    user_id: int
    amount: float
    status: BillStatus
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    def to_dict(self):
        """Convert Bill object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Bill object from dictionary"""
        return cls(
            id=int(data["id"]),
            order_id=int(data["order_id"]),
            user_id=int(data["user_id"]),
            amount=float(data["amount"]),
            status=BillStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        )
