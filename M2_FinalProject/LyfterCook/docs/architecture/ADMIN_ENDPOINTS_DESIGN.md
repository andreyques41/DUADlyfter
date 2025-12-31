# 👑 Admin Module - Design & Implementation Guide

## 📋 Overview

Endpoints administrativos para supervisión, gestión y moderación del sistema LyfterCook.

**Estado:** 📝 Design Phase | **Prioridad:** High | **Estimado:** 5-7 días

---

## 🎯 Propósito

- **Supervisión**: Monitoreo de todos los chefs y actividades
- **Moderación**: Activar/desactivar cuentas
- **Analytics**: Métricas y estadísticas del sistema
- **Auditoría**: Tracking de acciones administrativas

---

## 🏗️ Role Hierarchy

```
👑 ADMIN → Ver/gestionar TODO el sistema + estadísticas
👨‍🍳 CHEF → Solo sus propios recursos
🌐 PUBLIC → Solo lectura de datos públicos
```

**Middleware:**
```python
@jwt_required
@admin_required  # ← Nuevo decorador (ya existe en codebase)
def admin_endpoint():
    pass
```

---

## 📍 Endpoints (8 total)

### 1. Dashboard
```http
GET /admin/dashboard
```
Estadísticas globales: total chefs, clientes, platillos, menús, cotizaciones, citas, actividad reciente.

### 2. List All Chefs (Admin View)
```http
GET /admin/chefs?page=1&status=all&search=mario&sort=created_at
```
Ver TODOS los chefs con stats (total_clients, total_dishes, etc.). Incluye email (no público).

### 3. Get Chef Details
```http
GET /admin/chefs/:id
```
Perfil completo + estadísticas detalladas + actividad reciente.

### 4. Update Chef Status
```http
PATCH /admin/chefs/:id/status
Body: { "is_active": false, "reason": "TOS violation" }
```
Activar/desactivar chef. También desactiva usuario asociado (bloquea login).

### 5. List All Users
```http
GET /admin/users?role=all&status=active
```
Gestión de usuarios del sistema (chefs + admins).

### 6. Delete User
```http
DELETE /admin/users/:id
Body: { "confirm": true, "reason": "User request" }
```
**Soft delete**. No puede eliminarse a sí mismo. Debe haber 1+ admin activo.

### 7. System Reports
```http
GET /admin/reports?report_type=activity&start_date=...&end_date=...&format=json
```
Reportes: activity, chefs, quotations. Exportable en JSON/CSV.

### 8. Audit Logs
```http
GET /admin/audit-logs?admin_id=2&action_type=deactivate_chef
```
Tracking de todas las acciones admin (quién, qué, cuándo, dónde, por qué).

---

## 🗄️ Database

**Nueva tabla:**
```sql
CREATE TABLE core.admin_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES auth.users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    reason TEXT,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_admin_logs_admin_id ON core.admin_audit_logs(admin_id);
CREATE INDEX idx_admin_logs_action ON core.admin_audit_logs(action);
CREATE INDEX idx_admin_logs_created_at ON core.admin_audit_logs(created_at DESC);
```

---

## 📂 File Structure

```
app/admin/
├── __init__.py
├── controllers/admin_controller.py
├── models/audit_log_model.py
├── repositories/admin_repository.py
├── routes/admin_routes.py
├── schemas/admin_schemas.py
└── services/admin_service.py

tests/unit/test_admin.py
```

---

## 🔒 Security & Business Rules

✅ `@admin_required` decorator (ya existe)  
✅ Audit logging automático de acciones  
✅ Soft delete (no eliminación física)  
✅ Admin no puede eliminarse a sí mismo  
✅ Siempre debe haber 1+ admin activo  
✅ Chef desactivado → usuario desactivado (no puede login)  
✅ IP address tracking  

---

## 🧪 Testing (Mínimo 14 tests)

**Unit Tests:**
```python
test_admin_required_decorator_blocks_chef()
test_admin_required_decorator_allows_admin()
test_get_dashboard_returns_statistics()
test_list_all_chefs_includes_inactive()
test_deactivate_chef_updates_user_status()
test_admin_cannot_delete_self()
test_cannot_delete_last_admin()
test_soft_delete_works()
```

**Integration Tests:**
```python
test_deactivated_chef_cannot_login()
test_audit_log_created_on_admin_action()
```

**Performance Targets:**
- Dashboard: < 500ms
- List endpoints: < 300ms

---

## 🚀 Implementation Plan

### Phase 1: Core (2-3 días)
- [ ] Crear estructura `app/admin/`
- [ ] Tabla `admin_audit_logs` en PostgreSQL
- [ ] Endpoints: dashboard, list chefs, chef details, status
- [ ] Unit tests (6 mínimo)

### Phase 2: User Management (1-2 días)
- [ ] Endpoints: list users, delete user
- [ ] Business rules (no auto-delete, 1+ admin)
- [ ] Unit tests (5 mínimo)

### Phase 3: Analytics (2 días)
- [ ] Endpoints: reports, audit logs
- [ ] Exportación CSV
- [ ] Unit tests (3 mínimo)

**Total:** 5-7 días desarrollo + testing

---

## ❓ FAQs

**¿Los admins pueden crear platillos/menús?**  
No. Solo supervisan. Para crear contenido necesitan chef profile.

**¿Qué pasa con los datos de chef desactivado?**  
Persisten pero el chef no puede hacer login. Soft delete.

**¿Admin puede modificar cotizaciones de chefs?**  
No en Phase 1. Solo pueden ver.

---

**Next Step:** Implementar Phase 1  
**Referencias:** Ver [API_DOCUMENTATION.md](../api/API_DOCUMENTATION.md) sección Admin Module para ejemplos completos de request/response.
