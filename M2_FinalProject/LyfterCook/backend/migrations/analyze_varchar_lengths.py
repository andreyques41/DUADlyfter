"""
VARCHAR Length Inconsistency Analysis
======================================
Detailed analysis of VARCHAR length inconsistencies across tables.
Provide recommendations for standardization.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv('../config/.env')

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

def analyze_varchar_inconsistencies():
    """Analyze VARCHAR length patterns across tables"""
    
    query = """
    SELECT 
        table_schema,
        table_name,
        column_name,
        character_maximum_length,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema IN ('auth', 'core', 'integrations', 'admin')
    AND data_type = 'character varying'
    ORDER BY column_name, table_schema, table_name;
    """
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()

def group_by_column_name(columns):
    """Group columns by name to find inconsistencies"""
    grouped = defaultdict(list)
    for col in columns:
        grouped[col['column_name']].append(col)
    return grouped

def print_analysis():
    print("=" * 100)
    print("VARCHAR LENGTH INCONSISTENCY ANALYSIS")
    print("=" * 100)
    print()
    
    columns = analyze_varchar_inconsistencies()
    grouped = group_by_column_name(columns)
    
    # Find inconsistencies
    inconsistent = {}
    consistent = {}
    
    for col_name, instances in grouped.items():
        if len(instances) > 1:
            lengths = set(c['character_maximum_length'] for c in instances if c['character_maximum_length'])
            if len(lengths) > 1:
                inconsistent[col_name] = instances
            else:
                consistent[col_name] = instances
    
    print("🔍 SECTION 1: INCONSISTENT VARCHAR LENGTHS")
    print("-" * 100)
    print()
    
    if inconsistent:
        for col_name, instances in sorted(inconsistent.items()):
            lengths = sorted(set(c['character_maximum_length'] for c in instances if c['character_maximum_length']))
            
            print(f"❌ Column: '{col_name}' - {len(instances)} tables, {len(lengths)} different lengths: {lengths}")
            print()
            
            for inst in instances:
                print(f"   {inst['table_schema']}.{inst['table_name']:<30} → VARCHAR({inst['character_maximum_length']})")
            
            # Analyze usage context
            print()
            print(f"   📊 ANALYSIS:")
            
            # Check actual data
            for inst in instances:
                check_query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    MAX(LENGTH({inst['column_name']})) as max_length,
                    AVG(LENGTH({inst['column_name']}))::int as avg_length,
                    MIN(LENGTH({inst['column_name']})) as min_length
                FROM {inst['table_schema']}.{inst['table_name']}
                WHERE {inst['column_name']} IS NOT NULL;
                """
                
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    try:
                        cur.execute(check_query)
                        stats = cur.fetchone()
                        if stats and stats['total_rows'] > 0:
                            print(f"      {inst['table_schema']}.{inst['table_name']}:")
                            print(f"         Rows: {stats['total_rows']}, "
                                  f"Max used: {stats['max_length']}, "
                                  f"Avg: {stats['avg_length']}, "
                                  f"Min: {stats['min_length']}")
                        else:
                            print(f"      {inst['table_schema']}.{inst['table_name']}: No data yet")
                    except Exception as e:
                        print(f"      {inst['table_schema']}.{inst['table_name']}: Could not analyze - {e}")
            
            print()
            print(f"   💡 RECOMMENDATION:")
            
            # Make recommendation based on context
            if col_name == 'unit':
                print(f"      Standard unit abbreviations are typically short: 'kg', 'lbs', 'ml'")
                print(f"      RECOMMENDED: VARCHAR(50) for flexibility (allows longer units like 'tablespoons')")
                print(f"      IMPACT: Low - simple ALTER COLUMN")
                
            elif col_name in ['ingredient_name', 'product_name']:
                print(f"      Product/ingredient names vary widely in length")
                print(f"      RECOMMENDED: VARCHAR(200) as reasonable balance")
                print(f"      RATIONALE: Covers 99% of cases, not excessive")
                print(f"      IMPACT: Medium - may need to verify no data exceeds new limit")
            
            else:
                # Generic recommendation
                max_length = max(lengths)
                print(f"      RECOMMENDED: Use maximum found: VARCHAR({max_length})")
                print(f"      RATIONALE: Accommodate all current use cases")
            
            print()
            print("-" * 100)
            print()
    
    else:
        print("✅ No VARCHAR length inconsistencies found!")
    
    print()
    print("📋 SECTION 2: CONSISTENT MULTI-TABLE VARCHAR COLUMNS")
    print("-" * 100)
    print()
    
    for col_name, instances in sorted(consistent.items()):
        if len(instances) > 1:
            length = instances[0]['character_maximum_length']
            print(f"✅ '{col_name}' → VARCHAR({length}) in {len(instances)} tables (consistent)")
    
    print()
    print("=" * 100)
    print("SUMMARY & ACTION PLAN")
    print("=" * 100)
    print()
    
    if inconsistent:
        print(f"Found {len(inconsistent)} inconsistent column names across tables:")
        print()
        
        for col_name in sorted(inconsistent.keys()):
            instances = inconsistent[col_name]
            lengths = sorted(set(c['character_maximum_length'] for c in instances if c['character_maximum_length']))
            print(f"   • {col_name}: {lengths}")
        
        print()
        print("🎯 RECOMMENDED ACTIONS:")
        print()
        print("1. UNIT column:")
        print("   • Standardize to VARCHAR(50)")
        print("   • Tables: core.ingredients, integrations.scraped_prices")
        print()
        print("2. INGREDIENT_NAME column:")
        print("   • Standardize to VARCHAR(200)")
        print("   • Tables: integrations.scraped_prices, integrations.scraped_products")
        print()
        print("3. PRODUCT_NAME column:")
        print("   • Standardize to VARCHAR(300) or VARCHAR(200)")
        print("   • Decide based on actual data usage")
        print("   • Tables: integrations.scraped_prices, integrations.scraped_products")
        print()
        print("PRIORITY: MEDIUM")
        print("RISK: LOW (only affects scraper/integration tables)")
        print("IMPACT: Improves schema consistency and maintainability")
        
    else:
        print("✅ All VARCHAR columns are consistent!")
    
    print()
    print("=" * 100)

if __name__ == "__main__":
    try:
        print_analysis()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
