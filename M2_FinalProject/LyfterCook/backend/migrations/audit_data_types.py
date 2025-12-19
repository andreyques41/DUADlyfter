"""
COMPREHENSIVE DATABASE TYPE AUDIT
==================================
Professional audit of data type consistency across all tables.
Focus: Boolean/Integer inconsistencies and other type patterns.

Author: Backend Engineering Team
Date: 2025-12-19
"""

import psycopg2
from psycopg2.extras import RealDictCursor
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

def get_all_columns_with_types():
    """Get ALL columns with their full type information"""
    query = """
    SELECT 
        table_schema,
        table_name,
        column_name,
        data_type,
        udt_name,
        is_nullable,
        column_default,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        ordinal_position
    FROM information_schema.columns
    WHERE table_schema IN ('auth', 'core', 'integrations', 'admin')
    ORDER BY table_schema, table_name, ordinal_position;
    """
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()

def get_boolean_like_columns():
    """Get columns that are boolean-like (by type or name)"""
    query = """
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
        OR data_type = 'integer' AND (
            column_name LIKE 'is_%'
            OR column_name LIKE '%_active'
            OR column_name LIKE '%_enabled'
            OR column_name LIKE '%_verified'
            OR column_name LIKE '%_optional'
            OR column_name LIKE '%_deleted'
            OR column_name LIKE '%_approved'
            OR column_name LIKE '%_confirmed'
        )
    )
    ORDER BY table_schema, table_name, column_name;
    """
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()

def analyze_type_patterns(columns):
    """Analyze patterns and inconsistencies in data types"""
    
    # Group by column name pattern
    patterns = defaultdict(list)
    
    for col in columns:
        # Identify pattern
        if col['column_name'].startswith('is_'):
            pattern = 'is_*'
        elif col['column_name'].endswith('_active'):
            pattern = '*_active'
        elif col['column_name'].endswith('_enabled'):
            pattern = '*_enabled'
        elif col['column_name'].endswith('_optional'):
            pattern = '*_optional'
        elif col['column_name'].endswith('_verified'):
            pattern = '*_verified'
        else:
            pattern = 'other_boolean'
        
        patterns[pattern].append(col)
    
    return patterns

