# 🔍 API Response Audit - Frontend Data Requirements

**Fecha:** December 14, 2025
**Objetivo:** Identificar datos faltantes en las respuestas de API que el frontend necesitará

---

## ❌ PROBLEMAS IDENTIFICADOS

### 🧑‍🍳 **Chef Module**

#### `GET /chefs/{id}` - ChefPublicSchema
**Actual:**
```json
{
  "id": 1,
  "bio": "...",
  "specialty": "...",
  "location": "...",
  "user": {
    "id": 1,
    "username": "..."
  }
}
```

**Problemas:**
1. ❌ Falta `phone` - Necesario para contacto
2. ❌ Falta `is_active` - Frontend debe saber si chef está activo
3. ❌ Falta `created_at` - Útil para mostrar "Miembro desde..."
4. ❌ Falta `user.email` en ChefPublicSchema - Contacto público

**Solución:** Agregar campos faltantes a `ChefPublicSchema`

---

#### `GET /chefs/profile` - ChefResponseSchema
**Actual:** ✅ CORRECTO
```json
{
  "id": 1,
  "user_id": 1,
  "bio": "...",
  "specialty": "...",
  "phone": "...",
  "location": "...",
  "is_active": true,
  "created_at": "...",
  "updated_at": "...",
  "user": {
    "id": 1,
    "username": "...",
    "email": "..."
  }
}
```

---

### 👥 **Client Module**

#### `GET /clients` y `GET /clients/{id}` - ClientResponseSchema
**Actual:** ✅ CORRECTO
```json
{
  "id": 1,
  "chef_id": 1,
  "name": "...",
  "email": "...",
  "phone": "...",
  "company": "...",
  "notes": "...",
  "created_at": "...",
  "updated_at": "..."
}
```

**Mejora sugerida:**
- ⚠️ Agregar `appointment_count` - Útil para dashboard
- ⚠️ Agregar `quotation_count` - Útil para dashboard
- ⚠️ Agregar `last_contact_date` - Último appointment/quotation

---

### 🍽️ **Dish Module**

#### `GET /dishes` y `GET /dishes/{id}` - DishResponseSchema
**Actual:** ✅ MAYORMENTE CORRECTO
```json
{
  "id": 1,
  "chef_id": 1,
  "name": "...",
  "description": "...",
  "price": 18.99,
  "category": "...",
  "preparation_steps": "...",
  "prep_time": 30,
  "servings": 4,
  "photo_url": "...",
  "is_active": true,
  "created_at": "...",
  "updated_at": "...",
  "ingredients": [...]
}
```

**Mejora sugerida:**
- ⚠️ Agregar `menu_count` - En cuántos menús está este platillo
- ⚠️ Agregar `times_ordered` - Popularidad (si se implementa tracking de órdenes)

---

### 📋 **Menu Module**

#### `GET /menus` y `GET /menus/{id}` - MenuResponseSchema
**Actual:**
```json
{
  "id": 1,
  "chef_id": 1,
  "name": "...",
  "description": "...",
  "status": "active",
  "created_at": "...",
  "updated_at": "...",
  "dishes": [...]
}
```

**Problemas:**
1. ❌ `dishes` devuelve `List[Dict]` sin estructura clara
2. ⚠️ Falta `total_price` calculado (suma de precios de platillos)
3. ⚠️ Falta `dish_count` (número de platillos)
4. ⚠️ Falta información completa de platillos en lista

**Solución:** 
- Crear `MenuDishResponseSchema` para estructurar dishes:
```json
{
  "dish_id": 1,
  "order_position": 1,
  "dish": {
    "id": 1,
    "name": "...",
    "price": 18.99,
    "category": "...",
    "photo_url": "...",
    "is_active": true
  }
}
```
- Agregar campos calculados: `total_price`, `dish_count`

---

### 💰 **Quotation Module**

#### `GET /quotations` y `GET /quotations/{id}` - QuotationResponseSchema
**Actual:** ✅ MAYORMENTE CORRECTO
```json
{
  "id": 1,
  "chef_id": 1,
  "client_id": 1,
  "menu_id": 1,
  "quotation_number": "QT-...",
  "event_date": "...",
  "number_of_people": 50,
  "total_price": 949.50,
  "status": "sent",
  "notes": "...",
  "terms_and_conditions": "...",
  "created_at": "...",
  "updated_at": "...",
  "sent_at": "...",
  "responded_at": "...",
  "items": [...]
}
```

**Problemas:**
1. ❌ Falta información del `client` (nested)
2. ❌ Falta información del `menu` (nested)
3. ❌ `items` devuelve `List[Dict]` sin estructura

