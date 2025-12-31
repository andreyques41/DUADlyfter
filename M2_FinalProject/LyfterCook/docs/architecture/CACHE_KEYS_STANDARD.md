# 🔑 Cache Keys Standard - LyfterCook

## 📋 Industry Standard Pattern

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

---

## 🎯 Cache Key Examples

### Service-Level Cache (Database Objects)

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

### Auth Cache

```
user:auth:123:v1                     # User authentication data for ID 123
```

### Route-Level Cache (HTTP Responses)

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

---

## 🛠️ Implementation

### 1. CacheHelper Pattern (Service-Level)

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

### 2. @cached Decorator (Method-Level)

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

### 3. @cache_response Decorator (Route-Level)

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

---

## 🔄 Cache Invalidation Patterns

### Invalidate Specific Keys

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

### Invalidate with Wildcards

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

### @invalidate_on_modify Decorator

```python
from app.core.middleware.cache_decorators import invalidate_on_modify

@chef_bp.route('/profile', methods=['POST'])
@jwt_required
@invalidate_on_modify('route:public:chefs:*', 'route:chefs:*')
def create_profile():
    return chef_controller.create_profile(g.current_user)
```

---

## 📊 Cache Key Architecture Summary

| Layer | Pattern | Example | TTL |
|-------|---------|---------|-----|
| **Service** | `resource:entity:identifier:version` | `chef:profile:123:v1` | 5-10 min |
| **Auth** | `user:auth:id:version` | `user:auth:123:v1` | 10 min |
| **Route** | `route:module:endpoint` | `route:chefs:list` | 5-10 min |
| **Public** | `route:public:module:endpoint` | `route:public:chefs:list` | 5-10 min |

---

## ✅ Migration Checklist

- [x] CacheHelper: Updated `_build_cache_key()` to put version at end
- [x] Chef service: Updated all cache keys to new format
- [x] Dish service: Updated all cache keys to new format
- [x] Menu service: Updated all cache keys to new format
- [x] Auth service: Changed `user:id` → `user:auth`
- [x] Chef routes: Changed to `route:chefs:*` format
- [x] All invalidations: Updated to match new key patterns
- [x] Documentation: Updated with examples

---

## 🔍 Testing Cache Keys

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

**Last Updated:** December 18, 2025
**Version:** v1
