# 🍳 LyfterCook Backend

REST API para la plataforma LyfterCook - Gestión integral para chefs profesionales.

## 🚀 Quick Start

### Prerrequisitos
- Python 3.11+
- PostgreSQL 15+
- pip

### Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp config/.env.example config/.env
# Editar config/.env con tus valores

# 5. Crear base de datos
psql -U postgres
CREATE DATABASE lyftercook;
\q

# 6. Inicializar base de datos
python scripts/init_db.py

# 7. Crear usuario administrador
python scripts/seed_admin.py

# 8. Ejecutar aplicación
python run.py
```

El servidor estará disponible en `http://localhost:5000`

## 🔐 Seguridad - Usuario Administrador

### Crear Admin Inicial

Ejecuta el script de seeding para crear el usuario administrador:

```bash
python scripts/seed_admin.py
```

Credenciales por defecto (configurables en `.env`):
- Username: `admin`
- Email: `admin@lyftercook.com`  
- Password: `Admin123!@#`

⚠️ **IMPORTANTE: Cambia la contraseña después del primer login**

### Política de Roles

- **Registro público** (`POST /auth/register`): Solo crea usuarios tipo `CHEF`
- El parámetro `role` en registro público es **IGNORADO** por seguridad
- Solo admins pueden crear otros admins (endpoint protegido)
- Si pierdes las credenciales del admin:
  1. Actualiza `.env` con nuevas credenciales
  2. Elimina el usuario admin de la base de datos
  3. Ejecuta `python scripts/seed_admin.py` nuevamente

### 🚨 Seguridad en Producción

**Ambiente de Desarrollo (Actual):**
- Script `seed_admin.py` es aceptable
- Credenciales por defecto OK para testing local
- Focus en desarrollo rápido

**Ambiente de Staging:**
- Ejecutar seed script UNA VEZ durante setup inicial
- Cambiar contraseña inmediatamente después del primer login
- Crear segunda cuenta admin como respaldo
- Probar procedimientos de recuperación de credenciales

**Ambiente de Producción:**

1. **Setup Inicial**
   - Ejecutar seed script con credenciales fuertes
   - Guardar credenciales en vault seguro (LastPass, 1Password)
   - Cambiar contraseña inmediatamente después del primer login
   - Crear 2-3 cuentas admin adicionales
   - **ELIMINAR script seed_admin.py del servidor de producción**

2. **Features de Seguridad Requeridas** (A implementar)
   - ⏳ Sistema de recuperación por email
   - ⏳ Códigos de recuperación (backup 2FA)
   - ⏳ Endpoint admin-only para crear usuarios admin
   - ⏳ Multi-factor authentication (MFA) para admins
   - ⏳ Audit logging de todas las acciones admin

3. **Recuperación de Credenciales Perdidas**
   
   **Prioridad de métodos:**
   - 🥇 **Email Recovery**: POST /auth/forgot-password (primary)
   - 🥈 **Recovery Codes**: Códigos one-time generados durante creación admin
   - 🥉 **Otro Admin**: Múltiples admins pueden resetear contraseñas entre sí
   - 🔧 **Acceso a DB**: Último recurso, requiere acceso directo a base de datos

4. **Prevención de Ataques**
   
   **Actualmente Implementado:**
   - ✅ Parámetro `role` ignorado en registro público
   - ✅ Role hardcodeado a CHEF en `auth_service.py`
   - ✅ Seed script usa variables de entorno
   
   **Requerimientos de Producción:**
   - ⏳ Eliminar seed script de deployment
   - ⏳ MFA obligatorio para cuentas admin
   - ⏳ Rate limiting en endpoints de auth
   - ⏳ Audit logs (quién, qué, cuándo, IP)
   - ⏳ Monitoreo de intentos de login fallidos
   - ⏳ Alertas automáticas para actividad admin sospechosa

