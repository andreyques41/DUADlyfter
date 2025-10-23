"""
Initialize database with roles and test data.
Run this script after creating tables.
"""

from app.utilities.db_manager import DBManager
from app.utilities.base_model import Role, User, Product
from datetime import date


def init_roles(db_manager):
    """Insert default roles: administrator (1) and client (2)."""
    try:
        with db_manager.get_session() as session:
            # Check if roles already exist
            existing_roles = session.query(Role).count()
            if existing_roles > 0:
                print("✅ Roles already initialized")
                return
            
            # Create roles
            admin_role = Role(id=1, name="administrator")
            client_role = Role(id=2, name="client")
            
            session.add_all([admin_role, client_role])
            session.commit()
            
            print("✅ Roles created successfully")
            print("   - 1: administrator")
            print("   - 2: client")
    except Exception as e:
        print(f"❌ Error creating roles: {e}")


def init_test_data(db_manager):
    """Create test users and products (optional)."""
    try:
        with db_manager.get_session() as session:
            # Create admin user
            admin = User(username="admin", password="admin123", role_id=1)
            session.add(admin)
            
            # Create test client
            client = User(username="client1", password="pass123", role_id=2)
            session.add(client)
            
            # Create test products
            products = [
                Product(name="Apple", price=150, quantity=100, entry_date=date.today()),
                Product(name="Banana", price=80, quantity=150, entry_date=date.today()),
                Product(name="Orange", price=120, quantity=200, entry_date=date.today()),
                Product(name="Strawberry", price=200, quantity=50, entry_date=date.today()),
            ]
            session.add_all(products)
            
            session.commit()
            
            print("\n✅ Test data created successfully")
            print("   Users:")
            print("     - admin / admin123 (administrator)")
            print("     - client1 / pass123 (client)")
            print("   Products:")
            print("     - 4 fruits added to inventory")
    except Exception as e:
        print(f"❌ Error creating test data: {e}")


def main():
    print("=== DATABASE INITIALIZATION ===\n")
    
    # Initialize DB Manager
    db_manager = DBManager()
    
    # Create all tables
    print("Creating tables...")
    db_manager.create_all_tables()
    
    # Initialize roles
    print("\nInitializing roles...")
    init_roles(db_manager)
    
    # Ask if user wants test data
    response = input("\nDo you want to create test data? (y/n): ")
    if response.lower() == 'y':
        init_test_data(db_manager)
    
    print("\n🎉 Database initialization complete!")


if __name__ == "__main__":
    main()