**Solución:**
- Agregar nested schemas:
```json
{
  "client": {
    "id": 1,
    "name": "...",
    "email": "...",
    "phone": "...",
    "company": "..."
  },
  "menu": {
    "id": 1,
    "name": "...",
    "dish_count": 5
  },
  "items": [
    {
      "id": 1,
      "dish_id": 1,
      "item_name": "...",
      "description": "...",
      "quantity": 50,
      "unit_price": 18.99,
      "subtotal": 949.50
    }
  ]
}
```

---

### 📅 **Appointment Module**

#### `GET /appointments` y `GET /appointments/{id}` - AppointmentResponseSchema
**Actual:** ✅ MAYORMENTE CORRECTO
```json
{
  "id": 1,
  "chef_id": 1,
  "client_id": 1,
  "title": "...",
  "description": "...",
  "scheduled_at": "...",
  "duration_minutes": 60,
  "location": "...",
  "meeting_url": "...",
  "status": "scheduled",
  "notes": "...",
  "cancellation_reason": null,
  "created_at": "...",
  "updated_at": "...",
  "cancelled_at": null,
  "completed_at": null
}
```

**Problemas:**
1. ❌ Falta información del `client` (nested)
2. ⚠️ Falta `end_time` calculado (scheduled_at + duration_minutes)

**Solución:**
```json
{
  "client": {
    "id": 1,
    "name": "...",
    "email": "...",
    "phone": "...",
    "company": "..."
  },
  "end_time": "2025-12-20T15:00:00Z"  // Calculated
}
```

---

### 🛒 **Scraper Module**

#### `GET /scrapers/sources` - PriceSourceResponseSchema
**Actual:** ✅ CORRECTO (revisar si se necesita más)

#### `GET /scrapers/prices` - ScrapedPriceResponseSchema
**Actual:** ✅ CORRECTO (revisar si se necesita más)

---

### 🌐 **Public Module**

Los endpoints públicos deben devolver datos similares pero con restricciones de privacidad.

#### `GET /public/chefs` - Necesita mismo fix que ChefPublicSchema

#### `GET /public/menus/{id}` - Necesita:
- Chef info (name, specialty, location)
- Dishes completos con ingredientes

#### `GET /public/dishes/{id}` - Necesita:
- Chef info completo

---

## 📊 RESUMEN DE CAMBIOS NECESARIOS

### 🔴 ALTA PRIORIDAD (Datos críticos faltantes):

1. **ChefPublicSchema** → Agregar `phone`, `is_active`, `created_at`, `user.email`
2. **MenuResponseSchema** → Estructurar `dishes` con schema, agregar `total_price`, `dish_count`
3. **QuotationResponseSchema** → Agregar nested `client`, `menu`, estructurar `items`
4. **AppointmentResponseSchema** → Agregar nested `client`, `end_time` calculado

### 🟡 MEDIA PRIORIDAD (Mejoras para UX):

5. **ClientResponseSchema** → Agregar `appointment_count`, `quotation_count`, `last_contact_date`
6. **DishResponseSchema** → Agregar `menu_count`, `times_ordered`

### 🟢 BAJA PRIORIDAD (Nice to have):

7. Agregar paginación metadata consistente en todos los list endpoints
8. Agregar campos `_links` para HATEOAS (REST best practice)

---

## 🎯 PLAN DE ACCIÓN

### Fase 1: Fixes Críticos (ChefPublicSchema)
```python
# app/chefs/schemas/chef_schema.py
class ChefPublicSchema(Schema):
    """Schema for public chef profile (visible to anyone)"""
    id = fields.Int(dump_only=True)
    bio = fields.Str(allow_none=True)
    specialty = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)  # ✅ AGREGAR
    location = fields.Str(allow_none=True)
    is_active = fields.Bool()  # ✅ AGREGAR
    created_at = fields.DateTime(dump_only=True)  # ✅ AGREGAR
    
    # User info for public view
    user = fields.Nested('UserResponseSchema', only=['id', 'username', 'email'])  # ✅ AGREGAR email
```

### Fase 2: Menu Response Structure
```python
# app/menus/schemas/menu_schema.py
class MenuDishDetailSchema(Schema):
    """Dish details in menu context"""
    id = fields.Int()
    name = fields.Str()
    price = fields.Decimal(as_string=True)
    category = fields.Str(allow_none=True)
    photo_url = fields.Str(allow_none=True)
    is_active = fields.Bool()

class MenuDishResponseSchema(Schema):
    """Schema for dish in menu with position"""
    dish_id = fields.Int()
    order_position = fields.Int()
    dish = fields.Nested(MenuDishDetailSchema)

class MenuResponseSchema(Schema):
    """Schema for menu response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    dishes = fields.List(fields.Nested(MenuDishResponseSchema))  # ✅ ESTRUCTURADO
    dish_count = fields.Method("get_dish_count")  # ✅ AGREGAR
    total_price = fields.Method("get_total_price")  # ✅ AGREGAR
    
    def get_dish_count(self, obj):
        return len(obj.dishes) if hasattr(obj, 'dishes') else 0
    
    def get_total_price(self, obj):
        if not hasattr(obj, 'dishes'):
            return 0
        return sum(d.dish.price for d in obj.dishes if d.dish.price)
```

