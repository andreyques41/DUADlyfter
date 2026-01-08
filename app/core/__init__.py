"""
Core module - Essential application components

Contains:
- database: SQLAlchemy configuration and session management
- enums: Business logic enums
- lib: Utility functions (auth, jwt, users)
- middleware: Authentication and authorization decorators
"""

from app.core.database import Base, get_schema, set_schema, get_db_session, session_scope, get_engine
from app.core.enums import UserRole, ProductCategory, PetType, OrderStatus, ReturnStatus, InvoiceStatus

__all__ = [
    # Database
    'Base',
    'get_schema',
    'set_schema',
    'get_db_session',
    'session_scope',
    'get_engine',
    # Enums
    'UserRole',
    'ProductCategory',
    'PetType',
    'OrderStatus',
    'ReturnStatus',
    'InvoiceStatus',
]
