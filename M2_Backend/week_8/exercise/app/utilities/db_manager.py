from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.utilities.base_model import Base, User, Product, Invoice, InvoiceItem, Role, set_schema


class DBManager:
    """Database manager for handling connections, schema, and table creation using ORM."""
    
    def __init__(self, db_uri=None, schema=None, echo=False):
        """
        Initialize the database manager.
        
        Args:
            db_uri: Database connection URI (default: PostgreSQL localhost)
            schema: Database schema name (default: backend_week7)
            echo: Whether to log SQL queries (default: False)
        """
        self.db_uri = db_uri or 'postgresql://postgres:postgres@localhost:5432/lyfter'
        self.schema = schema or 'backend_week7'
        self.echo = echo
        
        # Set the global schema for all models BEFORE creating engine
        set_schema(self.schema)
        
        self.engine = create_engine(self.db_uri, echo=self.echo)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self) -> Session:
        """
        Get a new database session for ORM operations.
        
        Returns:
            SQLAlchemy Session object
            
        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).filter_by(username='john').first()
        """
        return self.SessionLocal()

    def create_all_tables(self):
        """
        Auto-discover and create all tables defined in models.
        No manual registration needed - Base.metadata finds all models automatically!
        """
        try:
            # Test connection
            with self.engine.connect() as connection:
                print("✅ Database connection successful!")
            
            print("Creating tables...")
            
            # Auto-discover and create ALL tables that inherit from Base
            Base.metadata.create_all(self.engine)
            
            # Get list of created tables
            table_names = [table.name for table in Base.metadata.sorted_tables]
            
            print("\n🎉 Tables created successfully!")
            print(f"- {', '.join(table_names)}")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise

    def get_engine(self):
        """Get the database engine."""
        return self.engine
    
    def get_metadata(self):
        """Get the Base metadata (contains all registered models)."""
        return Base.metadata
