"""Script to check the actual database schema"""
from app import create_app
from app.core.database import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('quotations', schema='core')
    
    print('\nCurrent columns in core.quotations:')
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    print('\n')
