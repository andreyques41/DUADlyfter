from sqlalchemy import String, Integer, Date, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr
from datetime import date
from typing import Optional, List


# Global variable to store the schema name
_schema_name = None


def set_schema(schema: str):
    """Set the global schema name for all models."""
    global _schema_name
    _schema_name = schema


def get_schema() -> str:
    """Get the current schema name."""
    return _schema_name or 'backend_week7'


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ============================================
# MODELS
# ============================================

class Role(Base):
    """Role model for user permissions (cliente/administrador)."""
    __tablename__ = "roles"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 'cliente' or 'administrador'
    
    # Relationship
    users: Mapped[List["User"]] = relationship(back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey(f"{get_schema()}.roles.id"), nullable=False)
    
    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role_id={self.role_id})>"


class Product(Base):
    """Product model for fruits inventory management."""
    __tablename__ = "products"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    
    # Relationship
    invoice_items: Mapped[List["InvoiceItem"]] = relationship(back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class Invoice(Base):
    """Invoice model for sales transactions."""
    __tablename__ = "invoices"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{get_schema()}.users.id"), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    total: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="invoices")
    items: Mapped[List["InvoiceItem"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, user_id={self.user_id}, total={self.total})>"


class InvoiceItem(Base):
    """Invoice item model - many-to-many relationship between Invoice and Product."""
    __tablename__ = "invoice_items"
    
    @declared_attr
    def __table_args__(cls):
        return {'schema': get_schema()}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey(f"{get_schema()}.invoices.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{get_schema()}.products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[int] = mapped_column(nullable=False)
    subtotal: Mapped[int] = mapped_column(nullable=False)
    
    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="invoice_items")
    
    def __repr__(self):
        return f"<InvoiceItem(id={self.id}, invoice_id={self.invoice_id}, product_id={self.product_id})>"
