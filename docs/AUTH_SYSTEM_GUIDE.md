# 🔐 Sistema de Autenticación y Autorización - Guía de Uso

Sistema consolidado compatible con **multi-role** (usuarios pueden tener múltiples roles).

---

## 📁 **Estructura de Archivos**

```
app/core/
├── lib/
│   └── auth.py              # ✅ Helper functions (is_admin_user, user_has_role, is_user_or_admin)
└── middleware/
    └── auth_decorators.py   # ✅ Decoradores (@token_required_with_repo, @admin_required_with_repo)
```

---

## 🎯 **Patrones de Uso**

### **Pattern 1: Admin-Only Endpoint**
Cuando SOLO los admins pueden acceder.

```python
from app.core.middleware import admin_required_with_repo

@admin_required_with_repo
def delete_user(user_id):
    """Only admins can delete users"""
    # g.current_user is set automatically
    # Admin check already done by decorator
    
    user_service.delete_user(user_id)
    return jsonify({"message": "User deleted"}), 200
```

**¿Qué hace el decorador?**
1. ✅ Valida JWT token
2. ✅ Carga usuario desde DB (fresco)
3. ✅ Verifica que tenga rol 'admin' (entre TODOS sus roles)
4. ✅ Retorna 403 si no es admin
5. ✅ Setea `g.current_user` si todo OK

---

### **Pattern 2: User or Admin Access**
Cuando usuarios pueden acceder a SUS datos, pero admins pueden acceder a TODOS.

```python
from app.core.middleware import token_required_with_repo
from app.core.lib.auth import is_user_or_admin

@token_required_with_repo
def get_user_cart(user_id):
    """Users can see their own cart, admins can see any cart"""
    
    # Check authorization manually
    if not is_user_or_admin(user_id):
        return jsonify({"error": "Access denied"}), 403
    
    cart = cart_service.get_cart(user_id)
    return jsonify(cart), 200
```

**¿Qué hace `@token_required_with_repo`?**
1. ✅ Valida JWT token
2. ✅ Carga usuario desde DB (fresco)
3. ✅ Setea `g.current_user`
4. ❌ **NO** verifica roles (eso lo haces tú con `is_user_or_admin()`)

**¿Qué hace `is_user_or_admin(user_id)`?**
- Retorna `True` si:
  - El usuario actual es admin, O
  - El usuario actual tiene el mismo ID que `user_id`

---

### **Pattern 3: Public with Admin Extras (Optional Auth)**
Cuando el endpoint es público, pero si hay admin autenticado ve datos extra.

```python
from flask import g
from app.core.lib.auth import is_admin_user
from app.core.lib.jwt import verify_jwt_token
from app.core.lib.users import get_user_by_id

class ProductAPI(MethodView):
    def get(self, product_id=None):
        """Public access, with admin extras if authenticated"""
        
        # Optional authentication
        self._try_authenticate_user()
        
        # Get products
        products = product_service.get_all_products()
        
        # Check if admin (safely)
        include_admin_data = is_admin_user()
        
        # Serialize with appropriate schema
        schema = ProductResponseSchema(
            include_admin_data=include_admin_data,
            many=True
        )
        
        return jsonify(schema.dump(products))
    
    def _try_authenticate_user(self):
        """Try to authenticate, but don't fail if no token"""
        if 'Authorization' not in request.headers:
            return  # No token, public access
        
        try:
            token = request.headers['Authorization'].split(" ")[1]
            data = verify_jwt_token(token)
            if data:
                user = get_user_by_id(data['user_id'])
                if user:
                    g.current_user = user
        except:
            pass  # Invalid token, just ignore
```

**¿Qué hace `is_admin_user()`?**
- Retorna `True` si `g.current_user` existe Y tiene rol 'admin'
- Retorna `False` si no hay usuario autenticado (safe)

---

## 🧰 **Funciones Helper en `auth.py`**

