# Fruit Store API - Week 7 Project

Sistema de venta de frutas con autenticación y control de roles usando SQLAlchemy ORM.

## 📋 Características

- ✅ **Autenticación**: Register y Login con JWT
- ✅ **Roles**: Administrador y Cliente
- ✅ **CRUD Usuarios**: Gestión completa de usuarios (Admin)
- ✅ **CRUD Productos**: Gestión completa de inventario (Admin)
- ✅ **CRUD Facturas**: Ventas con control de stock
- ✅ **Permisos**: Control granular basado en roles
- ✅ **ORM**: SQLAlchemy con auto-discovery de modelos
- ✅ **Relaciones**: Many-to-many entre Invoices y Products

## 🗄️ Modelos

### Role
- `id` (PK)
- `name` (cliente/administrador)

### User
- `id` (PK)
- `username` (unique)
- `password`
- `role_id` (FK → roles)

### Product
- `id` (PK)
- `nombre`
- `precio`
- `fecha_entrada`
- `cantidad`

### Invoice
- `id` (PK)
- `user_id` (FK → users)
- `fecha`
- `total`

### InvoiceItem
- `id` (PK)
- `invoice_id` (FK → invoices)
- `product_id` (FK → products)
- `cantidad`
- `precio_unitario`
- `subtotal`

## 🚀 Instalación

### 1. Instalar dependencias
```bash
pip install flask sqlalchemy psycopg2-binary PyJWT
```

### 2. Configurar base de datos
Asegúrate de tener PostgreSQL corriendo en `localhost:5432` con:
- Database: `lyfter`
- User: `postgres`
- Password: `postgres`

O actualiza la URI en `app/utilities/db_manager.py`:
```python
db_uri = 'postgresql://user:password@host:port/database'
```

### 3. Inicializar base de datos
```bash
python init_db.py
```

Esto creará:
- Todas las tablas
- Roles (administrador y cliente)
- Opcionalmente: datos de prueba

### 4. Ejecutar API
```bash
python run.py
```

La API estará disponible en `http://localhost:5000`

## 📡 Endpoints

### Autenticación

#### POST /register
Registrar nuevo usuario (cliente por defecto)
```json
Request:
{
  "username": "usuario1",
  "password": "pass123"
}

Response:
{
  "message": "User registered successfully",
  "token": "eyJ...",
  "user_id": 1
}
```

#### POST /login
Iniciar sesión
```json
Request:
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "message": "Login successful",
  "token": "eyJ...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "administrador",
    "is_admin": true
  }
}
```

### Gestión de Usuarios (Requiere autenticación)

**Ver documentación completa**: [USER_MANAGEMENT_API.md](docs/USER_MANAGEMENT_API.md)

#### GET /users
Obtener todos los usuarios (Solo Admin)

#### GET /users/{id}
Obtener usuario específico (Admin o propio perfil)

#### POST /users
Crear nuevo usuario (Solo Admin)
```json
Request:
{
  "username": "newuser",
  "password": "pass123",
  "role_id": 2  // 1=admin, 2=client
}
```

#### PUT /users/{id}
Actualizar usuario
- Admin: Puede actualizar cualquier usuario (username, password, role_id)
- Cliente: Solo puede actualizar su propia contraseña

#### DELETE /users/{id}
Eliminar usuario (Solo Admin, no puede eliminarse a sí mismo)

### Productos (GET público, CUD requiere Admin)

#### GET /products
Obtener todos los productos
```json
Response:
{
  "products": [
    {
      "id": 1,
      "nombre": "Manzana",
      "precio": 150,
      "cantidad": 100,
      "fecha_entrada": "2025-10-08"
    }
  ]
}
```

#### GET /products/{id}
Obtener producto específico

#### POST /products
Crear producto
```json
Request:
{
  "nombre": "Manzana",
  "precio": 150,
  "cantidad": 100,
  "fecha_entrada": "2025-10-08"  // Opcional, usa fecha actual si se omite
}
```

#### PUT /products/{id}
Actualizar producto

#### DELETE /products/{id}
Eliminar producto

### Facturas (Requiere autenticación - Token en header)

#### GET /invoices
Obtener facturas
- **Cliente**: Solo ve sus propias facturas
- **Admin**: Ve todas las facturas

Headers:
```
Authorization: Bearer {token}
```

#### GET /invoices/{id}
Obtener factura específica (solo si es el dueño o admin)

#### POST /invoices
Crear factura
```json
Request:
{
  "items": [
    {"product_id": 1, "cantidad": 5},
    {"product_id": 2, "cantidad": 3}
  ]
}

Response:
{
  "message": "Invoice created successfully",
  "invoice_id": 1
}
```

Nota: La factura se crea automáticamente:
- Calcula el total
- Reduce el stock de productos
- Asigna al usuario del token

#### DELETE /invoices/{id}
Eliminar factura (solo Admin)

## 🔐 Roles y Permisos

### Administrador (role_id=1)
- ✅ Ver todas las facturas
- ✅ Eliminar facturas
- ✅ Gestionar productos
- ✅ Crear facturas

### Cliente (role_id=2)
- ✅ Ver solo sus facturas
- ✅ Crear facturas
- ❌ No puede eliminar facturas
- ✅ Ver productos

## 🧪 Testing con datos de prueba

Si usaste test data en `init_db.py`, puedes probar con:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Cliente:**
- Username: `cliente1`
- Password: `pass123`

**Productos:**
- Manzana ($150)
- Banana ($80)
- Naranja ($120)
- Fresa ($200)

## 📂 Estructura del Proyecto

```
week_7/
├── api.py                  # Flask app con routes registradas
├── init_db.py              # Script de inicialización
├── app/
│   ├── auth/
│   │   ├── auth_routes.py      # Register y Login
│   │   └── user_repository.py  # Lógica de usuarios
│   ├── products/
│   │   ├── product_routes.py   # CRUD productos
│   │   └── product_repository.py
│   ├── sales/
│   │   ├── invoice_routes.py   # CRUD facturas
│   │   └── invoice_repository.py
│   └── utilities/
│       ├── base_model.py       # Todos los modelos ORM
│       ├── db_manager.py       # Gestión de DB
│       └── jwt_manager.py      # Gestión de tokens
```

## 🔧 Configuración Adicional

### Cambiar Schema
Por defecto usa `backend_week7`. Para cambiarlo:

```python
db_manager = DBManager(schema='mi_schema')
```

### Habilitar logs SQL
```python
db_manager = DBManager(echo=True)
```

## ✅ TODO
- [ ] Hash passwords con bcrypt
- [ ] Agregar validación de roles con decoradores
- [ ] Agregar paginación a GET /products y /invoices
- [ ] Agregar búsqueda/filtros a productos
- [ ] Agregar fecha de creación a users
- [ ] Tests unitarios

## � Manejo de Transacciones

Este proyecto implementa **transacciones robustas** para prevenir race conditions:

### **Pessimistic Locking** (SELECT FOR UPDATE)
Usado en `invoice_repository.create_invoice()` para evitar sobreventa:

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

### **Testing**
Ejecutar test de race conditions:
```bash
python test_transactions.py
```

Ver documentación completa: [`TRANSACTIONS_GUIDE.md`](./TRANSACTIONS_GUIDE.md)

## �📝 Notas

- Las contraseñas están en texto plano (agregar hashing en producción)
- El JWT_Manager debe estar configurado con secret key
- Asegúrate de que el schema de PostgreSQL exista antes de crear tablas
