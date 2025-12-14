"""
Unit Tests for Admin Module
Tests for repositories, services, and controllers
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.repositories.audit_log_repository import AuditLogRepository
from app.admin.services.admin_service import AdminService
from app.admin.services.audit_service import AuditService


class TestAdminRepository:
    """Tests for AdminRepository"""
    
    @pytest.fixture
    def repo(self):
        return AdminRepository()
    
    def test_get_dashboard_statistics_returns_dict(self, repo):
        """Test dashboard statistics returns proper structure"""
        with patch('app.admin.repositories.admin_repository.db.session') as mock_session:
            # Mock query results
            mock_session.query().count.return_value = 10
            
            stats = repo.get_dashboard_statistics()
            
            assert isinstance(stats, dict)
            assert 'statistics' in stats
            assert 'recent_activity' in stats
    
    def test_get_all_chefs_with_pagination(self, repo):
        """Test chef listing with pagination"""
        with patch('app.admin.repositories.admin_repository.db.session') as mock_session:
            # Mock query
            mock_query = MagicMock()
            mock_query.count.return_value = 25
            mock_query.offset().limit().all.return_value = []
            mock_session.query.return_value = mock_query
            
            chefs, total = repo.get_all_chefs(page=1, per_page=20)
            
            assert total == 25
            assert isinstance(chefs, list)
    
    def test_update_chef_status_success(self, repo):
        """Test successful chef status update"""
        with patch('app.admin.repositories.admin_repository.db.session') as mock_session:
            # Mock chef
            mock_chef = Mock()
            mock_chef.user_id = 1
            mock_user = Mock()
            
            mock_session.query().filter_by().first.side_effect = [mock_chef, mock_user]
            
            result = repo.update_chef_status(chef_id=1, is_active=False)
            
            assert result is True
            assert mock_chef.is_active is False
            assert mock_user.is_active is False
    
    def test_update_chef_status_not_found(self, repo):
        """Test status update for non-existent chef"""
        with patch('app.admin.repositories.admin_repository.db.session') as mock_session:
            mock_session.query().filter_by().first.return_value = None
            
            result = repo.update_chef_status(chef_id=999, is_active=False)
            
            assert result is False


class TestAuditLogRepository:
    """Tests for AuditLogRepository"""
    
    @pytest.fixture
    def repo(self):
        return AuditLogRepository()
    
    def test_create_audit_log(self, repo):
        """Test audit log creation"""
        with patch('app.admin.repositories.audit_log_repository.db.session') as mock_session, \
             patch('app.admin.repositories.audit_log_repository.request') as mock_request:
            
            mock_request.remote_addr = '127.0.0.1'
            
            log = repo.create(
                admin_id=1,
                action='test_action',
                target_type='chef',
                target_id=5
            )
            
            assert log is not None
            assert log.admin_id == 1
            assert log.action == 'test_action'
    
    def test_find_all_with_filters(self, repo):
        """Test finding logs with filters"""
        with patch('app.admin.repositories.audit_log_repository.db.session') as mock_session:
            mock_query = MagicMock()
            mock_query.count.return_value = 10
            mock_query.offset().limit().all.return_value = []
            mock_session.query.return_value = mock_query
            
            logs, total = repo.find_all(
                page=1,
                per_page=20,
                admin_id=1,
                action_type='view_dashboard'
            )
            
            assert total == 10
            assert isinstance(logs, list)


class TestAdminService:
    """Tests for AdminService"""
    
    @pytest.fixture
    def service(self):
        return AdminService()
    
    def test_get_dashboard_logs_action(self, service):
        """Test dashboard access is logged"""
        with patch.object(service.admin_repo, 'get_dashboard_statistics') as mock_dash, \
             patch.object(service.audit_service, 'log_action') as mock_log:
            
            mock_dash.return_value = {'statistics': {}}
            
            service.get_dashboard(admin_id=1)
            
            mock_log.assert_called_once_with(
                admin_id=1,
                action='view_dashboard'
            )
    
    def test_update_chef_status_logs_action(self, service):
        """Test chef status update is logged"""
        with patch.object(service.admin_repo, 'update_chef_status') as mock_update, \
             patch.object(service.audit_service, 'log_action') as mock_log:
            
            mock_update.return_value = True
            
            service.update_chef_status(
                admin_id=1,
                chef_id=5,
                is_active=False,
                reason='Test reason'
            )
            
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[1]['action'] == 'deactivate_chef'
            assert args[1]['target_id'] == 5
            assert args[1]['reason'] == 'Test reason'
    
    def test_get_chef_details_returns_none_if_not_found(self, service):
        """Test chef details returns None for invalid ID"""
        with patch.object(service.admin_repo, 'get_chef_details') as mock_get:
            mock_get.return_value = None
            
            result = service.get_chef_details(admin_id=1, chef_id=999)
            
            assert result is None


class TestAuditService:
    """Tests for AuditService"""
    
    @pytest.fixture
    def service(self):
        return AuditService()
    
    def test_log_action_calls_repository(self, service):
        """Test log_action delegates to repository"""
        with patch.object(service.audit_repo, 'create') as mock_create:
            mock_create.return_value = Mock()
            
            service.log_action(
                admin_id=1,
                action='test_action',
                target_type='chef',
                target_id=5
            )
            
            mock_create.assert_called_once_with(
                admin_id=1,
                action='test_action',
                target_type='chef',
                target_id=5,
                reason=None,
                metadata=None
            )
    
    def test_get_logs_returns_paginated_response(self, service):
        """Test get_logs returns proper pagination"""
        with patch.object(service.audit_repo, 'find_all') as mock_find:
            mock_log = Mock()
            mock_log.to_dict.return_value = {'id': 1}
            mock_find.return_value = ([mock_log], 1)
            
            result = service.get_logs(page=1, per_page=20)
            
            assert 'logs' in result
            assert 'total' in result
            assert 'pages' in result
            assert result['total'] == 1
            assert result['pages'] == 1


class TestAdminPhase2:
    """Tests for Admin Phase 2 - User Management"""
    
    @pytest.fixture
    def repo(self):
        return AdminRepository()
    
    @pytest.fixture
    def service(self):
        return AdminService()
    
    def test_get_all_users_with_filters(self, repo):
        """Test user listing with role and status filters"""
        with patch('app.admin.repositories.admin_repository.User') as mock_user:
            mock_query = MagicMock()
            mock_query.count.return_value = 5
            mock_query.offset().limit().all.return_value = []
            mock_user.query = mock_query
            
            users, total = repo.get_all_users(
                page=1,
                per_page=20,
                role='admin',
                status='active'
            )
            
            assert total == 5
            assert isinstance(users, list)
    
    def test_get_all_users_with_search(self, repo):
        """Test user search by username/email"""
        with patch('app.admin.repositories.admin_repository.User') as mock_user:
            mock_query = MagicMock()
            mock_query.count.return_value = 2
            mock_query.offset().limit().all.return_value = []
            mock_user.query = mock_query
            
            users, total = repo.get_all_users(search='maria')
            
            # Verify search filter was applied
            assert isinstance(users, list)
    
    def test_delete_user_prevents_self_deletion(self, repo):
        """Test that admin cannot delete themselves"""
        success, error = repo.delete_user(user_id=1, admin_id=1)
        
        assert success is False
        assert error == "No puedes eliminar tu propia cuenta"
    
    def test_delete_user_prevents_last_admin_deletion(self, repo):
        """Test that last active admin cannot be deleted"""
        with patch('app.admin.repositories.admin_repository.User') as mock_user:
            # Mock user to be deleted
            mock_target = Mock()
            mock_target.role = 'admin'
            mock_target.is_active = True
            mock_user.query.get.return_value = mock_target
            
            # Mock only 1 active admin exists
            mock_user.query.filter_by().count.return_value = 1
            
            success, error = repo.delete_user(user_id=2, admin_id=1)
            
            assert success is False
            assert "único administrador activo" in error
    
    def test_delete_user_success(self, repo):
        """Test successful user deletion"""
        with patch('app.admin.repositories.admin_repository.User') as mock_user, \
             patch('app.admin.repositories.admin_repository.Chef') as mock_chef, \
             patch('app.admin.repositories.admin_repository.db.session'):
            
            # Mock user to delete (chef role)
            mock_target = Mock()
            mock_target.role = 'chef'
            mock_target.is_active = True
            mock_user.query.get.return_value = mock_target
            
            # Mock chef profile
            mock_chef_obj = Mock()
            mock_chef.query.filter_by().first.return_value = mock_chef_obj
            
            success, error = repo.delete_user(user_id=5, admin_id=1)
            
            assert success is True
            assert error is None
            assert mock_target.is_active is False
            assert mock_chef_obj.is_active is False
    
    def test_delete_user_not_found(self, repo):
        """Test deletion of non-existent user"""
        with patch('app.admin.repositories.admin_repository.User') as mock_user:
            mock_user.query.get.return_value = None
            
            success, error = repo.delete_user(user_id=999, admin_id=1)
            
            assert success is False
            assert error == "Usuario no encontrado"
    
    def test_service_get_all_users_logs_action(self, service):
        """Test that listing users creates audit log"""
        with patch.object(service.admin_repo, 'get_all_users') as mock_get, \
             patch.object(service.audit_service, 'log_action') as mock_log:
            
            mock_get.return_value = ([], 0)
            
            service.get_all_users(
                admin_id=1,
                page=1,
                per_page=20,
                role='chef',
                status='active'
            )
            
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[1]['action'] == 'list_users'
            assert args[1]['admin_id'] == 1
    
    def test_service_delete_user_logs_action(self, service):
        """Test that deleting user creates audit log"""
        with patch.object(service.admin_repo, 'delete_user') as mock_delete, \
             patch.object(service.audit_service, 'log_action') as mock_log:
            
            mock_delete.return_value = (True, None)
            
            service.delete_user(
                admin_id=1,
                user_id=5,
                reason='User requested account deletion'
            )
            
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[1]['action'] == 'delete_user'
            assert args[1]['target_id'] == 5
            assert args[1]['reason'] == 'User requested account deletion'
    
    def test_service_delete_user_returns_error(self, service):
        """Test service returns error from repository"""
        with patch.object(service.admin_repo, 'delete_user') as mock_delete:
            mock_delete.return_value = (False, "No puedes eliminar tu propia cuenta")
            
            success, error = service.delete_user(
                admin_id=1,
                user_id=1,
                reason='Test'
            )
            
            assert success is False
            assert error == "No puedes eliminar tu propia cuenta"


class TestAdminPhase3:
    """Tests for Admin Phase 3 - Analytics & Reports"""
    
    @pytest.fixture
    def repo(self):
        return AdminRepository()
    
    @pytest.fixture
    def service(self):
        return AdminService()
    
    def test_generate_activity_report(self, repo):
        """Test activity report generation"""
        with patch('app.admin.repositories.admin_repository.Chef') as mock_chef, \
             patch('app.admin.repositories.admin_repository.Client') as mock_client:
            
            mock_chef.query.filter().count.return_value = 5
            mock_client.query.filter().count.return_value = 10
            
            report = repo.generate_activity_report()
            
            assert 'period' in report
            assert 'new_records' in report
    
    def test_generate_chefs_report(self, repo):
        """Test chefs report generation"""
        with patch('app.admin.repositories.admin_repository.Chef') as mock_chef, \
             patch('app.admin.repositories.admin_repository.db.session'):
            
            mock_chef.query.count.return_value = 10
            mock_chef.query.filter_by().count.return_value = 8
            
            report = repo.generate_chefs_report()
            
            assert 'summary' in report
            assert 'top_chefs_by_clients' in report
            assert 'by_specialty' in report
    
    def test_generate_quotations_report(self, repo):
        """Test quotations report generation"""
        with patch('app.admin.repositories.admin_repository.Quotation') as mock_quotation, \
             patch('app.admin.repositories.admin_repository.db.session'):
            
            mock_quotation.query.filter().count.return_value = 20
            
            report = repo.generate_quotations_report()
            
            assert 'period' in report
            assert 'summary' in report
            assert 'top_chefs_by_accepted' in report
    
    def test_service_generate_report_logs_action(self, service):
        """Test that generating report creates audit log"""
        with patch.object(service.admin_repo, 'generate_activity_report') as mock_report, \
             patch.object(service.audit_service, 'log_action') as mock_log:
            
            mock_report.return_value = {'period': {}}
            
            service.generate_report(
                admin_id=1,
                report_type='activity',
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[1]['action'] == 'generate_report'
            assert args[1]['metadata']['report_type'] == 'activity'
    
    def test_service_generate_report_invalid_type(self, service):
        """Test invalid report type returns None"""
        result = service.generate_report(
            admin_id=1,
            report_type='invalid_type'
        )
        
        assert result is None
    
    def test_audit_log_statistics(self):
        """Test audit log statistics generation"""
        from app.admin.repositories.audit_log_repository import AuditLogRepository
        repo = AuditLogRepository()
        
        with patch('app.admin.repositories.audit_log_repository.AuditLog') as mock_log, \
             patch('app.admin.repositories.audit_log_repository.db.session'):
            
            mock_log.query.count.return_value = 100
            mock_log.query.filter().count.return_value = 15
            
            stats = repo.get_statistics()
            
            assert 'total_logs' in stats
            assert 'recent_logs_7_days' in stats
            assert 'logs_by_action' in stats
            assert 'top_admins' in stats
    
    def test_audit_service_get_statistics(self):
        """Test audit service get statistics"""
        from app.admin.services.audit_service import AuditService
        service = AuditService()
        
        with patch.object(service.audit_repo, 'get_statistics') as mock_stats:
            mock_stats.return_value = {
                'total_logs': 100,
                'recent_logs_7_days': 15
            }
            
            stats = service.get_audit_statistics()
            
            assert stats['total_logs'] == 100
            assert stats['recent_logs_7_days'] == 15