### **`user_has_role(user, role_name)`**
Verifica si un usuario tiene un rol específico (soporta multi-role).

```python
from app.core.lib.auth import user_has_role

if user_has_role(current_user, 'admin'):
    # Usuario es admin
    
if user_has_role(current_user, 'moderator'):
    # Usuario es moderador
```

---

### **`is_admin_user()`**
Verifica si el usuario actual (en `g.current_user`) es admin.
Safe to call - retorna `False` si no hay usuario autenticado.

```python
from app.core.lib.auth import is_admin_user

if is_admin_user():
    # Show admin panel
    # Add admin_data to response
```

---

### **`is_user_or_admin(user_id)`**
Verifica si el usuario actual puede acceder a datos del `user_id`.
- `True` si el usuario actual es admin
- `True` si el usuario actual tiene el mismo ID
- `False` en otro caso

```python
from app.core.lib.auth import is_user_or_admin

@token_required_with_repo
def update_profile(user_id):
    if not is_user_or_admin(user_id):
        return jsonify({"error": "Access denied"}), 403
    
    # Proceed with update
```

---

## 📋 **Checklist de Implementación**

### ✅ **Para rutas ADMIN-ONLY:**
1. Usa `@admin_required_with_repo`
2. Accede a `g.current_user` directamente
3. No necesitas verificar nada más

### ✅ **Para rutas USER-OR-ADMIN:**
1. Usa `@token_required_with_repo`
2. Verifica con `is_user_or_admin(user_id)`
3. Retorna 403 si la verificación falla

### ✅ **Para rutas PUBLIC con admin extras:**
1. NO uses decorador
2. Llama a `_try_authenticate_user()` manualmente
3. Usa `is_admin_user()` para verificar

---

## 🚫 **Qué NO Hacer**

### ❌ **NO uses decoradores viejos:**
```python
# ❌ OLD - No longer exported
from app.core.middleware import token_required, admin_required

@token_required
@admin_required
def my_route():
    pass
```

### ❌ **NO accedas a `g.current_user.role` (singular):**
```python
# ❌ OLD - role is now user_roles (N:M relationship)
if g.current_user.role == 'admin':
    pass
```

### ❌ **NO verifices solo el primer rol:**
```python
# ❌ BAD - User might have admin as 2nd, 3rd role
if g.current_user.user_roles[0].role.name == 'admin':
    pass
```

### ✅ **CORRECTO - Usa las funciones helper:**
```python
# ✅ GOOD - Checks ALL roles
from app.core.lib.auth import user_has_role, is_admin_user

if user_has_role(g.current_user, 'admin'):
    pass

# Or simply:
if is_admin_user():
    pass
```

---

## 🎓 **Ejemplos Completos**

### **Ejemplo 1: Product Routes (Public + Admin)**

```python
from flask import g, request, jsonify
from flask.views import MethodView
from app.core.middleware import admin_required_with_repo
from app.core.lib.auth import is_admin_user
from app.core.lib.jwt import verify_jwt_token
from app.core.lib.users import get_user_by_id

class ProductAPI(MethodView):
    
    def get(self, product_id=None):
        """Public endpoint - shows admin data if authenticated as admin"""
        # Try optional authentication
        self._try_authenticate_user()
        
        # Get products
        if product_id:
            product = product_service.get_by_id(product_id)
            many = False
        else:
            product = product_service.get_all()
            many = True
        
        # Determine schema config based on admin status
        include_admin_data = is_admin_user()
        schema = ProductResponseSchema(
            include_admin_data=include_admin_data,
            many=many
        )
        
        return jsonify(schema.dump(product))
    
    @admin_required_with_repo
    def post(self):
        """Admin-only - create product"""
        data = product_schema.load(request.json)
        product = product_service.create(data)
        return jsonify({"message": "Created", "product": product}), 201
    
    @admin_required_with_repo
    def put(self, product_id):
        """Admin-only - update product"""
        data = product_schema.load(request.json)
        product = product_service.update(product_id, data)
        return jsonify({"message": "Updated", "product": product}), 200
    
    @admin_required_with_repo
    def delete(self, product_id):
        """Admin-only - delete product"""
        product_service.delete(product_id)
        return jsonify({"message": "Deleted"}), 200
    
    def _try_authenticate_user(self):
        """Optional authentication helper"""
        if 'Authorization' not in request.headers:
            return
        
        try:
            token = request.headers['Authorization'].split(" ")[1]
            data = verify_jwt_token(token)
            if data:
                user = get_user_by_id(data['user_id'])
                if user:
                    g.current_user = user
        except:
            pass
```

