"""
Initialize Pet E-commerce Database

Creates all tables and populates reference tables with initial data.
Run this script after configuring database connection settings.

Reference Tables Initialized:
- Roles (USER, ADMIN)
- Product Categories (food, toys, accessories, health, grooming)
- Pet Types (dog, cat, bird, fish, reptile, other)
- Order Status (pending, confirmed, processing, shipped, delivered, cancelled)
- Return Status (requested, approved, rejected, processed)
- Invoice Status (paid, pending, overdue, refunded)

Usage:
    python scripts/init_db.py
"""

from app.core.database import Base, set_schema, get_engine, session_scope
from app.auth.models.user import Role, RoleUser, User
from app.products.models.product import ProductCategory, PetType, Product
from app.sales.models.order import OrderStatus, OrderItem, Order
from app.sales.models.cart import CartItem, Cart
from app.sales.models.bills import InvoiceStatus, Invoice
from app.sales.models.returns import ReturnStatus, ReturnItem, Return
from config.settings import get_database_url, DB_SCHEMA

from sqlalchemy import text


def init_reference_tables(session):
    """Populate reference tables with initial data."""
    
    print("\n📋 Initializing reference tables...")
    
    # --- Roles ---
    roles = [
        Role(name="user", description="Regular user with basic permissions"),
        Role(name="admin", description="Administrator with full permissions"),
    ]
    session.add_all(roles)
    print("   ✅ Roles created")
    
    # --- Product Categories ---
    categories = [
        ProductCategory(category="food"),
        ProductCategory(category="toys"),
        ProductCategory(category="accessories"),
        ProductCategory(category="health"),
        ProductCategory(category="grooming"),
    ]
    session.add_all(categories)
    print("   ✅ Product categories created")
    
    # --- Pet Types ---
    pet_types = [
        PetType(type="dog"),
        PetType(type="cat"),
        PetType(type="bird"),
        PetType(type="fish"),
        PetType(type="reptile"),
        PetType(type="other"),
    ]
    session.add_all(pet_types)
    print("   ✅ Pet types created")
    
    # --- Order Status ---
    order_statuses = [
        OrderStatus(status="pending"),
        OrderStatus(status="confirmed"),
        OrderStatus(status="processing"),
        OrderStatus(status="shipped"),
        OrderStatus(status="delivered"),
        OrderStatus(status="cancelled"),
    ]
    session.add_all(order_statuses)
    print("   ✅ Order statuses created")
    
    # --- Return Status ---
    return_statuses = [
        ReturnStatus(status="requested"),
        ReturnStatus(status="approved"),
        ReturnStatus(status="rejected"),
        ReturnStatus(status="processed"),
    ]
    session.add_all(return_statuses)
    print("   ✅ Return statuses created")
    
    # --- Invoice Status ---
    invoice_statuses = [
        InvoiceStatus(name="paid"),
        InvoiceStatus(name="pending"),
        InvoiceStatus(name="overdue"),
        InvoiceStatus(name="refunded"),
    ]
    session.add_all(invoice_statuses)
    print("   ✅ Invoice statuses created")
    
    session.commit()
    print("\n✅ All reference tables populated successfully!")


def create_test_data(session):
    """Create sample test data (optional)."""
    
    print("\n📦 Creating test data...")
    
    # Note: This would require implementing password hashing first
    # For now, this is a placeholder
    
    print("   ℹ️  Test data creation skipped")
    print("   💡 Implement this after setting up authentication service")


def main():
    print("=" * 50)
    print("PET E-COMMERCE DATABASE INITIALIZATION")
    print("=" * 50)
    
    # Get schema name from config
    schema_name = DB_SCHEMA
    set_schema(schema_name)
    print(f"\n🗄️  Schema: {schema_name}")
    
    # Get database engine
    print(f"🔗 Connecting to database...")
    
    try:
        engine = get_engine()
        
        # Create schema if it doesn't exist
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            conn.commit()
            print(f"✅ Schema '{schema_name}' ready")
        
        # Create all tables
        print("\n📊 Creating tables...")
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully!")
        
        # Initialize reference tables using session_scope
        with session_scope() as session:
            # Check if reference tables are already populated
            if session.query(Role).count() > 0:
                print("\n⚠️  Reference tables already contain data")
                response = input("Do you want to skip initialization? (y/n): ")
                if response.lower() == 'y':
                    print("Skipping reference table initialization")
                else:
                    session.query(Role).delete()
                    session.query(ProductCategory).delete()
                    session.query(PetType).delete()
                    session.query(OrderStatus).delete()
                    session.query(ReturnStatus).delete()
                    session.query(InvoiceStatus).delete()
                    session.commit()
                    init_reference_tables(session)
            else:
                init_reference_tables(session)
            
            # Ask if user wants test data
            response = input("\nDo you want to create test data? (y/n): ")
            if response.lower() == 'y':
                create_test_data(session)
        
        print("\n" + "=" * 50)
        print("🎉 DATABASE INITIALIZATION COMPLETE!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
