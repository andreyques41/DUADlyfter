"""
Migration Runner: Standardize VARCHAR Lengths
Executes 003_standardize_varchar_lengths.sql migration
"""

import psycopg2
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv('config/.env')

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

# Read migration file
migration_path = Path(__file__).parent / '003_standardize_varchar_lengths.sql'
with open(migration_path, 'r', encoding='utf-8') as f:
    sql = f.read()

# Execute migration
conn.autocommit = False
cur = conn.cursor()

try:
    print("Executing VARCHAR length standardization migration...")
    print("-" * 60)
    
    # Execute the SQL (includes BEGIN/COMMIT)
    cur.execute(sql)
    
    # Fetch notices
    for notice in conn.notices:
        print(notice.strip())
    
    print("-" * 60)
    print("✅ Migration completed successfully!")
    print()
    print("Changes applied:")
    print("  • core.ingredients.unit: VARCHAR(20) → VARCHAR(50)")
    print("  • integrations.scraped_products.ingredient_name: VARCHAR(100) → VARCHAR(200)")
    print("  • integrations.scraped_products.product_name: VARCHAR(200) → VARCHAR(300)")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
