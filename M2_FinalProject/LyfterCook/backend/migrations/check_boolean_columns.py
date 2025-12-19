"""
Check all boolean columns in database and compare with SQLAlchemy models
PostgreSQL can use BOOLEAN or INTEGER for boolean values - we need to match exactly
"""
import psycopg2
import os
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def main():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        print(f"Connected to database: {DB_NAME}\n")
        print("="*80)
        print("CHECKING ALL BOOLEAN-LIKE COLUMNS IN DATABASE")
        print("="*80)
        
        # Get all columns that might be boolean (boolean type or integer with boolean-like names)
        cursor.execute("""
            SELECT 
                table_schema,
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema IN ('auth', 'core', 'integrations', 'admin')
              AND (
                  data_type = 'boolean' 
                  OR (data_type = 'integer' AND column_name LIKE '%active%')
                  OR (data_type = 'integer' AND column_name LIKE 'is_%')
              )
            ORDER BY table_schema, table_name, column_name
        """)
        
        columns = cursor.fetchall()
        
        if not columns:
            print("No boolean-like columns found")
            return
        
        print(f"\nFound {len(columns)} boolean-like columns:\n")
        
        issues = []
        
        for schema, table, column, data_type, nullable, default in columns:
            is_null = "NULL" if nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            
            status = "✅" if data_type == "boolean" else "⚠️ INTEGER"
            print(f"{status} {schema}.{table}.{column}")
            print(f"   Type: {data_type} {is_null}{default_str}")
            
            if data_type == "integer":
                issues.append({
                    'schema': schema,
                    'table': table,
                    'column': column,
                    'type': data_type
                })
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        if issues:
            print(f"\n⚠️ Found {len(issues)} INTEGER columns that should probably be checked:\n")
            
            model_fixes = {}
            
            for issue in issues:
                full_table = f"{issue['schema']}.{issue['table']}"
                col = issue['column']
                print(f"  • {full_table}.{col} is INTEGER (not BOOLEAN)")
                
                # Group by table for model fixes
                if full_table not in model_fixes:
                    model_fixes[full_table] = []
                model_fixes[full_table].append(col)
            
            print("\n" + "-"*80)
            print("REQUIRED MODEL CHANGES:")
            print("-"*80)
            
            for table, columns in model_fixes.items():
                print(f"\n{table}:")
                for col in columns:
                    print(f"  {col} = Column(Integer, ...) instead of Column(Boolean, ...)")
        else:
            print("\n✅ All boolean columns use BOOLEAN type correctly!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