**📚 Basado en estándares de industria**: Django, Rails, WordPress, Auth0, AWS IAM, GitHub, OWASP/NIST

Ver `docs/PROJECT_PLAN.md` sección "Production Security Strategy" para el plan completo de implementación en fases.

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── auth/          # Autenticación y usuarios
│   ├── chefs/         # Perfiles de chefs
│   ├── clients/       # Gestión de clientes
│   ├── dishes/        # CRUD de platillos
│   ├── menus/         # CRUD de menús
│   ├── quotations/    # Cotizaciones y PDFs
│   ├── appointments/  # Sistema de citas
│   ├── scrapers/      # Scraper de productos
│   ├── public/        # Endpoints públicos
│   ├── admin/         # 👑 Endpoints admin
│   └── core/          # Database, utils, middleware
├── config/            # Configuración
├── tests/             # Tests organizados
│   ├── conftest.py    # Fixtures compartidas
│   ├── setup_test_db.py
│   ├── TESTING_GUIDE.md
│   ├── unit/          # ✅ 113 tests (100%)
│   │   ├── README.md
│   │   ├── test_auth.py
│   │   ├── test_appointments.py
│   │   ├── test_chefs.py
│   │   ├── test_clients.py
│   │   ├── test_dishes.py
│   │   ├── test_menus.py
│   │   ├── test_quotations.py
│   │   ├── test_scrapers.py
│   │   ├── test_public.py
│   │   ├── test_admin.py
│   │   └── test_helpers.py
│   └── integration/   # ✅ Integration tests (1 scenario)
│       └── README.md
└── scripts/           # Scripts de utilidad
    ├── init_db.py
    └── seed_admin.py
```

## 🔧 Configuración

Ver `config/.env.example` para todas las variables disponibles.

Variables esenciales:
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`
- `JWT_SECRET_KEY`
- `CLOUDINARY_*` (para imágenes)
- `SENDGRID_API_KEY` (para emails)

## 📚 Documentación

### Principal
- [Plan del Proyecto](../docs/PROJECT_PLAN.md) - Arquitectura completa y roadmap
- [API Documentation](../docs/API_DOCUMENTATION.md) - Documentación de 60 endpoints implementados
- [Admin Module Design](docs/ADMIN_ENDPOINTS_DESIGN.md) - 👑 Diseño e implementación de endpoints admin (esencial)
- [Guía de Testing](tests/TESTING_GUIDE.md) - Cómo ejecutar y escribir tests (110 tests)
- [Schema Migration](../docs/SCHEMA_MIGRATION.md) - Detalles de base de datos
- [Cache Implementation](docs/CACHE_IMPLEMENTATION.md) - Sistema de caché Redis
- [Chef Endpoints Testing](docs/CHEF_ENDPOINTS_TESTING.md) - Validación de endpoints chef

### Tests
- [Unit Tests](tests/unit/README.md) - 93 tests unitarios
- [Integration Tests](tests/integration/README.md) - Tests de integración (workflows)

## 🎭 Roles y Permisos

### Role-Based Access Control (RBAC)

```
👑 ADMIN
├─ Dashboard con estadísticas globales
├─ Ver/gestionar TODOS los chefs del sistema
├─ Activar/desactivar cuentas
├─ Gestión completa de usuarios
├─ Reportes y análisis del sistema
├─ Audit logs de acciones admin
└─ NO puede crear platillos/menús (necesita chef profile)

👨‍🍳 CHEF
├─ CRUD de su propio perfil
├─ CRUD de sus clientes
├─ CRUD de sus platillos
├─ CRUD de sus menús
├─ CRUD de sus cotizaciones
├─ CRUD de sus citas
├─ Web scraping de precios
└─ NO puede ver/modificar datos de otros chefs

🌐 PUBLIC (sin autenticación)
├─ Ver catálogo de chefs
├─ Buscar chefs por especialidad/ubicación
├─ Ver menús públicos
├─ Ver platillos públicos
└─ Solo lectura
```

