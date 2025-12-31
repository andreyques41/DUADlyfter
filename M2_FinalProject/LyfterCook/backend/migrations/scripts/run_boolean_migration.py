"""
Migration Runner: Standardize Boolean Types
Executes 002_standardize_boolean_types.sql migration
"""

import psycopg2
import os
from dotenv import load_dotenv

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
with open('migrations/002_standardize_boolean_types.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Execute migration
conn.autocommit = False
cur = conn.cursor()

try:
    print("Executing Boolean type standardization migration...")
    print("-" * 60)
    
    # Execute the SQL (includes BEGIN/COMMIT)
    cur.execute(sql)
    
    # Fetch notices
    for notice in conn.notices:
        print(notice.strip())
    
    print("-" * 60)
    print("✅ Migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    cur.close()
    conn.close()
