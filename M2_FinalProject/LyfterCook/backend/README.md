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

# 6. Ejecutar aplicación
python run.py
```

El servidor estará disponible en `http://localhost:5000`

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
│   ├── scraper/       # Scraper de productos
│   ├── public/        # Endpoints públicos
│   └── core/          # Database, utils, middleware
├── config/            # Configuración
├── tests/             # Tests
└── scripts/           # Scripts de utilidad
```

## 🔧 Configuración

Ver `config/.env.example` para todas las variables disponibles.

Variables esenciales:
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`
- `JWT_SECRET_KEY`
- `CLOUDINARY_*` (para imágenes)
- `SENDGRID_API_KEY` (para emails)

## 📚 Documentación

- [Plan del Proyecto](../docs/PROJECT_PLAN.md)
- API Routes (próximamente)

## 🧪 Testing

```bash
pytest
pytest --cov=app tests/
```

## 📦 Dependencias Principales

- Flask 3.1 - Framework web
- SQLAlchemy 2.0 - ORM
- PostgreSQL - Base de datos
- PyJWT - Autenticación JWT
- WeasyPrint - Generación de PDFs
- Cloudinary - Almacenamiento de imágenes
- SendGrid - Envío de emails
