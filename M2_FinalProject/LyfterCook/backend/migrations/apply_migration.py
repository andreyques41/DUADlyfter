"""Apply database migration to add event_date column"""
import psycopg2
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

try:
    # Connect to database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print(f"Connected to database: {DB_NAME}")
    
    # Check quotations schema
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'core' 
          AND table_name = 'quotations'
        ORDER BY ordinal_position
    """)
    
    print("\n=== QUOTATIONS SCHEMA ===")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # Check appointments schema
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'integrations' 
          AND table_name = 'appointments'
        ORDER BY ordinal_position
    """)
    
    print("\n=== APPOINTMENTS SCHEMA ===")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\nDone checking schemas")
    
    # Verify the change
    cursor.execute("""
        SELECT 'quotations' as table_name, column_name
        FROM information_schema.columns 
        WHERE table_schema = 'core' 
          AND table_name = 'quotations' 
          AND column_name = 'event_date'
        UNION ALL
        SELECT 'appointments' as table_name, column_name
        FROM information_schema.columns 
        WHERE table_schema = 'integrations' 
          AND table_name = 'appointments' 
          AND column_name = 'title'
    """)
    
    results = cursor.fetchall()
    print(f"\nVerification: Found {len(results)} columns")
    for row in results:
        print(f"  {row[0]}.{row[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    raise
