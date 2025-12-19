"""
Compare all SQLAlchemy models with actual database schema
This script checks for mismatches between models and database tables
"""
import psycopg2
import os
import sys
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

# Define all tables to check with their schema
TABLES_TO_CHECK = [
    ('auth', 'users'),
    # ('auth', 'refresh_tokens'),  # Not implemented in database yet
    ('core', 'chefs'),
    ('core', 'clients'),
    ('core', 'dishes'),
    ('core', 'ingredients'),
    ('core', 'menus'),
    ('core', 'menu_dishes'),
    ('core', 'quotations'),
    ('core', 'quotation_items'),
    ('integrations', 'appointments'),
    ('integrations', 'price_sources'),
    # ('admin', 'audit_logs'),  # Not implemented in database yet
]

def get_table_columns(cursor, schema, table):
    """Get all columns for a table from database"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = %s 
          AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table))
    return cursor.fetchall()

def get_model_columns(schema, table):
    """Get expected columns from SQLAlchemy model"""
    model_map = {
        ('auth', 'users'): 'app.auth.models.user_model.User',
        ('auth', 'refresh_tokens'): 'app.auth.models.refresh_token_model.RefreshToken',
        ('core', 'chefs'): 'app.chefs.models.chef_model.Chef',
        ('core', 'clients'): 'app.clients.models.client_model.Client',
        ('core', 'dishes'): 'app.dishes.models.dish_model.Dish',
        ('core', 'ingredients'): 'app.dishes.models.ingredient_model.Ingredient',
        ('core', 'menus'): 'app.menus.models.menu_model.Menu',
        ('core', 'menu_dishes'): 'app.menus.models.menu_dish_model.MenuDish',
        ('core', 'quotations'): 'app.quotations.models.quotation_model.Quotation',
        ('core', 'quotation_items'): 'app.quotations.models.quotation_item_model.QuotationItem',
        ('integrations', 'appointments'): 'app.appointments.models.appointment_model.Appointment',
        ('integrations', 'scraped_products'): 'app.scrapers.models.scraped_product_model.ScrapedProduct',
        ('integrations', 'price_sources'): 'app.scrapers.models.price_source_model.PriceSource',
        ('admin', 'audit_logs'): 'app.admin.models.audit_log_model.AuditLog',
    }
    
    model_path = model_map.get((schema, table))
    if not model_path:
        return []
    
    try:
        # Import the model
        module_path, class_name = model_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        model_class = getattr(module, class_name)
        
        # Get columns from model
        columns = []
        for column in model_class.__table__.columns:
            columns.append(column.name)
        return sorted(columns)
    except Exception as e:
        print(f"    ⚠️ Could not import model: {e}")
        return []

def main():
    try:
        # Connect to database
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
        print("COMPARING ALL MODELS WITH DATABASE SCHEMA")
        print("="*80)
        
        all_issues = []
        
        for schema, table in TABLES_TO_CHECK:
            print(f"\n📋 {schema}.{table}")
            print("-" * 60)
            
            # Get database columns
            db_columns = get_table_columns(cursor, schema, table)
            
            if not db_columns:
                print(f"    ❌ Table does not exist in database!")
                all_issues.append(f"{schema}.{table}: TABLE NOT FOUND")
                continue
            
            db_column_names = set([col[0] for col in db_columns])
            
            # Get model columns
            model_columns = get_model_columns(schema, table)
            model_column_names = set(model_columns)
            
            if not model_columns:
                print(f"    ⚠️ Could not load model")
                continue
            
            # Compare
            only_in_db = db_column_names - model_column_names
            only_in_model = model_column_names - db_column_names
            in_both = db_column_names & model_column_names
            
            if only_in_db or only_in_model:
                print(f"    ❌ MISMATCH FOUND!")
                
                if only_in_db:
                    print(f"    🔴 In DB but NOT in model: {sorted(only_in_db)}")
                    all_issues.append(f"{schema}.{table}: Missing in model: {sorted(only_in_db)}")
                
                if only_in_model:
                    print(f"    🔴 In model but NOT in DB: {sorted(only_in_model)}")
                    all_issues.append(f"{schema}.{table}: Extra in model: {sorted(only_in_model)}")
                
                print(f"    ✓ Matching columns ({len(in_both)}): {sorted(in_both)}")
            else:
                print(f"    ✅ PERFECT MATCH! All {len(db_column_names)} columns match")
            
            # Show DB schema details
            if only_in_db:
                print(f"\n    DB Schema for missing columns:")
                for col in db_columns:
                    if col[0] in only_in_db:
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        default = f" DEFAULT {col[3]}" if col[3] else ""
                        print(f"      - {col[0]}: {col[1]} {nullable}{default}")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        if all_issues:
            print(f"\n❌ Found {len(all_issues)} issues:\n")
            for issue in all_issues:
                print(f"  • {issue}")
            print("\n⚠️ Models need to be updated to match database schema!")
        else:
            print("\n✅ ALL MODELS MATCH DATABASE SCHEMA PERFECTLY!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
