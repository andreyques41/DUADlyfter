"""
Database Initialization Script
Creates database schemas and tables for LyfterCook.

Organization:
- auth schema: users
- core schema: chefs, clients, dishes, ingredients, menus, menu_dishes, quotations, quotation_items
- integrations schema: appointments, scraped_products
"""

import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core import database
from sqlalchemy import text

# Import all models to register them with Base
from app.auth.models import User
from app.chefs.models import Chef
from app.clients.models import Client
from app.dishes.models import Dish, Ingredient
from app.menus.models import Menu, MenuDish
from app.quotations.models import Quotation, QuotationItem
from app.appointments.models import Appointment
from app.scrapers.models import PriceSource, ScrapedPrice
from app.admin.models.audit_log_model import AuditLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_schemas():
    """Create database schemas if they don't exist."""
    logger.info("Creating database schemas...")
    
    schemas = ['auth', 'core', 'integrations']
    
    with database.engine.connect() as conn:
        for schema in schemas:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()
            logger.info(f"Schema '{schema}' created/verified")


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    
    # Create all tables defined in models
    database.Base.metadata.create_all(bind=database.engine)
    
    logger.info("All tables created successfully")
    
    # Log created tables by schema
    with database.engine.connect() as conn:
        for schema in ['auth', 'core', 'integrations']:
            result = conn.execute(text(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{schema}'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            if tables:
                logger.info(f"\n  Schema '{schema}':")
                for table in tables:
                    logger.info(f"    - {table}")


def drop_all():
    """Drop all tables and schemas. WARNING: Destructive operation!"""
    logger.warning("WARNING: DROPPING ALL TABLES AND SCHEMAS...")
    
    # Drop all tables
    database.Base.metadata.drop_all(bind=database.engine)
    
    # Drop schemas
    with database.engine.connect() as conn:
        for schema in ['auth', 'core', 'integrations']:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
            conn.commit()
            logger.info(f"Schema '{schema}' dropped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize LyfterCook database')
    parser.add_argument('--drop', action='store_true', 
                       help='Drop all tables and schemas before creating')
    args = parser.parse_args()
    
    try:
        if args.drop:
            confirm = input("WARNING: This will DELETE ALL DATA. Type 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                drop_all()
            else:
                logger.info("Operation cancelled")
                sys.exit(0)
        
        logger.info("=" * 60)
        logger.info("LyfterCook Database Initialization")
        logger.info("=" * 60)
        
        # Initialize database connection
        database.init_db()
        
        create_schemas()
        create_tables()
        
        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        sys.exit(1)
