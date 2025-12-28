"""Targeted unit tests for chef repository/service.

Testing scope only: uses real DB session fixture and patches cache to avoid Redis.
"""

from __future__ import annotations

import pytest

from app.auth.models.user_model import User, UserRole
from app.chefs.repositories.chef_repository import ChefRepository
from app.chefs.services.chef_service import ChefService


class _InMemoryCache:
    def __init__(self):
        self.enabled = True
        self._store: dict[str, object] = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value, ttl: int = 3600):
        self._store[key] = value
        return True

    def delete(self, key: str):
        return self._store.pop(key, None) is not None

    def delete_pattern(self, pattern: str):
        # Minimal pattern support for tests.
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys = [k for k in list(self._store.keys()) if k.startswith(prefix)]
        else:
            keys = [k for k in list(self._store.keys()) if k == pattern]
        for k in keys:
            self._store.pop(k, None)
        return len(keys)


@pytest.fixture()
def chef_service(db_session, monkeypatch):
    # Patch caching to be in-memory for ChefService/CacheHelper.
    import app.core.cache_manager as cm

    fake_cache = _InMemoryCache()
    monkeypatch.setattr(cm, "get_cache", lambda: fake_cache)

    # Also patch invalidate_cache helper (still uses get_cache internally, but keep deterministic).
    monkeypatch.setattr(cm, "invalidate_cache", lambda pattern: 0)

    repo = ChefRepository(db_session)
    return ChefService(repo)


def _create_user(db_session, *, username: str, email: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash="x",
        role=UserRole.CHEF,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_chef_repository_crud(db_session):
    repo = ChefRepository(db_session)

    user = _create_user(db_session, username="chef_repo", email="chef_repo@test.com")

    chef = repo.create(
        {
            "user_id": user.id,
            "bio": "bio",
            "specialty": "Italian",
            "phone": "123",
            "location": "NY",
            "is_active": True,
        }
    )

    assert chef.id is not None
    assert repo.get_by_id(chef.id).id == chef.id
    assert repo.get_by_user_id(user.id).id == chef.id
    assert repo.exists_by_user_id(user.id) is True

    updated = repo.update(chef, {"location": "LA", "bio": "new"})
    assert updated.location == "LA"
    assert updated.bio == "new"

    active = repo.get_all(active_only=True)
    assert any(c.id == chef.id for c in active)

    repo.delete(chef)
    assert repo.get_by_id(chef.id) is None


def test_chef_service_create_update_activate_deactivate(chef_service, db_session):
    user = _create_user(db_session, username="chef_svc", email="chef_svc@test.com")

    created = chef_service.create_profile(
        user.id,
        {"bio": "b", "specialty": "Mexican", "phone": "1", "location": "CDMX"},
    )
    assert created.user_id == user.id

    updated = chef_service.update_profile(user.id, {"location": "GDL", "bio": None, "phone": "2"})
    assert updated.location == "GDL"
    assert updated.phone == "2"

    deactivated = chef_service.deactivate_profile(user.id)
    assert deactivated.is_active is False

    activated = chef_service.activate_profile(user.id)
    assert activated.is_active is True


def test_chef_service_duplicate_profile_raises(chef_service, db_session):
    user = _create_user(db_session, username="chef_dup", email="chef_dup@test.com")
    chef_service.create_profile(user.id, {"bio": "b"})

    with pytest.raises(ValueError):
        chef_service.create_profile(user.id, {"bio": "b2"})
