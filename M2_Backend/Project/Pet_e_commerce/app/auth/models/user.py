"""
User Model Module

Defines the User data model with role-based access control for the authentication system.
Includes serialization methods for API responses and secure storage.

Features:
- UserRole enum for customer/admin roles
- Secure password handling (separate serialization methods)
- Flexible factory methods for object creation
- JSON serialization/deserialization support
"""
from dataclasses import dataclass
from app.shared.enums import UserRole
from typing import Optional

# UserRole is now imported from app.shared.enums

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
        """Convert User object to dictionary for JSON serialization (API responses)
        
        NOTE: password_hash is intentionally excluded for security
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }

    def to_dict_with_password(self):
        """Convert User object to dictionary including password hash (for storage only)
        
        WARNING: This includes password_hash and should ONLY be used for internal storage,
        NEVER for API responses or logging
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role.value,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data, id=None, password_hash=None):
        """Create User object from dictionary

        Args:
            data: Dictionary containing user data (without id or password_hash)
            id: Optional ID to assign (used for updates), if None, id must be set later
            password_hash: Pre-hashed password (backend should hash the password before calling this)
        """
        return cls(
            id=id if id is not None else 0,  # Temporary ID, should be set by caller
            username=data["username"],
            email=data["email"],
            password_hash=password_hash if password_hash is not None else "",  # Backend provides this
            role=UserRole(data["role"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone")
        )

    @classmethod
    def from_dict_with_password(cls, data):
        """Create User object from dictionary that includes password_hash (for loading from storage)
        
        Args:
            data: Complete dictionary including id and password_hash (from database)
        """
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=UserRole(data["role"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone")
        )
