"""Coverage-focused tests for AdminService and AuditService.

Uses mocks to cover action logging and branching behavior without DB.
"""

from __future__ import annotations

from unittest.mock import MagicMock


def test_audit_service_get_audit_statistics_calls_repo():
    from app.admin.services.audit_service import AuditService

    repo = MagicMock()
    repo.get_statistics.return_value = {"count": 1}

    svc = AuditService(repo)
    assert svc.get_audit_statistics() == {"count": 1}
    repo.get_statistics.assert_called_once_with()


class TestAdminServiceCoverage:
    def _service(self):
        from app.admin.services.admin_service import AdminService

        admin_repo = MagicMock()
        audit_repo = MagicMock()
        return AdminService(admin_repo, audit_repo), admin_repo, audit_repo

    def test_get_dashboard_logs_action(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.get_dashboard_statistics.return_value = {"ok": True}

        out = svc.get_dashboard(admin_id=7)
        assert out == {"ok": True}
        audit_repo.create.assert_called_once()
        assert audit_repo.create.call_args.kwargs["admin_id"] == 7
        assert audit_repo.create.call_args.kwargs["action"] == "view_dashboard"

    def test_get_all_chefs_logs_action_and_pages(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.get_all_chefs.return_value = ([{"id": 1}], 21)

        out = svc.get_all_chefs(admin_id=1, page=2, per_page=10, status="all", search=None)
        assert out["pages"] == 3
        assert out["total"] == 21
        assert out["chefs"] == [{"id": 1}]
        assert audit_repo.create.call_args.kwargs["action"] == "list_chefs"

    def test_get_chef_details_none_does_not_log(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.get_chef_details.return_value = None

        assert svc.get_chef_details(admin_id=1, chef_id=123) is None
        audit_repo.create.assert_not_called()

    def test_get_chef_details_success_logs(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.get_chef_details.return_value = {"id": 123}

        assert svc.get_chef_details(admin_id=1, chef_id=123) == {"id": 123}
        assert audit_repo.create.call_args.kwargs["action"] == "view_chef_details"

    def test_update_chef_status_false_no_log(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.update_chef_status.return_value = False

        assert svc.update_chef_status(admin_id=1, chef_id=1, is_active=True) is False
        audit_repo.create.assert_not_called()

    def test_update_chef_status_true_logs_activate_deactivate(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.update_chef_status.return_value = True

        assert svc.update_chef_status(admin_id=1, chef_id=1, is_active=True, reason="r") is True
        assert audit_repo.create.call_args.kwargs["action"] == "activate_chef"

        audit_repo.create.reset_mock()
        assert svc.update_chef_status(admin_id=1, chef_id=1, is_active=False, reason="r") is True
        assert audit_repo.create.call_args.kwargs["action"] == "deactivate_chef"

    def test_get_all_users_logs_action(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.get_all_users.return_value = ([{"id": 1}], 1)

        out = svc.get_all_users(admin_id=1, page=1, per_page=20, role="all", status="all", search=None)
        assert out["users"] == [{"id": 1}]
        assert audit_repo.create.call_args.kwargs["action"] == "list_users"

    def test_delete_user_logs_on_success_only(self):
        svc, admin_repo, audit_repo = self._service()
        admin_repo.delete_user.return_value = (False, "no")

        ok, msg = svc.delete_user(admin_id=1, user_id=2, reason="reason")
        assert ok is False
        assert msg == "no"
        audit_repo.create.assert_not_called()

        admin_repo.delete_user.return_value = (True, None)
        ok, msg = svc.delete_user(admin_id=1, user_id=2, reason="reason")
        assert ok is True
        assert msg is None
        assert audit_repo.create.call_args.kwargs["action"] == "delete_user"

    def test_generate_report_branches_and_invalid(self):
        svc, admin_repo, audit_repo = self._service()

        admin_repo.generate_activity_report.return_value = {"a": 1}
        assert svc.generate_report(admin_id=1, report_type="activity") == {"a": 1}

        audit_repo.create.reset_mock()
        admin_repo.generate_chefs_report.return_value = {"c": 1}
        assert svc.generate_report(admin_id=1, report_type="chefs") == {"c": 1}

        audit_repo.create.reset_mock()
        admin_repo.generate_quotations_report.return_value = {"q": 1}
        assert svc.generate_report(admin_id=1, report_type="quotations") == {"q": 1}

        audit_repo.create.reset_mock()
        assert svc.generate_report(admin_id=1, report_type="nope") is None
        audit_repo.create.assert_not_called()
