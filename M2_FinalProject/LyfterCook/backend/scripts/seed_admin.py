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

from app.core.database import get_db
from app.auth.repositories import UserRepository
from app.auth.services import AuthService
from app.auth.models import UserRole
from config.logging import get_logger
from config import settings

logger = get_logger(__name__)


def seed_admin():
    """Create default admin user if none exists."""
    try:
        # Initialize database connection
        from app.core.database import init_db
        init_db()
        
        db = get_db()
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
        logger.error(f"Error seeding admin: {e}", exc_info=True)
        print(f"[ERROR] {e}")
        sys.exit(1)
    finally:
        # Close database connection
        from app.core.database import close_db
        close_db()


if __name__ == "__main__":
    print("=" * 60)
    print("LyfterCook - Seed Default Admin User")
    print("=" * 60)
    
    seed_admin()
    
    print("=" * 60)
    print("Admin seeding completed")
    print("=" * 60)
