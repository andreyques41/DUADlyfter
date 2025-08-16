"""
Order Models Module

This module defines the data models for order management in the e-commerce system.
Provides comprehensive order representation with items, status tracking, and persistence.

Models included:
- OrderStatus: Enum (from app.shared.enums) defining order workflow states
- OrderItem: Individual product items within an order
- Order: Complete order with items, status, and metadata

Features:
- Immutable dataclass design for data integrity
- Status workflow management with enum constraints
- Automatic subtotal calculations for order items
- Complete serialization support for JSON persistence
- Business logic methods for order operations
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from app.shared.enums import OrderStatus

@dataclass
class OrderItem:
    """
    Represents an individual product item within an order.
    
    Attributes:
        product_id (int): Reference to product in catalog
        product_name (str): Product name for display and tracking
        price (float): Unit price at time of order (historical pricing)
        quantity (int): Number of units ordered
    
    Methods:
        subtotal(): Calculate total price for this item (price * quantity)
        to_dict(): Serialize to dictionary for JSON persistence
        from_dict(): Create instance from dictionary data
    
    Business Rules:
    - Price stored at order time for historical accuracy
    - Quantity must be positive integer
    - Subtotal calculated dynamically
    """
    product_id: int
    product_name: str
    price: float
    quantity: int
    
    def subtotal(self) -> float:
        """
        Calculate subtotal for this order item.
        
        Returns:
            float: Total price for this item (price * quantity)
        """
        return self.price * self.quantity
    
    def to_dict(self):
        """
        Serialize order item to dictionary for JSON persistence.
        
        Returns:
            dict: Dictionary representation including calculated subtotal
        """
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create OrderItem instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing order item data
            
        Returns:
            OrderItem: New instance with validated data types
        """
        return cls(
            product_id=int(data["product_id"]),
            product_name=data["product_name"],
            price=float(data["price"]),
            quantity=int(data["quantity"])
        )

@dataclass
class Order:
    """
    Represents a complete customer order with items and metadata.
    
    Attributes:
        id (int): Unique order identifier
        user_id (int): Reference to customer who placed order
        items (List[OrderItem]): List of products in this order
    status (OrderStatus from app.shared.enums): Current order status in workflow
        total_amount (float): Total order value (sum of item subtotals)
        created_at (datetime, optional): Order creation timestamp
        shipping_address (str, optional): Delivery address for order
    
    Methods:
        to_dict(): Serialize complete order to dictionary
        from_dict(): Create order instance from dictionary data
    
    Business Rules:
    - Must contain at least one item
    - Total amount calculated from item subtotals
    - Status follows defined workflow transitions
    - Created timestamp set automatically on creation
    """
    id: int
    user_id: int
    items: List[OrderItem]
    status: OrderStatus
    total_amount: float
    created_at: Optional[datetime] = None
    shipping_address: Optional[str] = None
    
    def to_dict(self):
        """
        Serialize complete order to dictionary for JSON persistence.
        
        Returns:
            dict: Complete order representation including nested items
        """
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
    def from_dict(cls, data, id=None):
        """
        Create Order instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing order data (without id)
            id (int, optional): Order ID to assign (used for updates)
                              If None, id must be set later by service layer
        
        Returns:
            Order: New instance with validated data types and nested items
        """
        return cls(
            id=id if id is not None else 0,  # Temporary ID, should be set by caller
            user_id=int(data["user_id"]),
            items=[OrderItem.from_dict(item) for item in data["items"]],
            status=OrderStatus(data["status"]),
            total_amount=float(data["total_amount"]),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            shipping_address=data.get("shipping_address")
        )
