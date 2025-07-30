from dataclasses import dataclass
from enum import Enum
from typing import Optional

class UserRole(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self):
        """Convert User object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data):
        """Create User object from dictionary"""
        return cls(
            id=data["id"] if isinstance(data["id"], int) else int(data["id"]),
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=UserRole(data["role"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone")
        )
