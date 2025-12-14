"""
Database Migration Script
Ejecuta las migraciones SQL de forma segura
"""
import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from config.logging import get_logger

logger = get_logger(__name__)


def run_migration(migration_file: str):
    """
    Ejecutar un archivo de migración SQL
    
    Args:
        migration_file: Nombre del archivo SQL en migrations/
    """
    migration_path = backend_path / 'migrations' / migration_file
    
    if not migration_path.exists():
        print(f"❌ Error: Archivo {migration_file} no encontrado")
        return False
    
    db = None
    try:
        # Initialize database connection
        from app.core.database import init_db
        init_db()
        
        # Import SessionLocal after init_db() has been called
        from app.core.database import SessionLocal
        
        if SessionLocal is None:
            raise RuntimeError("Failed to initialize database. SessionLocal is None.")
        
        # Create a new database session
        db = SessionLocal()
        
        # Read SQL file
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print(f"📋 Ejecutando migración: {migration_file}")
        
        # Execute SQL
        db.execute(text(sql))
        db.commit()
        
        print(f"✅ Migración {migration_file} ejecutada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando migración: {str(e)}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()


def verify_table():
    """Verificar que la tabla fue creada"""
    db = None
    try:
        from app.core.database import SessionLocal
        
        if SessionLocal is None:
            print("❌ Error: SessionLocal no inicializado")
            return False
        
        db = SessionLocal()
        
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'core' 
              AND table_name = 'admin_audit_logs'
        """))
        
        if result.fetchone():
            print("✅ Tabla core.admin_audit_logs existe")
            
            # Check indexes
            result = db.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'admin_audit_logs' 
                  AND schemaname = 'core'
            """))
            
            indexes = result.fetchall()
            print(f"📊 Índices creados: {len(indexes)}")
            for idx in indexes:
                print(f"   - {idx[0]}")
            
            return True
        else:
            print("❌ Tabla no encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {str(e)}")
        return False
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    print("🚀 Iniciando migración de base de datos...\n")
    
    # Run migration
    success = run_migration('001_create_admin_audit_logs.sql')
    
    if success:
        print("\n🔍 Verificando migración...")
        verify_table()
        print("\n✨ Proceso completado")
    else:
        print("\n❌ Migración falló")
        sys.exit(1)
