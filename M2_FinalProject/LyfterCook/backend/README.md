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
│   └── core/          # Database, utils, middleware
├── config/            # Configuración
├── tests/             # Tests organizados
│   ├── conftest.py    # Fixtures compartidas
│   ├── setup_test_db.py
│   ├── TESTING_GUIDE.md
│   ├── unit/          # ✅ 93 tests (100%)
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
│   │   └── test_helpers.py
│   └── integration/   # ⏳ Pending (Phase 7)
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
- [Rutas de API](../docs/API_ROUTES.md) - Documentación de 53 endpoints
- [Guía de Testing](tests/TESTING_GUIDE.md) - Cómo ejecutar y escribir tests
- [Schema Migration](../docs/SCHEMA_MIGRATION.md) - Detalles de base de datos

### Tests
- [Unit Tests](tests/unit/README.md) - 93 tests unitarios
- [Integration Tests](tests/integration/README.md) - Tests de integración (Phase 7)

## 📊 Estado del Proyecto

### ✅ Completado
- PostgreSQL database con 11 tablas
- Arquitectura 3-tier completa
- 9 módulos con CRUD operations
- Sistema de autenticación JWT
- 93 tests unitarios (100%)
- Documentación de API

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
