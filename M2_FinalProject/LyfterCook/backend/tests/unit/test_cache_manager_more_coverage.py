import json


class _BoomRedis:
    def __init__(self, *args, **kwargs):
        pass

    def ping(self):
        raise RuntimeError("no redis")


class _RedisWithBrokenOps:
    def __init__(self, *args, **kwargs):
        pass

    def ping(self):
        return True

    def get(self, key):
        return "not-json"

    def setex(self, key, ttl, value):
        raise RuntimeError("set failed")

    def delete(self, *keys):
        raise RuntimeError("delete failed")

    def keys(self, pattern):
        raise RuntimeError("keys failed")

    def exists(self, key):
        raise RuntimeError("exists failed")

    def flushdb(self):
        raise RuntimeError("flush failed")

    def ttl(self, key):
        raise RuntimeError("ttl failed")


def test_cache_manager_connect_failure_disables_cache(monkeypatch):
    import app.core.cache_manager as cm

    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: _BoomRedis())
    cm._cache_instance = None

    cache = cm.CacheManager()
    assert cache.enabled is False

    # All ops should be safe when disabled
    assert cache.get("k") is None
    assert cache.set("k", {"x": 1}) is False
    assert cache.delete("k") is False
    assert cache.delete_pattern("k*") == 0
    assert cache.exists("k") is False
    assert cache.flush_all() is False
    assert cache.get_ttl("k") == -2


def test_cache_manager_format_key_with_and_without_prefix(monkeypatch):
    import app.core.cache_manager as cm

    # Patch redis.Redis so we don't hit network.
    from tests.unit.test_hotspot_cache_manager import _FakeRedis

    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: _FakeRedis())
    cm._cache_instance = None

    cache = cm.CacheManager()
    assert cache.enabled is True

    cm.settings.REDIS_KEY_PREFIX = "pfx"
    assert cache._format_key("abc") == "pfx:abc"

    cm.settings.REDIS_KEY_PREFIX = ""
    assert cache._format_key("abc") == "abc"


def test_cache_manager_get_handles_json_decode_error(monkeypatch):
    import app.core.cache_manager as cm

    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: _RedisWithBrokenOps())
    cm._cache_instance = None

    cache = cm.CacheManager()
    assert cache.enabled is True
    assert cache.get("k") is None


def test_cache_manager_methods_handle_redis_exceptions(monkeypatch):
    import app.core.cache_manager as cm

    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: _RedisWithBrokenOps())
    cm._cache_instance = None

    cache = cm.CacheManager()
    assert cache.enabled is True

    # set should swallow exception
    assert cache.set("k", {"x": 1}, ttl=1) is False
    # delete should swallow exception
    assert cache.delete("k") is False
    # delete_pattern should swallow exception
    assert cache.delete_pattern("k*") == 0
    # exists should swallow exception
    assert cache.exists("k") is False
    # flush_all should swallow exception
    assert cache.flush_all() is False
    # get_ttl should swallow exception
    assert cache.get_ttl("k") == -2


def test_cache_manager_set_serializes_datetime_via_default_str(monkeypatch):
    import app.core.cache_manager as cm
    from datetime import datetime

    from tests.unit.test_hotspot_cache_manager import _FakeRedis

    fake_redis = _FakeRedis()
    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: fake_redis)
    cm._cache_instance = None

    cache = cm.CacheManager()
    assert cache.enabled is True

    payload = {"when": datetime(2026, 1, 3, 12, 0, 0)}
    assert cache.set("k", payload, ttl=60) is True

    # Under the hood, it should be JSON-dumped with datetime coerced to string
    raw = fake_redis.get(cache._format_key("k"))
    assert isinstance(raw, str)
    decoded = json.loads(raw)
    assert "when" in decoded
