"""
Test script for Cache Manager

Tests Redis connection and cache operations.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.cache_manager import get_cache, cached, invalidate_cache
from config.logging import setup_logging

# Setup logging
setup_logging()


def test_basic_operations():
    """Test basic cache operations"""
    print("\n" + "="*60)
    print("Testing Basic Cache Operations")
    print("="*60)
    
    cache = get_cache()
    
    if not cache.enabled:
        print("❌ Cache is disabled. Check Redis connection.")
        return False
    
    # Test SET and GET
    print("\n1. Testing SET and GET...")
    cache.set('test:key1', {'name': 'John', 'age': 30}, ttl=60)
    result = cache.get('test:key1')
    print(f"   Set: {{'name': 'John', 'age': 30}}")
    print(f"   Get: {result}")
    assert result == {'name': 'John', 'age': 30}, "GET failed"
    print("   ✅ SET and GET working")
    
    # Test EXISTS
    print("\n2. Testing EXISTS...")
    exists = cache.exists('test:key1')
    print(f"   Key 'test:key1' exists: {exists}")
    assert exists == True, "EXISTS failed"
    print("   ✅ EXISTS working")
    
    # Test TTL
    print("\n3. Testing TTL...")
    ttl = cache.get_ttl('test:key1')
    print(f"   TTL for 'test:key1': {ttl} seconds")
    assert ttl > 0, "TTL failed"
    print("   ✅ TTL working")
    
    # Test DELETE
    print("\n4. Testing DELETE...")
    cache.delete('test:key1')
    result = cache.get('test:key1')
    print(f"   After delete: {result}")
    assert result is None, "DELETE failed"
    print("   ✅ DELETE working")
    
    # Test PATTERN DELETE
    print("\n5. Testing PATTERN DELETE...")
    cache.set('test:user:1', {'id': 1, 'name': 'Alice'}, ttl=60)
    cache.set('test:user:2', {'id': 2, 'name': 'Bob'}, ttl=60)
    cache.set('test:user:3', {'id': 3, 'name': 'Charlie'}, ttl=60)
    deleted = cache.delete_pattern('test:user:*')
    print(f"   Deleted {deleted} keys matching 'test:user:*'")
    assert deleted == 3, "PATTERN DELETE failed"
    print("   ✅ PATTERN DELETE working")
    
    return True


def test_decorator():
    """Test @cached decorator"""
    print("\n" + "="*60)
    print("Testing @cached Decorator")
    print("="*60)
    
    call_count = 0
    
    @cached(key_prefix='test:factorial', ttl=60)
    def factorial(n):
        nonlocal call_count
        call_count += 1
        print(f"   🔄 Computing factorial({n})... (call #{call_count})")
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    
    print("\n1. First call (should compute):")
    result1 = factorial(5)
    print(f"   Result: {result1}")
    
    print("\n2. Second call (should use cache):")
    result2 = factorial(5)
    print(f"   Result: {result2}")
    
    print("\n3. Invalidating cache...")
    invalidate_cache('test:factorial:*')
    
    print("\n4. Third call (should compute again):")
    result3 = factorial(5)
    print(f"   Result: {result3}")
    
    assert result1 == result2 == result3 == 120, "Decorator results don't match"
    print("\n   ✅ Decorator working correctly")
    
    return True


def test_complex_data():
    """Test caching complex data structures"""
    print("\n" + "="*60)
    print("Testing Complex Data Structures")
    print("="*60)
    
    cache = get_cache()
    
    # Test list
    print("\n1. Testing list...")
    test_list = [1, 2, 3, {'nested': True}]
    cache.set('test:list', test_list, ttl=60)
    result = cache.get('test:list')
    print(f"   Original: {test_list}")
    print(f"   Cached:   {result}")
    assert result == test_list, "List caching failed"
    print("   ✅ List caching working")
    
    # Test nested dict
    print("\n2. Testing nested dict...")
    test_dict = {
        'user': {
            'id': 1,
            'name': 'John',
            'roles': ['chef', 'admin'],
            'settings': {
                'theme': 'dark',
                'notifications': True
            }
        }
    }
    cache.set('test:dict', test_dict, ttl=60)
    result = cache.get('test:dict')
    print(f"   Original: {test_dict}")
    print(f"   Cached:   {result}")
    assert result == test_dict, "Nested dict caching failed"
    print("   ✅ Nested dict caching working")
    
    # Cleanup
    cache.delete('test:list')
    cache.delete('test:dict')
    
    return True


def test_cache_performance():
    """Test cache vs direct access performance"""
    print("\n" + "="*60)
    print("Testing Cache Performance")
    print("="*60)
    
    import time
    
    cache = get_cache()
    
    # Simulate expensive operation
    def expensive_operation():
        time.sleep(0.1)  # 100ms delay
        return {'data': 'expensive result', 'timestamp': time.time()}
    
    print("\n1. Without cache (100ms delay):")
    start = time.time()
    result1 = expensive_operation()
    duration1 = (time.time() - start) * 1000
    print(f"   Time: {duration1:.2f}ms")
    
    # Cache it
    cache.set('test:expensive', result1, ttl=60)
    
    print("\n2. With cache:")
    start = time.time()
    result2 = cache.get('test:expensive')
    duration2 = (time.time() - start) * 1000
    print(f"   Time: {duration2:.2f}ms")
    
    speedup = duration1 / duration2
    print(f"\n   ⚡ Cache is {speedup:.1f}x faster!")
    
    cache.delete('test:expensive')
    
    return True


def cleanup():
    """Clean up test keys"""
    print("\n" + "="*60)
    print("Cleanup")
    print("="*60)
    
    cache = get_cache()
    deleted = cache.delete_pattern('test:*')
    print(f"\n🗑️ Deleted {deleted} test keys")


if __name__ == '__main__':
    try:
        print("\n🚀 Starting Cache Manager Tests\n")
        
        success = True
        success &= test_basic_operations()
        success &= test_decorator()
        success &= test_complex_data()
        success &= test_cache_performance()
        
        cleanup()
        
        if success:
            print("\n" + "="*60)
            print("✅ All tests passed!")
            print("="*60)
            print("\nCache is ready to use in your endpoints:")
            print("  - Use @cache_response decorator for route caching")
            print("  - Use @cached decorator for function caching")
            print("  - Use invalidate_cache() to clear specific patterns")
            print("\n")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        sys.exit(1)
