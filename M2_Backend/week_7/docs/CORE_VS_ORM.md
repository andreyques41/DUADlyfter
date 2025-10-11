# Comparación: SQLAlchemy Core vs ORM

## Ejemplo lado a lado

### 1️⃣ INSERTAR DATOS

**Core (antes):**
```python
from sqlalchemy import insert

users_table = Table("users", metadata, ...)
stmt = insert(users_table).values([
    {"username": "admin", "password": "hash123"},
    {"username": "john", "password": "hash456"}
])
conn.execute(stmt)
conn.commit()
```

**ORM (ahora):**
```python
user1 = User(username="admin", password="hash123")
user2 = User(username="john", password="hash456")
session.add_all([user1, user2])
session.commit()
```
✅ **Más simple, con type hints y autocompletado!**

---

### 2️⃣ CONSULTAR DATOS

**Core:**
```python
from sqlalchemy import select

stmt = select(users_table).where(users_table.c.username == "admin")
result = conn.execute(stmt)
row = result.fetchone()
print(row["username"])  # Acceso por string, sin validación
```

**ORM:**
```python
user = session.query(User).filter_by(username="admin").first()
print(user.username)  # Acceso con atributo, con autocompletado!
```
✅ **Type safety y mejor experiencia de desarrollo!**

---

### 3️⃣ ACTUALIZAR DATOS

**Core:**
```python
from sqlalchemy import update

stmt = update(users_table).where(
    users_table.c.username == "admin"
).values(password="new_hash")
conn.execute(stmt)
conn.commit()
```

**ORM:**
```python
user = session.query(User).filter_by(username="admin").first()
user.password = "new_hash"  # ¡Simplemente cambias el atributo!
session.commit()
```
✅ **Más intuitivo y Pythonic!**

---

### 4️⃣ ELIMINAR DATOS

**Core:**
```python
from sqlalchemy import delete

stmt = delete(users_table).where(users_table.c.id == 1)
conn.execute(stmt)
conn.commit()
```

**ORM:**
```python
user = session.query(User).get(1)
session.delete(user)
session.commit()
```
✅ **Más claro!**

---

### 5️⃣ RELACIONES (la verdadera ventaja del ORM)

**Core:**
```python
# Tienes que hacer JOINs manualmente
stmt = select(users_table, orders_table).join(
    orders_table, users_table.c.id == orders_table.c.user_id
)
```

**ORM:**
```python
class User(Base):
    orders = relationship("Order", back_populates="user")

class Order(Base):
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")

# Uso:
user = session.query(User).first()
print(user.orders)  # ¡Acceso directo a órdenes relacionadas!
```
✅ **Relaciones automáticas y bidireccionales!**

---

## 🎯 Resumen de Cambios en tu Código

### Antes (Core):
```python
# Tenías que:
1. Crear funciones create_*_table()
2. Registrar manualmente en self.tables = {}
3. Recordar actualizar DBManager cada vez que agregabas una tabla
4. Usar insert(), select(), update() para todo
```

### Ahora (ORM):
```python
# Solo necesitas:
1. Crear una clase que herede de Base
2. ¡SQLAlchemy la descubre automáticamente!
3. Trabajar con objetos Python normales
4. session.add(), session.query() - más simple
```

---

## 📦 Cómo Agregar Nuevas Tablas Ahora

**Antes (Core):** 5 pasos
1. Crear función `create_bills_table()` en `models/bills.py`
2. Importar en `models/__init__.py`
3. Importar en `db_manager.py`
4. Agregar `self.tables['bills'] = create_bills_table()`
5. ❌ Fácil olvidar un paso

**Ahora (ORM):** 2 pasos
1. Crear `models/bills.py`:
```python
class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = {'schema': 'backend_week7'}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[int]
    date: Mapped[date]
```

2. Importar en `models/__init__.py`:
```python
from .bills import Bill
__all__ = ['Base', 'User', 'Product', 'Bill']
```

✅ **¡Y listo! Base.metadata.create_all() la encontrará automáticamente**

---

## 🚀 Ventajas Clave para tu Proyecto

1. **No más diccionario `tables`** - Auto-discovery elimina el problema
2. **Type hints** - Tu IDE te ayuda con autocompletado
3. **Menos código** - Queries más simples y legibles
4. **Relaciones fáciles** - Para User → Bills, Product → Orders, etc.
5. **Validaciones** - Puedes agregar métodos y propiedades a los modelos
6. **Testing más fácil** - Objetos Python son más fáciles de testear

---

## 📖 Recursos para Aprender Más

- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [Mapped Column Documentation](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
- [Relationship Patterns](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
