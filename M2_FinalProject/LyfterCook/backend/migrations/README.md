# Database Migrations

Este directorio contiene las migraciones SQL para el proyecto.

## Ejecutar Migraciones

### Opción 1: PostgreSQL CLI (psql)

```bash
psql -U postgres -d lyfter_cook -f migrations/001_create_admin_audit_logs.sql
```

### Opción 2: pgAdmin

1. Abrir pgAdmin
2. Conectar a la base de datos `lyfter_cook`
3. Tools → Query Tool
4. Abrir el archivo SQL
5. Ejecutar (F5)

### Opción 3: Desde Python

```python
from config.database import db

with open('migrations/001_create_admin_audit_logs.sql') as f:
    sql = f.read()
    db.session.execute(sql)
    db.session.commit()
```

## Verificar Migración

```sql
-- Verificar que la tabla existe
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'core' 
  AND table_name = 'admin_audit_logs';

-- Ver estructura de la tabla
\d core.admin_audit_logs

-- Ver índices
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'admin_audit_logs' 
  AND schemaname = 'core';
```

## Rollback

Si necesitas revertir la migración:

```sql
DROP TABLE IF EXISTS core.admin_audit_logs CASCADE;
```

## Orden de Ejecución

Las migraciones deben ejecutarse en orden numérico:
1. `001_create_admin_audit_logs.sql` - Tabla de audit logs
