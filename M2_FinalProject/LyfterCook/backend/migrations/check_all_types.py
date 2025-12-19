"""
Comprehensive check of ALL column types in database vs SQLAlchemy models
This will catch ANY type mismatch, not just booleans
"""
import psycopg2
import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from sqlalchemy import inspect

# Import all models
from app.auth.models.user_model import User
from app.chefs.models.chef_model import Chef
from app.clients.models.client_model import Client
from app.dishes.models.dish_model import Dish
from app.dishes.models.ingredient_model import Ingredient
from app.menus.models.menu_model import Menu
from app.menus.models.menu_dish_model import MenuDish
from app.quotations.models.quotation_model import Quotation
from app.quotations.models.quotation_item_model import QuotationItem
from app.appointments.models.appointment_model import Appointment
from app.scrapers.models.price_source_model import PriceSource

# Map PostgreSQL types to SQLAlchemy types
TYPE_MAPPINGS = {
    'integer': ['INTEGER', 'Integer', 'SMALLINT', 'BIGINT'],
    'bigint': ['BIGINT', 'BigInteger'],
    'smallint': ['SMALLINT', 'SmallInteger'],
    'character varying': ['VARCHAR', 'String'],
    'text': ['TEXT', 'Text'],
    'numeric': ['NUMERIC', 'Numeric'],
    'boolean': ['BOOLEAN', 'Boolean'],
    'timestamp without time zone': ['DATETIME', 'DateTime'],
    'timestamp with time zone': ['DATETIME', 'DateTime'],
    'date': ['DATE', 'Date'],
    'time without time zone': ['TIME', 'Time'],
    'USER-DEFINED': ['Enum', 'String'],  # Enums often show as USER-DEFINED
}

def normalize_db_type(db_type):
    """Normalize database type for comparison"""
    return db_type.lower().replace(' ', '')

def get_sqlalchemy_type(column):
    """Get normalized SQLAlchemy type name"""
    col_type = str(column.type)
    # Extract base type (e.g., "VARCHAR(100)" -> "VARCHAR")
    if '(' in col_type:
        col_type = col_type.split('(')[0]
    return col_type.upper()

def types_are_compatible(db_type, sa_type):
    """Check if database type and SQLAlchemy type are compatible"""
    db_type_lower = db_type.lower()
    
    # Direct match
    if db_type_lower in TYPE_MAPPINGS:
        return sa_type in TYPE_MAPPINGS[db_type_lower]
    
    # Special cases
    if 'int' in db_type_lower and 'INT' in sa_type:
        return True
    if 'char' in db_type_lower and sa_type in ['VARCHAR', 'STRING', 'CHAR']:
        return True
    if db_type_lower == 'text' and sa_type in ['TEXT', 'STRING']:
        return True
    
    return False

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
        print("COMPREHENSIVE TYPE CHECK: DATABASE vs MODELS")
        print("="*80)
        
        # Get all tables
        cursor.execute("""
            SELECT DISTINCT table_schema, table_name
            FROM information_schema.columns 
            WHERE table_schema IN ('auth', 'core', 'integrations', 'admin')
            ORDER BY table_schema, table_name
        """)
        
        all_tables = cursor.fetchall()
        
        models = {
            ('auth', 'users'): User,
            ('core', 'chefs'): Chef,
            ('core', 'clients'): Client,
            ('core', 'dishes'): Dish,
            ('core', 'ingredients'): Ingredient,
            ('core', 'menus'): Menu,
            ('core', 'menu_dishes'): MenuDish,
            ('core', 'quotations'): Quotation,
            ('core', 'quotation_items'): QuotationItem,
            ('integrations', 'appointments'): Appointment,
            ('integrations', 'price_sources'): PriceSource,
        }
        
        all_issues = []
        
        for schema, table in all_tables:
            model = models.get((schema, table))
            if not model:
                continue
            
            print(f"\n📋 {schema}.{table}")
            print("-" * 60)
            
            # Get DB columns
            cursor.execute("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, table))
            
            db_columns = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
            
            # Get model columns
            model_columns = {}
            for column in model.__table__.columns:
                model_columns[column.name] = column
            
            # Compare each column
            type_mismatches = []
            
            for col_name in db_columns:
                if col_name not in model_columns:
                    continue
                
                db_type, udt_name = db_columns[col_name]
                sa_column = model_columns[col_name]
                sa_type = get_sqlalchemy_type(sa_column)
                
                # Check compatibility
                if not types_are_compatible(db_type, sa_type):
                    # Special check for boolean/integer mismatch
                    if (db_type == 'integer' and sa_type == 'BOOLEAN') or \
                       (db_type == 'boolean' and sa_type == 'INTEGER'):
                        type_mismatches.append({
                            'column': col_name,
                            'db_type': db_type,
                            'model_type': sa_type,
                            'severity': 'HIGH'
                        })
                        print(f"   ❌ {col_name}: DB={db_type} but Model={sa_type} (CRITICAL MISMATCH)")
                    elif db_type == 'USER-DEFINED':
                        # Enum types - usually OK
                        print(f"   ⚠️  {col_name}: DB=ENUM({udt_name}) Model={sa_type}")
                    else:
                        type_mismatches.append({
                            'column': col_name,
                            'db_type': db_type,
                            'model_type': sa_type,
                            'severity': 'MEDIUM'
                        })
                        print(f"   ⚠️  {col_name}: DB={db_type} but Model={sa_type}")
            
            if type_mismatches:
                all_issues.extend([{**m, 'table': f"{schema}.{table}"} for m in type_mismatches])
            else:
                print(f"   ✅ All column types match perfectly")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        if all_issues:
            high_priority = [i for i in all_issues if i.get('severity') == 'HIGH']
            medium_priority = [i for i in all_issues if i.get('severity') == 'MEDIUM']
            
            if high_priority:
                print(f"\n🚨 CRITICAL: {len(high_priority)} high-priority type mismatches:")
                for issue in high_priority:
                    print(f"   • {issue['table']}.{issue['column']}: {issue['db_type']} vs {issue['model_type']}")
            
            if medium_priority:
                print(f"\n⚠️  WARNING: {len(medium_priority)} medium-priority type mismatches:")
                for issue in medium_priority:
                    print(f"   • {issue['table']}.{issue['column']}: {issue['db_type']} vs {issue['model_type']}")
        else:
            print("\n✅ ALL COLUMN TYPES ARE COMPATIBLE!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
