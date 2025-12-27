"""
Run the menustatus enum expansion migration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text, create_engine
from config.logging import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# Create engine directly
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/lyfter_cook_db')
engine = create_engine(DATABASE_URL, echo=True)


def run_migration():
    """Execute the menustatus enum expansion migration"""
    try:
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), '005_expand_menustatus_enum.sql')
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        logger.info("Starting menustatus enum expansion migration...")
        
        # Execute migration
        with engine.begin() as conn:
            conn.execute(text(sql))
        
        logger.info("✅ Migration completed successfully")
        print("\n✅ menustatus enum expanded successfully!")
        print("New values: draft, published, archived, seasonal")
        print("Old ACTIVE menus updated to 'published'")
        print("Old INACTIVE menus updated to 'archived'")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        print(f"\n❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    run_migration()
