"""
Migration Runner: Add Unique Constraints
Executes 004_add_unique_constraints.sql migration
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
migration_path = Path(__file__).parent / '004_add_unique_constraints.sql'
with open(migration_path, 'r', encoding='utf-8') as f:
    sql = f.read()

# Execute migration
conn.autocommit = False
cur = conn.cursor()

try:
    print("=" * 70)
    print("Executing Unique Constraints Migration")
    print("=" * 70)
    print()
    
    # Execute the SQL (includes BEGIN/COMMIT)
    cur.execute(sql)
    
    # Fetch notices
    for notice in conn.notices:
        print(notice.strip())
    
    print()
    print("=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70)
    
except Exception as e:
    conn.rollback()
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
