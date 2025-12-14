"""
Seed initial admin user
Run this script to create the default admin account.

Usage:
    python scripts/seed_admin.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import ALL models first to ensure SQLAlchemy relationships are configured
from app.auth.models import User, UserRole
from app.chefs.models import Chef
from app.clients.models import Client
from app.dishes.models import Dish, Ingredient
from app.menus.models import Menu, MenuDish
from app.quotations.models import Quotation, QuotationItem
from app.appointments.models import Appointment
from app.scrapers.models import PriceSource, ScrapedPrice

# Now import services and repositories
from app.auth.repositories import UserRepository
from app.auth.services import AuthService
from config.logging import get_logger
from config import settings

logger = get_logger(__name__)


def seed_admin():
    """Create default admin user if none exists."""
    db = None
    try:
        # Initialize database connection
        from app.core.database import init_db
        init_db()
        
        # Import SessionLocal after init_db() has been called
        from app.core.database import SessionLocal
        
        if SessionLocal is None:
            raise RuntimeError("Failed to initialize database. SessionLocal is None.")
        
        # Create a new database session directly (not using Flask's g)
        db = SessionLocal()
        user_repo = UserRepository(db)
        
        # Check if admin already exists
        admin_username = settings.DEFAULT_ADMIN_USERNAME
        existing_admin = user_repo.get_by_username(admin_username)
        
        if existing_admin:
            logger.info(f"Admin user '{admin_username}' already exists. Skipping.")
            print(f"[INFO] Admin user '{admin_username}' already exists.")
            return
        
        # Create admin user
        auth_service = AuthService(user_repo)
        
        admin_user = user_repo.create(
            username=admin_username,
            email=settings.DEFAULT_ADMIN_EMAIL,
            password_hash=auth_service.security.hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            role=UserRole.ADMIN
        )
        
        if admin_user:
            db.commit()  # Commit the transaction
            logger.info(f"Default admin user created: {admin_username}")
            print(f"[SUCCESS] Default admin user created:")
            print(f"  Username: {admin_username}")
            print(f"  Email: {settings.DEFAULT_ADMIN_EMAIL}")
            print(f"  Password: {settings.DEFAULT_ADMIN_PASSWORD}")
            print(f"\n[WARNING] Change the default password immediately!")
        else:
            logger.error("Failed to create admin user")
            print("[ERROR] Failed to create admin user")
            sys.exit(1)
            
    except Exception as e:
        if db:
            db.rollback()  # Rollback on error
        logger.error(f"Error seeding admin: {e}", exc_info=True)
        print(f"[ERROR] {e}")
        sys.exit(1)
    finally:
        # Close database session
        if db:
            db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("LyfterCook - Seed Default Admin User")
    print("=" * 60)
    
    seed_admin()
    
    print("=" * 60)
    print("Admin seeding completed")
    print("=" * 60)