---

### **Ejemplo 2: Cart Routes (User or Admin)**

```python
from flask.views import MethodView
from app.core.middleware import token_required_with_repo
from app.core.lib.auth import is_user_or_admin

class CartAPI(MethodView):
    
    @token_required_with_repo
    def get(self, user_id):
        """User can see their own cart, admin can see any"""
        if not is_user_or_admin(user_id):
            return jsonify({"error": "Access denied"}), 403
        
        cart = cart_service.get_cart(user_id)
        return jsonify(cart), 200
    
    @token_required_with_repo
    def post(self, user_id):
        """User can add to their own cart, admin can add to any"""
        if not is_user_or_admin(user_id):
            return jsonify({"error": "Access denied"}), 403
        
        data = request.json
        cart = cart_service.add_item(user_id, data)
        return jsonify(cart), 201
    
    @token_required_with_repo
    def delete(self, user_id):
        """User can clear their own cart, admin can clear any"""
        if not is_user_or_admin(user_id):
            return jsonify({"error": "Access denied"}), 403
        
        cart_service.clear_cart(user_id)
        return jsonify({"message": "Cart cleared"}), 200
```

---

## 🔄 **Migración de Código Existente**

### **Si tienes:**
```python
@token_required
@admin_required
def my_route():
    pass
```

### **Cambia a:**
```python
@admin_required_with_repo
def my_route():
    pass
```

---

### **Si tienes:**
```python
@token_required
def my_route():
    if g.current_user.role != UserRole.ADMIN:
        return jsonify({"error": "Admin required"}), 403
    # ...
```

### **Cambia a:**
```python
@admin_required_with_repo
def my_route():
    # Admin check already done by decorator
    # ...
```

---

### **Si tienes:**
```python
@token_required
def get_cart(user_id):
    if g.current_user.role != UserRole.ADMIN and g.current_user.id != user_id:
        return jsonify({"error": "Access denied"}), 403
    # ...
```

### **Cambia a:**
```python
from app.core.lib.auth import is_user_or_admin

@token_required_with_repo
def get_cart(user_id):
    if not is_user_or_admin(user_id):
        return jsonify({"error": "Access denied"}), 403
    # ...
```

---

## ✅ **Resumen**

| Caso de Uso | Decorador | Función Helper | Ejemplo |
|-------------|-----------|----------------|---------|
| **Admin-only** | `@admin_required_with_repo` | - | `DELETE /users/{id}` |
| **User or Admin** | `@token_required_with_repo` | `is_user_or_admin(id)` | `GET /cart/{user_id}` |
| **Public + Admin extras** | None (manual) | `is_admin_user()` | `GET /products` |
| **Check specific role** | - | `user_has_role(user, 'moderator')` | Custom roles |

---

## 🎯 **Siguientes Pasos**

1. ✅ Revisar rutas de productos (**HECHO**)
2. 🔄 Aplicar mismo patrón en rutas de sales (cart, orders, etc.)
3. 🔄 Aplicar mismo patrón en rutas de auth (users management)
4. ✅ Eliminar decoradores viejos del código (**HECHO**)
5. ✅ Consolidar funciones helper (**HECHO**)