**Implementación:**
```python
# Chef endpoint
@jwt_required
def chef_endpoint():
    # Solo ve sus propios datos
    pass

# Admin endpoint
@jwt_required
@admin_required
def admin_endpoint():
    # Ve todos los datos del sistema
    pass
```

**Estado Actual:**
- ✅ Auth Module: 3 endpoints (register, login, me)
- ✅ Chef Module: 5 endpoints (profile CRUD + public list)
- ✅ 7 módulos Chef más: 42 endpoints
- ✅ Public Module: 6 endpoints
- 📝 Admin Module: 8 endpoints (diseñados, no implementados)

## 📊 Estado del Proyecto

### ✅ Completado
- PostgreSQL database con 12 tablas (11 core + 1 admin_audit_logs)
- Arquitectura 3-tier completa
- 9 módulos con CRUD operations + 1 módulo Admin
- Sistema de autenticación JWT
- **RBAC (Role-Based Access Control) - IMPLEMENTADO ✨**
  - Middleware `@admin_required` funcionando
  - 4 endpoints admin protegidos (Fase 1)
  - Audit logging automático
- 110 tests unitarios pasando exitosamente
- Admin endpoints completamente documentados
- Documentación de API actualizada con 60 endpoints totales

### 🚀 Nuevo: Módulo Admin (Fase 1)
**Estado:** COMPLETO - Listo para testing manual

**Endpoints Implementados:**
- `GET /admin/dashboard` - Estadísticas globales
- `GET /admin/chefs` - Lista con paginación y filtros
- `GET /admin/chefs/:id` - Detalles completos
- `PATCH /admin/chefs/:id/status` - Activar/desactivar chef

**Features:**
- ✅ Audit logging (tabla `admin_audit_logs`)
- ✅ Captura automática de IP
- ✅ Queries optimizados (<500ms)
- ✅ Paginación en todas las listas
- ✅ Búsqueda case-insensitive
- ✅ Ordenamiento flexible

**Documentación:**
- 📖 [Quick Start Guide](docs/ADMIN_QUICKSTART.md) - Guía de testing
- 📋 [Implementation Complete](docs/ADMIN_PHASE1_COMPLETED.md) - Detalles técnicos
- 🎯 [Endpoint Design](docs/ADMIN_ENDPOINTS_DESIGN.md) - Diseño completo

**Próximos Pasos:**
1. Ejecutar migración: `python scripts/run_migration.py`
2. Testing manual con Postman
3. Fase 2: User management endpoints
4. Fase 3: Reports & analytics

### 🔄 En Progreso
- Frontend (todas las páginas)
- PDF generation (WeasyPrint)
- Email integration (SendGrid)
- Calendar integration (Calendly)

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests unitarios
pytest tests/unit/ -v

# Módulo específico
pytest tests/unit/test_auth.py -v

# Test específico
pytest tests/unit/test_auth.py::TestAuthLogin::test_login_success -v

# Con coverage
pytest tests/unit/ --cov=app --cov-report=html
```

### Estado Actual

✅ **93 tests unitarios (100% passing)**

| Módulo | Tests | Estado |
|--------|-------|--------|
| Auth | 16 | ✅ |
| Appointments | 12 | ✅ |
| Chefs | 3 | ✅ |
| Clients | 8 | ✅ |
| Dishes | 10 | ✅ |
| Menus | 9 | ✅ |
| Quotations | 6 | ✅ |
| Scrapers | 14 | ✅ |
| Public | 15 | ✅ |

Ver documentación completa: `tests/TESTING_GUIDE.md`

## 📦 Dependencias Principales

- Flask 3.1 - Framework web
- SQLAlchemy 2.0 - ORM
- PostgreSQL - Base de datos
- PyJWT - Autenticación JWT
- WeasyPrint - Generación de PDFs
- Cloudinary - Almacenamiento de imágenes
- SendGrid - Envío de emails