def print_audit_report():
    """Generate comprehensive audit report"""
    
    print("=" * 100)
    print("DATABASE TYPE AUDIT REPORT")
    print("=" * 100)
    print()
    
    # Section 1: Boolean-like columns
    print("📊 SECTION 1: BOOLEAN-LIKE COLUMNS INVENTORY")
    print("-" * 100)
    
    boolean_cols = get_boolean_like_columns()
    
    # Separate by type
    actual_booleans = [c for c in boolean_cols if c['data_type'] == 'boolean']
    integer_booleans = [c for c in boolean_cols if c['data_type'] == 'integer']
    
    print(f"\n✅ TRUE BOOLEAN COLUMNS ({len(actual_booleans)} found):")
    print(f"{'Schema':<15} {'Table':<25} {'Column':<30} {'Nullable':<10} {'Default'}")
    print("-" * 100)
    for col in actual_booleans:
        print(f"{col['table_schema']:<15} {col['table_name']:<25} {col['column_name']:<30} "
              f"{col['is_nullable']:<10} {col['column_default'] or 'NULL'}")
    
    print(f"\n⚠️  INTEGER-AS-BOOLEAN COLUMNS ({len(integer_booleans)} found):")
    print(f"{'Schema':<15} {'Table':<25} {'Column':<30} {'Nullable':<10} {'Default'}")
    print("-" * 100)
    for col in integer_booleans:
        print(f"{col['table_schema']:<15} {col['table_name']:<25} {col['column_name']:<30} "
              f"{col['is_nullable']:<10} {col['column_default'] or 'NULL'}")
    
    # Section 2: Pattern Analysis
    print("\n\n📈 SECTION 2: PATTERN-BASED INCONSISTENCY ANALYSIS")
    print("-" * 100)
    
    patterns = analyze_type_patterns(boolean_cols)
    
    for pattern, cols in patterns.items():
        print(f"\n🔍 Pattern: {pattern}")
        
        # Check consistency
        types = set(c['data_type'] for c in cols)
        
        if len(types) > 1:
            print(f"   ❌ INCONSISTENT - Uses {len(types)} different types: {', '.join(types)}")
            
            # Show breakdown
            for dtype in types:
                matching = [c for c in cols if c['data_type'] == dtype]
                print(f"\n   Type: {dtype.upper()}")
                for c in matching:
                    print(f"      • {c['table_schema']}.{c['table_name']}.{c['column_name']}")
        else:
            print(f"   ✅ CONSISTENT - All use {list(types)[0].upper()}")
    
    # Section 3: Specific Column Name Analysis
    print("\n\n🔎 SECTION 3: SPECIFIC COLUMN NAME ANALYSIS")
    print("-" * 100)
    
    # Group by exact column name
    by_name = defaultdict(list)
    for col in boolean_cols:
        by_name[col['column_name']].append(col)
    
    for col_name, instances in sorted(by_name.items()):
        if len(instances) > 1:
            types = set(c['data_type'] for c in instances)
            
            if len(types) > 1:
                print(f"\n❌ INCONSISTENT: '{col_name}' appears in {len(instances)} tables with {len(types)} types:")
                for inst in instances:
                    print(f"   • {inst['table_schema']}.{inst['table_name']} → {inst['data_type'].upper()}")
            else:
                print(f"\n✅ CONSISTENT: '{col_name}' → {list(types)[0].upper()} ({len(instances)} tables)")
    
    # Section 4: Recommendations
    print("\n\n💡 SECTION 4: PROFESSIONAL RECOMMENDATIONS")
    print("-" * 100)
    
    print("\n🎯 CRITICAL FINDINGS:\n")
    
    # Count inconsistencies
    inconsistent_patterns = sum(1 for p, cols in patterns.items() 
                               if len(set(c['data_type'] for c in cols)) > 1)
    
    if integer_booleans:
        print(f"1. BOOLEAN vs INTEGER INCONSISTENCY:")
        print(f"   • {len(actual_booleans)} columns use native BOOLEAN type")
        print(f"   • {len(integer_booleans)} columns use INTEGER type for boolean values")
        print(f"   • This creates:")
        print(f"     - Code complexity (need to handle both True/False AND 1/0)")
        print(f"     - Type safety issues")
        print(f"     - API inconsistency")
        print(f"     - Potential bugs in boolean comparisons")
        print()
    
    if inconsistent_patterns > 0:
        print(f"2. PATTERN INCONSISTENCY:")
        print(f"   • {inconsistent_patterns} naming patterns have mixed types")
        print(f"   • This violates principle of least surprise")
        print()
    
    print("\n📋 RECOMMENDED STANDARD:\n")
    print("   Option A: PostgreSQL Best Practice (RECOMMENDED)")
    print("   ✅ Use native BOOLEAN type for all boolean columns")
    print("   ✅ Benefits:")
    print("      - Native database constraint checking")
    print("      - Clear intent in schema")
    print("      - Better query optimization")
    print("      - Standard SQL compliance")
    print("      - Works seamlessly with SQLAlchemy Boolean type")
    print("      - JSON serialization is straightforward (true/false)")
    print()
    print("   Option B: Integer Standard")
    print("   ⚠️  Use INTEGER(0/1) for all boolean columns")
    print("   ⚠️  Only if legacy compatibility required")
    print("   ⚠️  Drawbacks:")
    print("      - Non-standard (can store 2, 3, -1, etc.)")
    print("      - Requires application-level validation")
    print("      - Confusing for new developers")
    print()
    
    print("\n🔧 MIGRATION STRATEGY:\n")
    print("   1. Identify all INTEGER-as-boolean columns")
    print("   2. Create migration to ALTER COLUMN type to BOOLEAN")
    print("   3. Update SQLAlchemy models (Integer → Boolean)")
    print("   4. Test all affected endpoints")
    print("   5. Deploy with zero-downtime strategy")
    print()
    
    # Section 5: Other Type Issues
    print("\n📊 SECTION 5: OTHER TYPE PATTERNS")
    print("-" * 100)
    
    all_cols = get_all_columns_with_types()
    
    # Group by data type
    type_counts = defaultdict(int)
    for col in all_cols:
        type_counts[col['data_type']] += 1
    
    print("\nData Type Distribution:")
    for dtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"   {dtype:<30} {count:>5} columns")
    
    # Check for other inconsistencies
    print("\n\n🔍 Checking for other common inconsistencies...")
    
    # String length inconsistencies
    string_cols = defaultdict(list)
    for col in all_cols:
        if col['data_type'] == 'character varying':
            key = f"{col['column_name']}"
            string_cols[key].append(col)
    
    print("\n   VARCHAR Length Inconsistencies:")
    found_issues = False
    for col_name, instances in string_cols.items():
        if len(instances) > 1:
            lengths = set(c['character_maximum_length'] for c in instances)
            if len(lengths) > 1 and None not in lengths:
                found_issues = True
                print(f"   ⚠️  '{col_name}' has varying lengths: {sorted(lengths)}")
                for inst in instances:
                    print(f"      • {inst['table_schema']}.{inst['table_name']} → VARCHAR({inst['character_maximum_length']})")
    
    if not found_issues:
        print("   ✅ No significant VARCHAR length inconsistencies")
    
    print("\n" + "=" * 100)
    print("END OF AUDIT REPORT")
    print("=" * 100)

if __name__ == "__main__":
    try:
        print_audit_report()
    except Exception as e:
        print(f"❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
