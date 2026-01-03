"""Coverage-focused tests for AdminRepository.

These tests are mock-heavy by design: they validate branching logic and output
shaping without requiring a real database.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.admin.repositories.admin_repository import AdminRepository
from app.auth.models.user_model import UserRole


_UNSET = object()


def _query_mock(*, count=_UNSET, all_=_UNSET, first=_UNSET):
    q = MagicMock()

    # Common fluent methods
    q.join.return_value = q
    q.outerjoin.return_value = q
    q.filter.return_value = q
    q.filter_by.return_value = q
    q.group_by.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q

    if count is not _UNSET:
        q.count.return_value = count
    if all_ is not _UNSET:
        q.all.return_value = all_
    if first is not _UNSET:
        q.first.return_value = first
    return q


def test_get_dashboard_statistics_builds_top_chefs_and_counts():
    db = MagicMock()

    # Order matches method calls in get_dashboard_statistics
    db.query.side_effect = [
        _query_mock(count=10),
        _query_mock(count=7),
        _query_mock(count=3),
        _query_mock(count=4),
        _query_mock(count=5),
        _query_mock(count=6),
        _query_mock(count=7),
        _query_mock(count=8),
        _query_mock(count=9),
        _query_mock(count=11),
        _query_mock(all_=[SimpleNamespace(id=1, username="chef1", total_clients=2)]),
    ]

    repo = AdminRepository(db)
    out = repo.get_dashboard_statistics()

    assert out["statistics"]["total_chefs"] == 10
    assert out["statistics"]["inactive_chefs"] == 3
    assert out["top_chefs"][0]["chef_id"] == 1


def test_get_all_chefs_covers_status_search_sort_and_order_branches():
    db = MagicMock()

    chef = SimpleNamespace(
        id=1,
        user_id=2,
        specialty="bbq",
        location="x",
        is_active=True,
        created_at=None,
    )
    row = SimpleNamespace(
        Chef=chef,
        username="u",
        email="e",
        total_clients=3,
        total_dishes=4,
    )

    q = _query_mock(count=1, all_=[row])
    db.query.return_value = q

    repo = AdminRepository(db)

    # status=active, search set, sort=username, order=asc
    data, total = repo.get_all_chefs(
        page=2,
        per_page=1,
        status="active",
        search="bob",
        sort="username",
        order="asc",
    )

    assert total == 1
    assert data[0]["id"] == 1
    assert data[0]["created_at"] is None
    q.offset.assert_called_once_with(1)


def test_get_all_chefs_inactive_and_sort_total_clients_desc_branch():
    db = MagicMock()

    chef = SimpleNamespace(
        id=1,
        user_id=2,
        specialty="bbq",
        location="x",
        is_active=False,
        created_at=None,
    )
    row = SimpleNamespace(
        Chef=chef,
        username="u",
        email="e",
        total_clients=3,
        total_dishes=4,
    )

    q = _query_mock(count=1, all_=[row])
    db.query.return_value = q

    repo = AdminRepository(db)

    data, total = repo.get_all_chefs(
        page=1,
        per_page=20,
        status="inactive",
        search=None,
        sort="total_clients",
        order="desc",
    )

    assert total == 1
    assert data[0]["is_active"] is False


def test_get_chef_details_none_when_missing():
    db = MagicMock()
    q = _query_mock(first=None)
    db.query.return_value = q

    repo = AdminRepository(db)
    assert repo.get_chef_details(123) is None


def test_get_chef_details_formats_role_and_recent_activity():
    db = MagicMock()

    chef = SimpleNamespace(
        id=9,
        user_id=5,
        bio="b",
        specialty="s",
        phone="p",
        location="l",
        is_active=True,
        created_at=datetime(2025, 1, 1),
        updated_at=None,
    )
    user = SimpleNamespace(
        id=5,
        username="u",
        email="e",
        role=UserRole.CHEF,
        last_login=None,
    )

    # query sequence inside get_chef_details
    db.query.side_effect = [
        _query_mock(first=(chef, user)),
        _query_mock(count=2),
        _query_mock(count=3),
        _query_mock(count=1),
        _query_mock(count=4),
        _query_mock(count=1),
        _query_mock(all_=[("draft", 2), ("accepted", 1)]),
        _query_mock(all_=[("scheduled", 5)]),
        _query_mock(first=SimpleNamespace(created_at=datetime(2025, 2, 1))),
        _query_mock(first=None),
    ]

    repo = AdminRepository(db)
    out = repo.get_chef_details(9)

    assert out["chef"]["id"] == 9
    assert out["chef"]["user"]["role"] == UserRole.CHEF.value
    assert out["statistics"]["total_quotations"] == 3
    assert out["recent_activity"]["last_dish_created"] == datetime(2025, 2, 1).isoformat()
    assert out["recent_activity"]["last_quotation_sent"] is None


def test_update_chef_status_handles_missing_chef_and_missing_user():
    db = MagicMock()

    repo = AdminRepository(db)

    db.get.return_value = None
    assert repo.update_chef_status(1, True) is False

    chef = SimpleNamespace(id=1, user_id=2, is_active=False)

    def _get(model, id_):
        if id_ == 1:
            return chef
        return None

    db.get.side_effect = _get
    assert repo.update_chef_status(1, True) is True
    assert chef.is_active is True
    db.commit.assert_called_once()


def test_get_all_users_covers_role_filters_status_search_and_role_string_branch():
    db = MagicMock()

    user1 = SimpleNamespace(
        id=1,
        username="a",
        email="a@a.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2025, 1, 1),
        last_login=None,
    )
    user2 = SimpleNamespace(
        id=2,
        username="b",
        email="b@b.com",
        role="chef",  # exercise the else branch (no .value)
        is_active=False,
        created_at=datetime(2025, 1, 2),
        last_login=datetime(2025, 1, 3),
    )

    q = _query_mock(count=2, all_=[user1, user2])
    db.query.return_value = q

    repo = AdminRepository(db)

    users, total = repo.get_all_users(
        page=1,
        per_page=10,
        role="admin",
        status="inactive",
        search="bob",
    )

    assert total == 2
    assert users[0]["role"] == UserRole.ADMIN.value
    assert users[1]["role"] == "chef"
    assert users[0]["last_login"] is None


def test_get_all_users_role_chef_branch():
    db = MagicMock()

    user = SimpleNamespace(
        id=1,
        username="c",
        email="c@c.com",
        role=UserRole.CHEF,
        is_active=True,
        created_at=datetime(2025, 1, 1),
        last_login=None,
    )

    q = _query_mock(count=1, all_=[user])
    db.query.return_value = q

    repo = AdminRepository(db)
    users, total = repo.get_all_users(role="chef")

    assert total == 1
    assert users[0]["role"] == UserRole.CHEF.value


def test_get_all_users_status_active_branch():
    db = MagicMock()

    user = SimpleNamespace(
        id=1,
        username="x",
        email="x@x.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime(2025, 1, 1),
        last_login=None,
    )

    q = _query_mock(count=1, all_=[user])
    db.query.return_value = q

    repo = AdminRepository(db)
    users, total = repo.get_all_users(status="active")

    assert total == 1
    assert users[0]["id"] == 1


def test_delete_user_self_delete_and_last_admin_and_chef_profile_deactivate():
    db = MagicMock()
    repo = AdminRepository(db)

    ok, msg = repo.delete_user(user_id=1, admin_id=1)
    assert ok is False
    assert "propia" in msg

    # last active admin cannot be deleted
    admin_user = SimpleNamespace(id=2, role=UserRole.ADMIN, is_active=True)

    def _get(model, id_):
        return admin_user if id_ == 2 else None

    db.get.side_effect = _get
    db.query.return_value = _query_mock(count=1)

    ok, msg = repo.delete_user(user_id=2, admin_id=1)
    assert ok is False
    assert "único" in msg

    # deleting a chef should also deactivate chef profile
    chef_user = SimpleNamespace(id=3, role=UserRole.CHEF, is_active=True)

    def _get2(model, id_):
        return chef_user if id_ == 3 else None

    db.get.side_effect = _get2

    chef_profile = SimpleNamespace(is_active=True)

    # db.query(User) for active_admins_count not used here (role CHEF)
    # db.query(Chef).filter_by(...).first() is used
    q_chef = _query_mock(first=chef_profile)

    def _query_dispatch(*args, **kwargs):
        # for this test, only Chef query is used
        return q_chef

    db.query.side_effect = _query_dispatch

    ok, msg = repo.delete_user(user_id=3, admin_id=1)
    assert ok is True
    assert msg is None
    assert chef_user.is_active is False
    assert chef_profile.is_active is False
    db.commit.assert_called()


def test_delete_user_chef_without_profile_still_deactivates_user():
    db = MagicMock()
    repo = AdminRepository(db)

    chef_user = SimpleNamespace(id=3, role=UserRole.CHEF, is_active=True)

    def _get(model, id_):
        return chef_user if id_ == 3 else None

    db.get.side_effect = _get

    # Chef profile lookup returns None
    db.query.return_value = _query_mock(first=None)

    ok, msg = repo.delete_user(user_id=3, admin_id=1)
    assert ok is True
    assert msg is None
    assert chef_user.is_active is False
    db.commit.assert_called()


def test_delete_user_user_not_found_returns_message():
    db = MagicMock()
    repo = AdminRepository(db)

    db.get.return_value = None

    ok, msg = repo.delete_user(user_id=999, admin_id=1)
    assert ok is False
    assert msg == "Usuario no encontrado"


def test_generate_activity_report_default_dates_and_explicit_end_date_parsing():
    db = MagicMock()

    # 6 new records counts + 2 status breakdown queries
    db.query.side_effect = [
        _query_mock(count=1),
        _query_mock(count=2),
        _query_mock(count=3),
        _query_mock(count=4),
        _query_mock(count=5),
        _query_mock(count=6),
        _query_mock(all_=[("draft", 1)]),
        _query_mock(all_=[("scheduled", 2)]),
    ]

    repo = AdminRepository(db)

    out = repo.generate_activity_report()
    assert out["new_records"]["chefs"] == 1
    assert out["quotations_by_status"]["draft"] == 1

    # Explicit parsing branch (end_date provided)
    db2 = MagicMock()
    db2.query.side_effect = [
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(all_=[]),
        _query_mock(all_=[]),
    ]

    repo2 = AdminRepository(db2)
    out2 = repo2.generate_activity_report(start_date="2025-01-01", end_date="2025-01-10")
    assert out2["period"]["start"].startswith("2025-01-01")
    assert out2["period"]["end"].startswith("2025-01-10")


def test_generate_chefs_report_activity_rate_branches():
    db = MagicMock()

    db.query.side_effect = [
        _query_mock(count=0),
        _query_mock(count=0),
        _query_mock(all_=[]),
        _query_mock(all_=[]),
        _query_mock(all_=[]),
    ]

    repo = AdminRepository(db)
    out = repo.generate_chefs_report()
    assert out["summary"]["activity_rate"] == 0


def test_generate_quotations_report_acceptance_rate_and_top_chefs():
    db = MagicMock()

    q_base = _query_mock(count=10)
    q_base.filter.return_value = q_base

    db.query.side_effect = [
        q_base,
        _query_mock(all_=[("accepted", 4), ("draft", 6)]),
        _query_mock(all_=[(1, "chef", 2)]),
    ]

    repo = AdminRepository(db)
    out = repo.generate_quotations_report(start_date="2025-01-01", end_date="2025-01-10")

    assert out["summary"]["total"] == 10
    assert out["summary"]["acceptance_rate"] == 40.0
    assert out["top_chefs_by_accepted"][0]["chef_id"] == 1


def test_generate_quotations_report_default_dates_and_zero_total_branch():
    db = MagicMock()

    q_base = _query_mock(count=0)
    q_base.filter.return_value = q_base

    db.query.side_effect = [
        q_base,
        _query_mock(all_=[]),
        _query_mock(all_=[]),
    ]

    repo = AdminRepository(db)
    out = repo.generate_quotations_report()

    assert out["summary"]["total"] == 0
    assert out["summary"]["acceptance_rate"] == 0
