# Fruit Store API - Week 7

API REST para gestión de ventas de frutas con autenticación JWT y control de roles usando SQLAlchemy ORM.

## 📋 Características

- Autenticación con JWT (Register/Login)
- Control de acceso basado en roles (Administrador/Cliente)
- Gestión de usuarios
- Gestión de productos (inventario)
- Gestión de facturas/ventas
- Control de stock automático
- Transacciones seguras (prevención de race conditions)

## 🗄️ Base de Datos

### Modelos

**Role**
- id, name (administrador/cliente)

**User**
- id, username, password, role_id

**Product**
- id, name, price, quantity, entry_date

**Invoice**
- id, user_id, invoice_date, total

**InvoiceItem**
- id, invoice_id, product_id, quantity, unit_price, subtotal

### Relaciones
- User → Role (many-to-one)
- User → Invoice (one-to-many)
- Invoice → InvoiceItem (one-to-many, cascade delete)
- Product → InvoiceItem (one-to-many)

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install flask sqlalchemy psycopg2-binary PyJWT
```

### 2. Configurar PostgreSQL

Crear base de datos en PostgreSQL:
- Host: `localhost:5432`
- Database: `lyfter`
- User: `postgres`
- Password: `postgres`

Para usar otra configuración, editar en `app/utilities/db_manager.py`:
```python
db_uri = 'postgresql://user:password@host:port/database'
```

### 3. Inicializar base de datos

```bash
python init_db.py
```

Este script:
- Crea todas las tablas en el schema `backend_week7`
- Inserta roles (administrador y cliente)
- Opcionalmente crea datos de prueba

### 4. Ejecutar el servidor

```bash
python run.py
```

El servidor inicia en `http://localhost:5000`

## 📡 API Endpoints

### Autenticación (Público)

**POST /register** - Registrar nuevo usuario
```json
{
  "username": "usuario1",
  "password": "pass123"
}
```

**POST /login** - Iniciar sesión
```json
{
  "username": "admin",
  "password": "admin123"
}
```
Retorna un token JWT para usar en endpoints protegidos.

### Usuarios (Requiere autenticación)

**GET /users** - Listar usuarios (Solo Admin)

**GET /users/{id}** - Ver usuario (Admin o propio perfil)

**POST /users** - Crear usuario (Solo Admin)
```json
{
  "username": "newuser",
  "password": "pass123",
  "role_id": 2
}
```

**PUT /users/{id}** - Actualizar usuario
- Admin: Puede actualizar todo
- Cliente: Solo su password

**DELETE /users/{id}** - Eliminar usuario (Solo Admin)

### Productos

**GET /products** - Listar productos (Público)

**GET /products/{id}** - Ver producto (Público)

**POST /products** - Crear producto (Solo Admin)
```json
{
  "name": "Manzana",
  "price": 150,
  "quantity": 100,
  "entry_date": "2025-10-08"
}
```

**PUT /products/{id}** - Actualizar producto (Solo Admin)

**DELETE /products/{id}** - Eliminar producto (Solo Admin)

### Facturas (Requiere autenticación)

**GET /invoices** - Listar facturas
- Admin: Ve todas
- Cliente: Solo las propias

**GET /invoices/{id}** - Ver factura (Admin o dueño)

**POST /invoices** - Crear factura
```json
{
  "items": [
    {"product_id": 1, "quantity": 5},
    {"product_id": 2, "quantity": 3}
  ]
}
```

**DELETE /invoices/{id}** - Eliminar factura (Solo Admin)

### Autenticación en Headers

Para endpoints protegidos, incluir el token JWT:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🔐 Roles y Permisos

### Administrador (role_id = 1)
- CRUD completo de usuarios
- CRUD completo de productos
- Ver todas las facturas
- Eliminar facturas

### Cliente (role_id = 2)
- Ver productos
- Crear facturas (comprar)
- Ver solo sus facturas
- Actualizar su contraseña

## 🎯 Decoradores JWT

El proyecto usa decoradores para proteger rutas:

```python
@require_auth_with_repo('user_repository')
def get(self):
    user_id = g.user_data['user_id']
    is_admin = g.is_admin
    # ...
```

**Decoradores disponibles:**
- `@require_auth` - Requiere token válido
- `@require_admin` - Requiere token + rol admin
- `@require_auth_with_repo()` - Token + verifica rol en BD
- `@require_admin_with_repo()` - Token + verifica admin en BD

## 🔒 Transacciones y Concurrencia

El sistema usa **pessimistic locking** (SELECT FOR UPDATE) para prevenir problemas de concurrencia al crear facturas:

```python
# Bloquea el producto durante la transacción
product = session.query(Product).with_for_update().first()
```

Esto garantiza que:
- No se venda más stock del disponible
- Las transacciones sean atómicas (todo o nada)
- Se prevengan race conditions en compras simultáneas

## 🧪 Datos de Prueba

Si activaste los datos de prueba en `init_db.py`:

**Usuarios:**
- Admin: `admin` / `admin123`
- Cliente: `client1` / `pass123`

**Productos:**
- Apple ($150, stock: 100)
- Banana ($80, stock: 150)
- Orange ($120, stock: 200)
- Strawberry ($200, stock: 50)

## 📂 Estructura del Proyecto

```
week_7/
├── run.py                      # Punto de entrada
├── init_db.py                  # Inicialización de BD
├── app/
│   ├── auth/
│   │   ├── auth_routes.py      # Register/Login
│   │   ├── user_routes.py      # CRUD usuarios
│   │   └── user_repository.py  # Lógica de datos usuarios
│   ├── products/
│   │   ├── product_routes.py   # CRUD productos
│   │   └── product_repository.py
│   ├── sales/
│   │   ├── invoice_routes.py   # CRUD facturas
│   │   └── invoice_repository.py
│   └── utilities/
│       ├── base_model.py       # Modelos SQLAlchemy
│       ├── db_manager.py       # Gestión de conexiones
│       ├── jwt_manager.py      # Manejo de tokens
│       └── decorators.py       # Decoradores de autenticación
└── config/
    └── security_config.py      # Configuración JWT
```

## ⚙️ Configuración Avanzada

### Cambiar schema de PostgreSQL

```python
db_manager = DBManager(schema='otro_schema')
```

### Habilitar logs SQL

```python
db_manager = DBManager(echo=True)
```

### Configurar JWT

En `config/security_config.py`:
```python
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'tu-secret-key')
JWT_EXPIRATION_HOURS = 24
```

```python
# Bloquea la fila del producto hasta el COMMIT
product = session.query(Product).with_for_update().first()
product.cantidad -= cantidad_comprada
session.commit()  # Libera el lock
```

### **Casos de Uso**
- ✅ **Stock Management**: Previene que 2 usuarios compren el último producto
- ✅ **ACID Compliance**: Garantiza atomicidad en operaciones multi-paso
- ✅ **Rollback Automático**: Si falla cualquier paso, se revierten todos

## �📝 Notas

- Las contraseñas están en texto plano (agregar hashing en producción)
- El JWT_Manager debe estar configurado con secret key
- Asegúrate de que el schema de PostgreSQL exista antes de crear tablas
