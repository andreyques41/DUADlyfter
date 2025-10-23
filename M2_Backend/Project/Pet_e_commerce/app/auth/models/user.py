"""
User Model Module

Defines the User ORM models with role-based access control for the authentication system.
Now using SQLAlchemy ORM with normalized role tables.

Models:
- Role: Reference table for user roles (normalized)
- RoleUser: Join table for user-role many-to-many relationship
- User: User authentication and profile information

Features:
- SQLAlchemy ORM with normalized reference tables
- Many-to-many relationship between users and roles
- Secure password handling with password_hash field
- Configurable schema support
- Relationships ready for orders, carts, etc.

Migration Notes:
- Migrated from dataclass to SQLAlchemy ORM
- UserRole enum replaced with Role reference table
- Added RoleUser join table for flexibility
- Serialization now handled by Marshmallow schemas (user_schema.py)
"""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from app.core.database import Base, get_schema
from typing import Optional, List


class Role(Base):
    """Reference table for user roles (normalized)."""
    __tablename__ = "roles"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationship
    user_roles: Mapped[List["RoleUser"]] = relationship(back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class RoleUser(Base):
    """Join table for user-role many-to-many relationship."""
    __tablename__ = "role_user"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign keys
    role_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.roles.id"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{get_schema()}.users.id"),
        nullable=False
    )
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="user_roles")
    user: Mapped["User"] = relationship(back_populates="user_roles")
    
    def __repr__(self):
        return f"<RoleUser(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"


class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Authentication fields
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile fields (optional)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Relationships
    user_roles: Mapped[List["RoleUser"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Sales relationships
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    carts: Mapped[List["Cart"]] = relationship(back_populates="user")
    returns: Mapped[List["Return"]] = relationship(back_populates="user")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
