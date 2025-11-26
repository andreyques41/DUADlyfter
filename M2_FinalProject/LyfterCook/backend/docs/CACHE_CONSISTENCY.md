# Cache Consistency Strategy

## Problem Statement

When caching function results, we must ensure that the **cached data format** matches the **API response format** to avoid frontend inconsistencies.

---

## Solution: Schema-First Caching

### ✅ Correct Approach (Current Implementation)

**Principle:** Cache the **serialized schema output**, not the raw model object.

```python
# Service Layer
from app.auth.schemas import UserResponseSchema

@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    user = self.user_repo.get_by_id(user_id)  # Get ORM object
    if user:
        schema = UserResponseSchema()
        return schema.dump(user)  # ✅ Cache serialized dict
    return None
```

**Why this works:**
1. Same schema used in controller and service
2. Guarantees identical format (datetime, enums, computed fields)
3. Frontend receives consistent JSON structure

---

## Flow Diagram

### Without Cache
```
Request → Controller → Service → Repository → Database
                                               ↓
                                          User ORM object
                                               ↓
                                    UserResponseSchema.dump()
                                               ↓
                                          JSON dict
                                               ↓
                                    success_response()
                                               ↓
                                          Frontend
```

### With Cache (First Call - MISS)
```
Request → Controller → Service → @cached decorator
                                      ↓
                                 Cache MISS
                                      ↓
                              Repository → Database
                                      ↓
                                 User ORM object
                                      ↓
                           UserResponseSchema.dump()
                                      ↓
                                  JSON dict
                                      ↓
                            Redis SET (cache dict)
                                      ↓
                              Return dict to controller
                                      ↓
                            success_response()
                                      ↓
                                  Frontend
```

### With Cache (Second Call - HIT)
```
Request → Controller → Service → @cached decorator
                                      ↓
                                 Cache HIT
                                      ↓
                             Redis GET (cached dict)
                                      ↓
                              Return dict directly
                                      ↓
                            success_response()
                                      ↓
                                  Frontend
```

**Key Point:** Both paths return the **same dict format** because both use `UserResponseSchema.dump()`.

---

## Format Comparison

### UserResponseSchema Output
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "chef",
  "is_active": true,
  "created_at": "2025-11-26T10:30:00",
  "updated_at": "2025-11-26T10:30:00"
}
```

### Cached Value (in Redis)
```
KEY: user:id:1
VALUE: {"id":1,"username":"john_doe","email":"john@example.com","role":"chef","is_active":true,"created_at":"2025-11-26T10:30:00","updated_at":"2025-11-26T10:30:00"}
TTL: 600 seconds
```

### API Response (Both Cached & Uncached)
```json
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "chef",
    "is_active": true,
    "created_at": "2025-11-26T10:30:00",
    "updated_at": "2025-11-26T10:30:00"
  },
  "message": "Success"
}
```

**✅ Identical in all cases**

---

## Common Pitfalls to Avoid

### ❌ Bad: Caching ORM Objects
```python
@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[User]:
    return self.user_repo.get_by_id(user_id)  # ❌ Returns User object
    # Problem: ORM objects can't be JSON serialized
```

**Error:**
```
TypeError: Object of type User is not JSON serializable
```

---

### ❌ Bad: Using to_dict() Instead of Schema
```python
@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    user = self.user_repo.get_by_id(user_id)
    if user:
        return user.to_dict()  # ❌ May be inconsistent with schema
    return None
```

**Problem:**
- `to_dict()` is manual → prone to errors
- `UserResponseSchema` may have transformations/validations not in `to_dict()`
- If schema changes, `to_dict()` may not match

**Example inconsistency:**
```python
# Schema adds computed field
class UserResponseSchema(Schema):
    display_name = fields.Method("get_display_name")
    
    def get_display_name(self, obj):
        return f"{obj.username} ({obj.role.value})"

# to_dict() doesn't include this ❌
def to_dict(self):
    return {
        'id': self.id,
        'username': self.username,
        # Missing: 'display_name'
    }
```

**Result:**
- Cached response: `{"id": 1, "username": "john"}` (no display_name)
- Non-cached response: `{"id": 1, "username": "john", "display_name": "john (chef)"}` ❌ INCONSISTENT

---

### ❌ Bad: Serializing in Controller After Cache
```python
# Service
@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[User]:
    return self.user_repo.get_by_id(user_id)  # Returns User object

# Controller
def get_current_user():
    user = auth_service.get_user_by_id(g.user_id)
    schema = UserResponseSchema()
    user_data = schema.dump(user)  # ❌ Can't dump if user is dict from cache
    return success_response(user_data)
```

**Problem:**
- First call: `user` is User object → `schema.dump()` works ✅
- Second call: `user` is dict from cache → `schema.dump()` expects object ❌

**Error:**
```
AttributeError: 'dict' object has no attribute 'role'
```

---

## Best Practices

### ✅ 1. Always Cache Serialized Data
```python
@cached(key_prefix='resource', ttl=600)
def get_resource(self, id: int) -> Optional[Dict]:
    obj = self.repo.get_by_id(id)
    if obj:
        schema = ResourceSchema()
        return schema.dump(obj)  # ✅ Cache dict
    return None
```

---

### ✅ 2. Use Same Schema Everywhere
```python
# Service
from app.auth.schemas import UserResponseSchema  # ← Same import

@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    user = self.user_repo.get_by_id(user_id)
    if user:
        schema = UserResponseSchema()  # ✅ Same schema
        return schema.dump(user)
    return None

# Controller
from app.auth.schemas import UserResponseSchema  # ← Same import

def get_current_user():
    user_dict = auth_service.get_user_by_id(g.user_id)  # Already serialized
    return success_response(user_dict)  # ✅ No re-serialization needed
```

---

### ✅ 3. Document Return Types
```python
@cached(key_prefix='user:id', ttl=600)
def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    """
    Get user by ID.
    
    Returns:
        Dict serialized with UserResponseSchema, NOT User object.
        Format matches API response exactly.
    """
    ...
```

---

## Testing Consistency

### Unit Test Example
```python
def test_cache_format_matches_api_response():
    # Without cache
    user_service = AuthService(user_repo)
    user_dict_1 = user_service.get_user_by_id(1)
    
    # With cache (second call)
    user_dict_2 = user_service.get_user_by_id(1)
    
    # Should be identical
    assert user_dict_1 == user_dict_2
    
    # Should match schema format
    schema = UserResponseSchema()
    user_obj = user_repo.get_by_id(1)
    expected = schema.dump(user_obj)
    
    assert user_dict_1 == expected
    assert user_dict_2 == expected
```

---

## Summary

| Approach | Consistency | Performance | Maintainability |
|----------|-------------|-------------|-----------------|
| Cache schema.dump() | ✅ Always consistent | ⚡ Fast | ✅ Single source of truth |
| Cache to_dict() | ⚠️ Manual sync required | ⚡ Fast | ❌ Duplicate logic |
| Cache ORM object | ❌ Breaks serialization | ❌ N/A | ❌ N/A |
| No cache | ✅ Consistent | 🐌 Slow | ✅ Simple |

**Recommendation:** Always cache `schema.dump()` output for consistency and performance.
