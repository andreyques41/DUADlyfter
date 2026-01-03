"""Coverage-focused unit tests for admin controller.

We mock AdminService + AuditService to exercise controller branches without
needing database fixtures.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask, g


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


def _controller():
    from app.admin.controllers.admin_controller import AdminController

    return AdminController()


class TestAdminControllerCoverage:
    def test_dashboard_success(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.get_dashboard.return_value = {"users": 1}
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/dashboard"):
            g.user_id = 10
            resp, status = controller.dashboard()

        assert status == 200
        assert resp.get_json()["status"] == "success"
        assert resp.get_json()["data"] == {"users": 1}
        service.get_dashboard.assert_called_once_with(10)

    def test_dashboard_exception_returns_500(self, app, monkeypatch):
        controller = _controller()

        def boom():
            raise Exception("boom")

        monkeypatch.setattr(controller, "_get_service", boom)

        with app.test_request_context("/admin/dashboard"):
            g.user_id = 10
            resp, status = controller.dashboard()

        assert status == 500
        assert resp.get_json()["status"] == "error"
        assert "boom" in resp.get_json()["message"]

    def test_list_chefs_success_parses_query_params(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.get_all_chefs.return_value = {
            "chefs": [{"id": 1}],
            "page": 2,
            "per_page": 5,
            "total": 6,
            "pages": 2,
        }
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context(
            "/admin/chefs?page=2&per_page=5&status=active&search=ana&sort=email&order=asc"
        ):
            g.user_id = 99
            resp, status = controller.list_chefs()

        assert status == 200
        body = resp.get_json()
        assert body["status"] == "success"
        assert body["data"] == [{"id": 1}]
        assert body["pagination"]["page"] == 2
        assert body["pagination"]["per_page"] == 5
        assert body["pagination"]["total"] == 6
        assert body["pagination"]["pages"] == 2
        service.get_all_chefs.assert_called_once_with(
            admin_id=99,
            page=2,
            per_page=5,
            status="active",
            search="ana",
            sort="email",
            order="asc",
        )

    def test_get_chef_not_found_returns_404(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.get_chef_details.return_value = None
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/chefs/123"):
            g.user_id = 1
            resp, status = controller.get_chef(123)

        assert status == 404
        assert resp.get_json()["message"] == "Chef no encontrado"

    def test_get_chef_success(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.get_chef_details.return_value = {"id": 123}
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/chefs/123"):
            g.user_id = 1
            resp, status = controller.get_chef(123)

        assert status == 200
        assert resp.get_json()["data"] == {"id": 123}

    def test_update_chef_status_requires_is_active(self, app, monkeypatch):
        controller = _controller()
        monkeypatch.setattr(controller, "_get_service", lambda: MagicMock())

        with app.test_request_context("/admin/chefs/1/status", method="PATCH", json={}):
            g.user_id = 1
            resp, status = controller.update_chef_status(1)

        assert status == 400
        assert "is_active" in resp.get_json()["message"]

    def test_update_chef_status_not_found_returns_404(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.update_chef_status.return_value = False
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context(
            "/admin/chefs/1/status", method="PATCH", json={"is_active": True}
        ):
            g.user_id = 1
            resp, status = controller.update_chef_status(1)

        assert status == 404
        assert resp.get_json()["message"] == "Chef no encontrado"

    def test_update_chef_status_success_message_active_inactive(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.update_chef_status.return_value = True
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context(
            "/admin/chefs/1/status", method="PATCH", json={"is_active": True}
        ):
            g.user_id = 1
            resp, status = controller.update_chef_status(1)
        assert status == 200
        assert "activado" in resp.get_json()["message"]

        with app.test_request_context(
            "/admin/chefs/1/status", method="PATCH", json={"is_active": False}
        ):
            g.user_id = 1
            resp, status = controller.update_chef_status(1)
        assert status == 200
        assert "desactivado" in resp.get_json()["message"]

    def test_list_users_success(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.get_all_users.return_value = {
            "users": [],
            "page": 1,
            "per_page": 20,
            "total": 0,
            "pages": 0,
        }
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/users?role=chef&status=active&search=x"):
            g.user_id = 1
            resp, status = controller.list_users()

        assert status == 200
        body = resp.get_json()
        assert body["status"] == "success"
        assert "pagination" in body

    def test_delete_user_validations(self, app, monkeypatch):
        controller = _controller()
        monkeypatch.setattr(controller, "_get_service", lambda: MagicMock())

        # missing confirm
        with app.test_request_context("/admin/users/1", method="DELETE", json={}):
            g.user_id = 1
            resp, status = controller.delete_user(1)
        assert status == 400

        # missing reason
        with app.test_request_context(
            "/admin/users/1", method="DELETE", json={"confirm": True, "reason": ""}
        ):
            g.user_id = 1
            resp, status = controller.delete_user(1)
        assert status == 400

        # short reason
        with app.test_request_context(
            "/admin/users/1", method="DELETE", json={"confirm": True, "reason": "short"}
        ):
            g.user_id = 1
            resp, status = controller.delete_user(1)
        assert status == 400

    def test_delete_user_denied_403_and_success_200(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.delete_user.return_value = (False, "Not allowed")
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context(
            "/admin/users/1",
            method="DELETE",
            json={"confirm": True, "reason": "long enough reason"},
        ):
            g.user_id = 1
            resp, status = controller.delete_user(1)
        assert status == 403
        assert resp.get_json()["message"] == "Not allowed"

        service.delete_user.return_value = (True, None)
        with app.test_request_context(
            "/admin/users/1",
            method="DELETE",
            json={"confirm": True, "reason": "long enough reason"},
        ):
            g.user_id = 1
            resp, status = controller.delete_user(1)
        assert status == 200
        assert resp.get_json()["status"] == "success"

    def test_generate_report_invalid_type_400(self, app, monkeypatch):
        controller = _controller()
        monkeypatch.setattr(controller, "_get_service", lambda: MagicMock())

        with app.test_request_context("/admin/reports?report_type=bad"):
            g.user_id = 1
            resp, status = controller.generate_report()

        assert status == 400

    def test_generate_report_no_data_returns_500(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.generate_report.return_value = None
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/reports?report_type=activity"):
            g.user_id = 1
            resp, status = controller.generate_report()

        assert status == 500
        assert resp.get_json()["message"] == "Error generando reporte"

    def test_generate_report_csv_branch(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.generate_report.return_value = {"rows": 1}
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/reports?report_type=activity&format=csv"):
            g.user_id = 1
            resp, status = controller.generate_report()

        assert status == 200
        assert "CSV" in resp.get_json()["message"]

    def test_generate_report_json_branch(self, app, monkeypatch):
        controller = _controller()
        service = MagicMock()
        service.generate_report.return_value = {"rows": 1}
        monkeypatch.setattr(controller, "_get_service", lambda: service)

        with app.test_request_context("/admin/reports?report_type=activity"):
            g.user_id = 1
            resp, status = controller.generate_report()

        assert status == 200
        assert resp.get_json()["report_type"] == "activity"

    def test_get_audit_logs_success(self, app, monkeypatch):
        controller = _controller()

        audit_service = MagicMock()
        audit_service.get_logs.return_value = {
            "logs": [],
            "page": 1,
            "per_page": 50,
            "total": 0,
            "pages": 0,
        }

        admin_service = MagicMock()
        admin_service.audit_service = audit_service

        monkeypatch.setattr(controller, "_get_service", lambda: admin_service)

        with app.test_request_context("/admin/audit-logs?page=1&per_page=50"):
            g.user_id = 1
            resp, status = controller.get_audit_logs()

        assert status == 200
        audit_service.get_logs.assert_called_once()
        # should log the view action
        assert audit_service.log_action.called

    def test_get_audit_statistics_success(self, app, monkeypatch):
        controller = _controller()

        audit_service = MagicMock()
        audit_service.get_audit_statistics.return_value = {"count": 1}

        admin_service = MagicMock()
        admin_service.audit_service = audit_service

        monkeypatch.setattr(controller, "_get_service", lambda: admin_service)

        with app.test_request_context("/admin/audit-logs/statistics"):
            g.user_id = 1
            resp, status = controller.get_audit_statistics()

        assert status == 200
        assert resp.get_json()["data"] == {"count": 1}
        assert audit_service.log_action.called
