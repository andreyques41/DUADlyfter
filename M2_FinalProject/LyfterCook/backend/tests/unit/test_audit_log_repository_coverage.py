"""Coverage-focused tests for AuditLogRepository.

Goal: cover success + SQLAlchemyError fallback paths without requiring a real DB.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from app.admin.repositories.audit_log_repository import AuditLogRepository


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def test_create_sets_ip_and_commits(flask_app):
    db = MagicMock()
    repo = AuditLogRepository(db)

    with flask_app.test_request_context(
        "/admin/dashboard", environ_base={"REMOTE_ADDR": "1.2.3.4"}
    ):
        audit_log = repo.create(
            admin_id=1,
            action="test_action",
            target_type="system",
            target_id=None,
            reason=None,
            metadata={"k": "v"},
        )

    assert audit_log is not None
    assert audit_log.ip_address == "1.2.3.4"
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_create_sqlalchemy_error_rolls_back_and_returns_none(flask_app):
    db = MagicMock()
    db.commit.side_effect = SQLAlchemyError("db down")

    repo = AuditLogRepository(db)

    with flask_app.test_request_context(
        "/admin/dashboard", environ_base={"REMOTE_ADDR": "1.2.3.4"}
    ):
        audit_log = repo.create(admin_id=1, action="test_action")

    assert audit_log is None
    db.rollback.assert_called_once()


def test_find_all_applies_filters_orders_paginates_and_returns_total():
    db = MagicMock()

    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.count.return_value = 12
    query.all.return_value = [MagicMock(), MagicMock()]

    db.query.return_value = query

    repo = AuditLogRepository(db)
    logs, total = repo.find_all(
        page=2,
        per_page=2,
        admin_id=7,
        action_type="delete_user",
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    assert total == 12
    assert len(logs) == 2
    assert query.offset.call_args[0][0] == 2


def test_find_all_sqlalchemy_error_returns_empty_and_zero(monkeypatch):
    db = MagicMock()
    db.query.side_effect = SQLAlchemyError("boom")

    repo = AuditLogRepository(db)
    logs, total = repo.find_all(page=1, per_page=10)

    assert logs == []
    assert total == 0


def test_get_statistics_success_builds_payload():
    db = MagicMock()

    q_total = MagicMock()
    q_total.count.return_value = 5

    q_by_action = MagicMock()
    q_by_action.group_by.return_value = q_by_action
    q_by_action.order_by.return_value = q_by_action
    q_by_action.all.return_value = [("delete_user", 2), ("deactivate_chef", 3)]

    q_recent = MagicMock()
    q_recent.filter.return_value = q_recent
    q_recent.count.return_value = 4

    q_top_admins = MagicMock()
    q_top_admins.group_by.return_value = q_top_admins
    q_top_admins.order_by.return_value = q_top_admins
    q_top_admins.limit.return_value = q_top_admins
    q_top_admins.all.return_value = [(1, 3), (2, 1)]

    db.query.side_effect = [q_total, q_by_action, q_recent, q_top_admins]

    repo = AuditLogRepository(db)
    stats = repo.get_statistics()

    assert stats["total_logs"] == 5
    assert stats["recent_logs_7_days"] == 4
    assert stats["logs_by_action"]["delete_user"] == 2
    assert stats["top_admins"][0]["admin_id"] == 1


def test_get_statistics_sqlalchemy_error_returns_zeros():
    db = MagicMock()
    db.query.side_effect = SQLAlchemyError("boom")

    repo = AuditLogRepository(db)
    stats = repo.get_statistics()

    assert stats["total_logs"] == 0
    assert stats["recent_logs_7_days"] == 0
    assert stats["logs_by_action"] == {}
    assert stats["top_admins"] == []
