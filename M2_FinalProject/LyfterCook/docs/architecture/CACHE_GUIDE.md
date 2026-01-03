# 🚀 Redis Cache System Guide

Complete guide to LyfterCook's Redis-based caching system covering implementation, naming conventions, and consistency strategies.

---

## 📋 Table of Contents

1. [Implementation](#implementation)
2. [Naming Standards](#naming-standards)
3. [Consistency Strategy](#consistency-strategy)
4. [Testing](#testing)

---

<a name="implementation"></a>
## 1. Implementation

### Overview
Complete Redis-based cache system with decorators for easy integration.

### Core Components

#### `app/core/cache_manager.py`
Core cache manager with full CRUD operations:
- `get(key)` - Retrieve cached value
- `set(key, value, ttl)` - Store value with TTL
- `delete(key)` - Delete single key
- `delete_pattern(pattern)` - Delete keys by pattern
- `exists(key)` - Check if key exists
- `get_ttl(key)` - Get remaining TTL
- `flush_all()` - Clear all cache (use with caution)

**Singleton access**: `get_cache()`

#### `app/core/middleware/cache_decorators.py`
Route-level caching decorators:

**`@cache_response(ttl, key_prefix)`**
```python
@app.route('/api/chefs')
@cache_response(ttl=600, key_prefix='public_chefs')
def get_chefs():
    return jsonify(chefs)
```

**`@invalidate_on_modify(pattern)`**
```python
@app.route('/api/dishes', methods=['POST'])
@invalidate_on_modify('route:/api/dishes*')
def create_dish():
    return jsonify(dish), 201
```

### Usage Examples

#### Function-level caching (Services)
```python
from app.core.cache_manager import cached

@cached(key_prefix='user', ttl=600)
def get_user_by_id(user_id):
    # Database query
    user = db.query(User).filter_by(id=user_id).first()
    return user.to_dict()
```

#### Route-level caching (Controllers)
```python
from app.core.middleware.cache_decorators import cache_response, invalidate_on_modify

@chef_bp.route('', methods=['GET'])
@cache_response(ttl=300, key_prefix='chefs_list')
def get_all_chefs():
    chefs = ChefService.get_all()
    return jsonify({'data': chefs}), 200

@chef_bp.route('', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:/chefs*')
def create_chef():
    chef = ChefService.create(request.json)
    return jsonify({'data': chef}), 201
```

#### Manual cache management
```python
from app.core.cache_manager import get_cache, invalidate_cache

cache = get_cache()

# Store
cache.set('dishes:chef:123', dishes, ttl=600)

# Retrieve
dishes = cache.get('dishes:chef:123')

# Invalidate all dishes for a chef
invalidate_cache('dishes:chef:123:*')
```

### Currently Cached Endpoints

#### Public Endpoints (High Traffic)

| Endpoint | TTL | Key Pattern | Invalidated By | Reason |
|----------|-----|-------------|----------------|--------|
| `GET /public/chefs` | 5min | `route:/public/chefs*` | PUT /chefs/profile | Chef list changes when profiles update |
| `GET /public/chefs/:id` | 10min | `route:/public/chefs/:id` | PUT /chefs/profile | Individual chef profile updates |
| `GET /public/dishes` | 5min | `route:/public/dishes*` | POST/PUT/DELETE /dishes | Dish list/details change |
| `GET /public/dishes/:id` | 10min | `route:/public/dishes/:id` | PUT/DELETE /dishes/:id | Individual dish updates |
| `GET /public/menus` | 5min | `route:/public/menus*` | POST/PUT/DELETE /menus | Menu list changes |
| `GET /public/menus/:id` | 10min | `route:/public/menus/:id` | PUT/DELETE /menus/:id, PUT /menus/:id/dishes | Menu or its dishes updated |
| `GET /public/statistics` | 15min | `route:/public/statistics` | Any data modification | Global stats recalculated |
| `GET /public/filters` | 30min | `route:/public/filters` | Admin changes | Filter options rarely change |

**Total Cached:** 8 endpoints

### Cache Invalidation Strategy

#### Chef Profile Operations
**Triggers:** `POST /chefs/profile`, `PUT /chefs/profile`
**Invalidates:**
- `route:/public/chefs*` - Public chef listings
- `route:/chefs/:id` - Specific chef cache (if exists)

**Reason:** Profile changes must reflect in public browsing immediately.

#### Dish Operations
**Triggers:** `POST /dishes`, `PUT /dishes/:id`, `DELETE /dishes/:id`
**Invalidates:**
- `route:/public/dishes*` - Public dish listings
- `route:/public/menus*` - Menus that may contain these dishes

**Reason:** Dish availability affects menu composition and display.

#### Menu Operations
**Triggers:** `POST /menus`, `PUT /menus/:id`, `PUT /menus/:id/dishes`, `DELETE /menus/:id`
**Invalidates:**
- `route:/public/menus*` - Public menu listings
- `route:/menus/:id` - Specific menu cache

**Reason:** Menu structure or dish assignments changed.

#### Admin Operations
**Triggers:** Any `PATCH /admin/*/status` endpoint
**Invalidates:**
- Related public cache patterns
- `route:/admin/dashboard` - Dashboard statistics

**Reason:** Status changes (active/inactive) affect public visibility.

#### Cascading Invalidation

**Menu → Dishes relationship:**
- Updating a dish invalidates menus containing it
- Deleting a dish removes it from all menus and invalidates their cache

**Statistics endpoints:**
- Any data modification triggers statistics recalculation
- Cache prevents excessive computation on frequent access

### Configuration

Already configured in `.env`:
```env
REDIS_HOST=redis-19611.c265.us-east-1-2.ec2.cloud.redislabs.com
REDIS_PORT=19611
REDIS_PASSWORD=PstARfo9kPYyWLZpsqFFWcZHxcfwEwvw
REDIS_DB=0
```

### Benefits

- **Performance**: 10-100x faster than DB queries
- **Scalability**: Reduces database load
- **Flexibility**: TTL control per resource
- **Easy invalidation**: Pattern-based cleanup
- **Development**: Cache disabled if Redis unavailable

---

<a name="naming-standards"></a>
## 2. Naming Standards

### Industry Standard Pattern

```
namespace:entity:identifier:version
```

**Rationale:**
- ✅ Hierarchical (general → specific)
- ✅ Easy pattern matching: `KEYS chef:*`
- ✅ Wildcard invalidation: `chef:profile:*`
- ✅ Colon `:` is Redis standard separator
- ✅ Version at end for easy migration
- ✅ Self-documenting and readable

### Cache Key Examples

#### Service-Level Cache (Database Objects)

**Chef Module:**
```
chef:profile:123:v1                  # Chef profile with ID 123
chef:profile:user:456:v1             # Chef profile for user ID 456
chef:list:active:True:v1             # List of all active chefs
chef:list:active:False:v1            # List of all inactive chefs
```

**Dish Module:**
```
dish:detail:789:user:1:v1            # Dish ID 789 owned by user 1
dish:list:user:1:active:True:v1      # Active dishes for user 1
dish:list:chef:5:active:True:v1      # Active dishes for chef 5
```

**Menu Module:**
```
menu:detail:42:user:1:v1             # Menu ID 42 owned by user 1
menu:list:user:1:active:True:v1      # Active menus for user 1
menu:list:chef:5:active:False:v1     # Inactive menus for chef 5
```

#### Auth Cache

```
user:auth:123:v1                     # User authentication data for ID 123
```

#### Route-Level Cache (HTTP Responses)

**Public Routes:**
```
route:public:chefs:list              # GET /public/chefs
route:public:chefs:profile           # GET /public/chefs/{id}
route:public:search                  # GET /public/search
route:public:filters                 # GET /public/filters
route:public:menus:detail            # GET /public/menus/{id}
route:public:dishes:detail           # GET /public/dishes/{id}
```

**Chef Routes:**
```
route:chefs:list                     # GET /chefs
route:chefs:profile                  # GET /chefs/{id}
```

### Implementation Patterns

#### CacheHelper Pattern (Service-Level)

```python
from app.core.middleware.cache_helper import CacheHelper

class ChefService:
    def __init__(self):
        # Initialize with resource name and version
        self.cache_helper = CacheHelper(resource_name="chef", version="v1")
    
    def get_profile_by_id_cached(self, chef_id: int) -> Optional[dict]:
        return self.cache_helper.get_or_set(
            cache_key=f"profile:{chef_id}",      # Becomes: chef:profile:123:v1
            fetch_func=lambda: self.repo.get_by_id(chef_id),
            schema_class=ChefResponseSchema,
            ttl=600
        )
    
    def get_all_profiles_cached(self, active_only: bool = True) -> List[dict]:
        return self.cache_helper.get_or_set(
            cache_key=f"list:active:{active_only}",  # Becomes: chef:list:active:True:v1
            fetch_func=lambda: self.repo.get_all(active_only),
            schema_class=ChefResponseSchema,
            ttl=300,
            many=True
        )
```

#### @cached Decorator (Method-Level)

```python
from app.core.cache_manager import cached

class AuthService:
    @cached(key_prefix='user:auth', ttl=600)  # Will append args: user:auth:123
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        user = self.user_repo.get_by_id(user_id)
        if user:
            return UserSchema().dump(user)
        return None
```

#### @cache_response Decorator (Route-Level)

**IMPORTANT:** The decorator automatically adds `route:` prefix, so don't include it in `key_prefix`.

```python
from app.core.middleware.cache_decorators import cache_response

# ✅ CORRECT - decorator adds 'route:' prefix automatically
@chef_bp.route('', methods=['GET'])
@cache_response(ttl=300, key_prefix='chefs:list')  # Becomes: route:chefs:list
def get_all_chefs():
    return chef_controller.get_all_chefs()

@public_bp.route('/chefs/<int:chef_id>', methods=['GET'])
@cache_response(ttl=600, key_prefix='public:chefs:profile')  # Becomes: route:public:chefs:profile
def get_chef_profile(chef_id: int):
    return PublicController.get_chef_profile(chef_id)

# ❌ WRONG - This creates route:route:chefs:list (duplicate)
@cache_response(ttl=300, key_prefix='route:chefs:list')  # DON'T DO THIS
```

### Cache Invalidation Patterns

#### Invalidate Specific Keys

```python
# Invalidate single profile
self.cache_helper.invalidate(f"profile:{chef_id}")  # chef:profile:123:v1

# Invalidate multiple specific keys
self.cache_helper.invalidate(
    f"profile:{chef_id}",
    f"profile:user:{user_id}",
    "list:active:True",
    "list:active:False"
)
```

#### Invalidate with Wildcards

```python
# Invalidate ALL chef caches
self.cache_helper.invalidate_pattern("*")  # chef:*:v1

# Invalidate all user's dishes
self.cache_helper.invalidate(f"*:user:{user_id}:*")  # dish:*:user:123:*:v1

# Invalidate route caches
from app.core.cache_manager import invalidate_cache
invalidate_cache('route:public:chefs:*')
invalidate_cache('route:chefs:*')
```

#### @invalidate_on_modify Decorator

```python
from app.core.middleware.cache_decorators import invalidate_on_modify

@chef_bp.route('/profile', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:public:chefs:*', 'route:chefs:*')
def create_profile():
    return chef_controller.create_profile(g.current_user)
```

### Cache Key Architecture Summary

| Layer | Pattern | Example | TTL |
|-------|---------|---------|-----|
| **Service** | `resource:entity:identifier:version` | `chef:profile:123:v1` | 5-10 min |
| **Auth** | `user:auth:id:version` | `user:auth:123:v1` | 10 min |
| **Route** | `route:module:endpoint` | `route:chefs:list` | 5-10 min |
| **Public** | `route:public:module:endpoint` | `route:public:chefs:list` | 5-10 min |

### Redis Commands

```bash
# List all cache keys
redis-cli KEYS "*"

# List by namespace
redis-cli KEYS "chef:*"
redis-cli KEYS "dish:*"
redis-cli KEYS "menu:*"
redis-cli KEYS "user:*"
redis-cli KEYS "route:*"

# List specific patterns
redis-cli KEYS "chef:profile:*"
redis-cli KEYS "route:public:*"
redis-cli KEYS "*:user:1:*"

# Get specific key
redis-cli GET "chef:profile:123:v1"

# Clear all caches (DANGEROUS!)
redis-cli FLUSHDB
```

---

<a name="consistency-strategy"></a>
## 3. Consistency Strategy

### Problem Statement

When caching function results, we must ensure that the **cached data format** matches the **API response format** to avoid frontend inconsistencies.

### Solution: Schema-First Caching

#### ✅ Correct Approach (Current Implementation)

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

### Flow Diagrams

#### Without Cache
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

#### With Cache (First Call - MISS)
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

#### With Cache (Second Call - HIT)
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

### Format Comparison

#### UserResponseSchema Output
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

#### Cached Value (in Redis)
```
KEY: user:id:1
VALUE: {"id":1,"username":"john_doe","email":"john@example.com","role":"chef","is_active":true,"created_at":"2025-11-26T10:30:00","updated_at":"2025-11-26T10:30:00"}
TTL: 600 seconds
```

#### API Response (Both Cached & Uncached)
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

### Common Pitfalls to Avoid

#### ❌ Bad: Caching ORM Objects
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

#### ❌ Bad: Using to_dict() Instead of Schema
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

#### ❌ Bad: Serializing in Controller After Cache
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

### Best Practices

#### ✅ Always Cache Serialized Data
```python
@cached(key_prefix='resource', ttl=600)
def get_resource(self, id: int) -> Optional[Dict]:
    obj = self.repo.get_by_id(id)
    if obj:
        schema = ResourceSchema()
        return schema.dump(obj)  # ✅ Cache dict
    return None
```

#### ✅ Use Same Schema Everywhere
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

#### ✅ Document Return Types
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

### Testing Consistency

#### Unit Test Example
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

### Summary Table

| Approach | Consistency | Performance | Maintainability |
|----------|-------------|-------------|-----------------|
| Cache schema.dump() | ✅ Always consistent | ⚡ Fast | ✅ Single source of truth |
| Cache to_dict() | ⚠️ Manual sync required | ⚡ Fast | ❌ Duplicate logic |
| Cache ORM object | ❌ Breaks serialization | ❌ N/A | ❌ N/A |
| No cache | ✅ Consistent | 🐌 Slow | ✅ Simple |

**Recommendation:** Always cache `schema.dump()` output for consistency and performance.

---

<a name="testing"></a>
## 4. Testing

### Setup

Install dependencies:
```bash
pip install redis==5.2.0
```

### Test Script

Run the comprehensive test suite:
```bash
cd backend
python test_cache.py
```

Expected output:
- ✅ Basic operations (set, get, delete, pattern)
- ✅ Decorator functionality
- ✅ Complex data structures
- ✅ Performance comparison (cache ~10-100x faster)

### Manual Testing

```python
from app.core.cache_manager import get_cache

cache = get_cache()

# Test set/get
cache.set('test:key', {'data': 'value'}, ttl=60)
result = cache.get('test:key')
print(result)  # {'data': 'value'}

# Test pattern delete
cache.set('test:key:1', 'val1', ttl=60)
cache.set('test:key:2', 'val2', ttl=60)
cache.delete_pattern('test:key:*')
print(cache.get('test:key:1'))  # None
```

---

**Last Updated:** January 2, 2026  
**Version:** v1
