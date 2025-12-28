"""Targeted unit tests for cache manager behavior.

Testing scope only: exercises app.core.cache_manager without requiring real Redis.
"""

from __future__ import annotations

import fnmatch

import pytest


class _FakeRedis:
    def __init__(self, *args, **kwargs):
        self._store: dict[str, str] = {}
        self._ttl: dict[str, int] = {}

    def ping(self):
        return True

    def get(self, key: str):
        return self._store.get(key)

    def setex(self, key: str, ttl: int, value: str):
        self._store[key] = value
        self._ttl[key] = int(ttl)
        return True

    def delete(self, *keys: str):
        deleted = 0
        for key in keys:
            if key in self._store:
                deleted += 1
                self._store.pop(key, None)
                self._ttl.pop(key, None)
        return deleted

    def keys(self, pattern: str):
        return [k for k in list(self._store.keys()) if fnmatch.fnmatch(k, pattern)]

    def exists(self, key: str):
        return 1 if key in self._store else 0

    def flushdb(self):
        self._store.clear()
        self._ttl.clear()
        return True

    def ttl(self, key: str):
        if key not in self._store:
            return -2
        return self._ttl.get(key, -1)


@pytest.fixture()
def cache_manager(monkeypatch):
    # Patch redis.Redis used by CacheManager so it never touches the network.
    import app.core.cache_manager as cm

    monkeypatch.setattr(cm.redis, "Redis", lambda **kwargs: _FakeRedis())

    # Ensure key prefix is stable (conftest already sets REDIS_KEY_PREFIX, but settings is imported).
    cm.settings.REDIS_KEY_PREFIX = "lyftercook:test"

    return cm.CacheManager()


def test_cache_manager_set_get_delete(cache_manager):
    assert cache_manager.enabled is True

    payload = {"a": 1, "b": "two"}
    assert cache_manager.set("k1", payload, ttl=123) is True

    # get should return de-serialized JSON.
    assert cache_manager.get("k1") == payload

    assert cache_manager.exists("k1") is True
    assert cache_manager.get_ttl("k1") == 123

    assert cache_manager.delete("k1") is True
    assert cache_manager.get("k1") is None
    assert cache_manager.exists("k1") is False


def test_cache_manager_delete_pattern(cache_manager):
    cache_manager.set("route:public:chefs:/public/chefs", {"ok": True}, ttl=60)
    cache_manager.set("route:public:dishes:/public/dishes/1", {"ok": True}, ttl=60)
    cache_manager.set("unrelated", {"ok": True}, ttl=60)

    deleted = cache_manager.delete_pattern("route:public:*")
    assert deleted == 2

    assert cache_manager.get("unrelated") == {"ok": True}


def test_cached_decorator_caches_none(monkeypatch):
    import app.core.cache_manager as cm

    # Use a fake cache instance behind get_cache() to avoid Redis.
    fake_cache = type(
        "FakeCache",
        (),
        {
            "enabled": True,
            "_store": {},
            "get": lambda self, k: self._store.get(k),
            "set": lambda self, k, v, ttl=3600: self._store.__setitem__(k, v) or True,
        },
    )()

    monkeypatch.setattr(cm, "get_cache", lambda: fake_cache)

    calls = {"n": 0}

    @cm.cached(key_prefix="x:y", ttl=60)
    def maybe(value):
        calls["n"] += 1
        return None if value == "missing" else {"value": value}

    assert maybe("missing") is None
    assert maybe("missing") is None
    # Under the decorator, None should be cached to avoid repeated function calls.
    assert calls["n"] == 1
