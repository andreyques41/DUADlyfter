"""
Duplication Check Audit
=======================
Analyzes all creation endpoints to identify which check for duplicates.

This script reviews:
1. Database unique constraints
2. Application-level validation
3. Recommendations for duplication prevention
"""

import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict

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

def get_all_unique_constraints():
    """Get all UNIQUE constraints across all tables"""
    query = """
    SELECT 
        tc.table_schema,
        tc.table_name,
        tc.constraint_name,
        tc.constraint_type,
        string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.table_schema IN ('auth', 'core', 'integrations', 'admin')
    AND tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
    GROUP BY tc.table_schema, tc.table_name, tc.constraint_name, tc.constraint_type
    ORDER BY tc.table_schema, tc.table_name, tc.constraint_type;
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def print_duplication_audit():
    print("=" * 100)
    print("DUPLICATION CHECK AUDIT REPORT")
    print("=" * 100)
    print()
    
    constraints = get_all_unique_constraints()
    
    # Group by table
    by_table = defaultdict(list)
    for row in constraints:
        schema, table = row[0], row[1]
        by_table[(schema, table)].append(row)
    
    print("DATABASE-LEVEL DUPLICATION PREVENTION (Unique Constraints)")
    print("-" * 100)
    print()
    
    for (schema, table), constraints in sorted(by_table.items()):
        unique_constraints = [c for c in constraints if c[3] == 'UNIQUE']
        pk_constraints = [c for c in constraints if c[3] == 'PRIMARY KEY']
        
        print(f"{schema}.{table}")
        
        # Primary keys
        for constraint in pk_constraints:
            print(f"   PK: {constraint[4]}")
        
        # Unique constraints
        if unique_constraints:
            for constraint in unique_constraints:
                print(f"   UNIQUE: {constraint[4]} ({constraint[2]})")
        else:
            print(f"   ⚠️  NO UNIQUE CONSTRAINTS (allows duplicates)")
        
        print()
    
    print()
    print("=" * 100)
    print("CRITICAL FINDINGS & RECOMMENDATIONS")
    print("=" * 100)
    print()
    
    # Analyze specific tables
    tables_without_uniqueness = []
    
    print("TABLES THAT ALLOW DUPLICATE DATA:")
    print()
    
    for (schema, table), constraints in sorted(by_table.items()):
        unique_constraints = [c for c in constraints if c[3] == 'UNIQUE']
        
        if not unique_constraints:
            tables_without_uniqueness.append((schema, table))
            
            # Provide recommendations based on table
            if table == 'dishes':
                print(f"❌ {schema}.{table}")
                print(f"   Issue: Can create multiple dishes with same name for same chef")
                print(f"   Recommendation: Add UNIQUE(chef_id, name)")
                print(f"   Impact: Prevents chef from creating 'Pasta Carbonara' twice")
                print()
                
            elif table == 'clients':
                print(f"❌ {schema}.{table}")
                print(f"   Issue: Can create multiple clients with same email")
                print(f"   Recommendation: Add UNIQUE(email)")
                print(f"   Impact: Ensures email uniqueness across system")
                print()
                
            elif table == 'menus':
                print(f"❌ {schema}.{table}")
                print(f"   Issue: Can create multiple menus with same name for same chef")
                print(f"   Recommendation: Add UNIQUE(chef_id, name)")
                print(f"   Impact: Prevents duplicate menu names per chef")
                print()
                
            elif table == 'ingredients':
                print(f"⚠️  {schema}.{table}")
                print(f"   Issue: Can add same ingredient multiple times to same dish")
                print(f"   Recommendation: Add UNIQUE(dish_id, name)")
                print(f"   Impact: Prevents duplicate ingredients in dish")
                print()
                
            elif table == 'quotations':
                print(f"⚠️  {schema}.{table}")
                print(f"   Note: Multiple quotations for same client/event may be valid")
                print(f"   Recommendation: Consider business logic validation, not DB constraint")
                print()
                
            elif table in ['appointments', 'quotation_items', 'menu_dishes']:
                # These are OK without unique constraints
                pass
            else:
                print(f"ℹ️  {schema}.{table} - No unique constraints")
    
    print()
    print("=" * 100)
    print("RECOMMENDED MIGRATIONS")
    print("=" * 100)
    print()
    
    print("Priority 1: Critical Business Logic")
    print()
    print("-- Prevent duplicate dishes per chef")
    print("ALTER TABLE core.dishes")
    print("  ADD CONSTRAINT dishes_chef_name_unique UNIQUE (chef_id, name);")
    print()
    print("-- Prevent duplicate client emails")
    print("ALTER TABLE core.clients")
    print("  ADD CONSTRAINT clients_email_unique UNIQUE (email);")
    print()
    
    print("Priority 2: Data Quality")
    print()
    print("-- Prevent duplicate ingredients in same dish")
    print("ALTER TABLE core.ingredients")
    print("  ADD CONSTRAINT ingredients_dish_name_unique UNIQUE (dish_id, name);")
    print()
    print("-- Prevent duplicate menus per chef")
    print("ALTER TABLE core.menus")
    print("  ADD CONSTRAINT menus_chef_name_unique UNIQUE (chef_id, name);")
    print()
    
    print()
    print("=" * 100)
    print("APPLICATION-LEVEL VALIDATION NEEDED")
    print("=" * 100)
    print()
    
    print("Even with DB constraints, services should check BEFORE attempting insert:")
    print()
    print("1. DishService.create_dish()")
    print("   → Check if dish with same name exists for chef")
    print("   → Return user-friendly error message")
    print()
    print("2. ClientService.create_client()")
    print("   → Check if client email already exists")
    print("   → Return 'Email already registered' error")
    print()
    print("3. MenuService.create_menu()")
    print("   → Check if menu name exists for chef")
    print("   → Suggest alternative name")
    print()
    
    print()
    print("=" * 100)
    print("END OF AUDIT")
    print("=" * 100)

if __name__ == "__main__":
    try:
        print_duplication_audit()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