### Fase 3: Quotation Nested Data
```python
# app/quotations/schemas/quotation_schema.py
class QuotationClientSchema(Schema):
    """Client info in quotation"""
    id = fields.Int()
    name = fields.Str()
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)

class QuotationMenuSchema(Schema):
    """Menu info in quotation"""
    id = fields.Int()
    name = fields.Str()
    dish_count = fields.Int()

class QuotationItemResponseSchema(Schema):
    """Schema for quotation item"""
    id = fields.Int()
    dish_id = fields.Int(allow_none=True)
    item_name = fields.Str()
    description = fields.Str(allow_none=True)
    quantity = fields.Int()
    unit_price = fields.Decimal(as_string=True)
    subtotal = fields.Decimal(as_string=True)

class QuotationResponseSchema(Schema):
    """Schema for quotation response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    client_id = fields.Int(allow_none=True)
    menu_id = fields.Int(allow_none=True)
    quotation_number = fields.Str(dump_only=True)
    event_date = fields.Date(allow_none=True)
    number_of_people = fields.Int(allow_none=True)
    total_price = fields.Decimal(as_string=False, dump_only=True)
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    terms_and_conditions = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    sent_at = fields.DateTime(dump_only=True, allow_none=True)
    responded_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Nested data
    client = fields.Nested(QuotationClientSchema, allow_none=True)  # ✅ AGREGAR
    menu = fields.Nested(QuotationMenuSchema, allow_none=True)  # ✅ AGREGAR
    items = fields.List(fields.Nested(QuotationItemResponseSchema))  # ✅ ESTRUCTURADO
```

### Fase 4: Appointment Nested Data
```python
# app/appointments/schemas/appointment_schema.py
class AppointmentClientSchema(Schema):
    """Client info in appointment"""
    id = fields.Int()
    name = fields.Str()
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)

class AppointmentResponseSchema(Schema):
    """Schema for appointment response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    client_id = fields.Int(allow_none=True)
    title = fields.Str()
    description = fields.Str(allow_none=True)
    scheduled_at = fields.DateTime()
    duration_minutes = fields.Int()
    location = fields.Str(allow_none=True)
    meeting_url = fields.Str(allow_none=True)
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    cancellation_reason = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    cancelled_at = fields.DateTime(dump_only=True, allow_none=True)
    completed_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Nested and calculated
    client = fields.Nested(AppointmentClientSchema, allow_none=True)  # ✅ AGREGAR
    end_time = fields.Method("get_end_time")  # ✅ AGREGAR
    
    def get_end_time(self, obj):
        if obj.scheduled_at and obj.duration_minutes:
            from datetime import timedelta
            return obj.scheduled_at + timedelta(minutes=obj.duration_minutes)
        return None
```

---

## ⚠️ CONSIDERACIONES IMPORTANTES

1. **Lazy Loading vs Eager Loading:**
   - Nested data requiere JOINs en queries
   - Puede impactar performance si no se optimiza
   - Considerar usar `joinedload()` en SQLAlchemy

2. **Paginación:**
   - Todos los list endpoints deben devolver metadata de paginación:
   ```json
   {
     "data": [...],
     "pagination": {
       "page": 1,
       "per_page": 20,
       "total": 150,
       "pages": 8
     }
   }
   ```

3. **Circular References:**
   - Cuidado con nested schemas que referencian entre sí
   - Usar `only=[]` para limitar campos en nested

4. **Performance:**
   - Considerar crear versiones "light" y "full" de schemas
   - List endpoints → datos básicos
   - Detail endpoints → datos completos con nested

---

## ✅ TESTING REQUIREMENTS

Después de implementar cambios, verificar:

1. ✅ Todos los unit tests actualizados
2. ✅ Tests de serialización para nested schemas
3. ✅ Tests de performance (queries N+1)
4. ✅ Validación manual de cada endpoint
5. ✅ Actualizar API_DOCUMENTATION.md con ejemplos reales

---

**Siguiente paso:** ¿Quieres que implemente estos cambios en orden de prioridad?
