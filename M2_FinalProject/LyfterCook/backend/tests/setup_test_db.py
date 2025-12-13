"""
Setup Test Database
Creates and configures the test database for running tests.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_test_database():
    """Create test database if it doesn't exist."""
    
    # Connection parameters
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'andyshadow41',  # Use actual PostgreSQL password
        'database': 'postgres'  # Connect to default database first
    }
    
    test_db_name = 'lyftercook_test'
    
    try:
        # Connect to PostgreSQL
        print(f"Connecting to PostgreSQL at {db_params['host']}:{db_params['port']}...")
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (test_db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Test database '{test_db_name}' already exists")
        else:
            # Create test database
            print(f"Creating test database '{test_db_name}'...")
            cursor.execute(f'CREATE DATABASE {test_db_name}')
            print(f"✅ Test database '{test_db_name}' created successfully")
        
        cursor.close()
        conn.close()
        
        # Now connect to test database and create schemas
        db_params['database'] = test_db_name
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create schemas
        schemas = ['auth', 'core', 'integrations']
        for schema in schemas:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            print(f"✅ Schema '{schema}' ready")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Test database setup completed successfully!")
        print(f"\nYou can now run tests with:")
        print("  .\\venv\\Scripts\\python.exe -m pytest tests/ -v")
        
    except psycopg2.Error as e:
        print(f"\n❌ Error setting up test database: {e}")
        print("\nMake sure PostgreSQL is running and accessible with:")
        print(f"  Host: {db_params['host']}")
        print(f"  Port: {db_params['port']}")
        print(f"  User: {db_params['user']}")
        print(f"  Password: {db_params['password']}")
        return False
    
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("LyfterCook Test Database Setup")
    print("=" * 60)
    setup_test_database()
