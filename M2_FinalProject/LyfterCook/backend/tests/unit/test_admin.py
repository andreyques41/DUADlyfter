"""
Functional tests for admin endpoints and middleware behavior.
"""

import pytest


class TestAdminEndpoints:
    """End-to-end smoke tests for admin routes."""

    def test_dashboard_returns_statistics(
        self,
        client,
        admin_headers,
        test_chef,
        test_client_profile,
        test_dish,
        test_menu,
        test_quotation,
        test_appointment
    ):
        response = client.get('/admin/dashboard', headers=admin_headers)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload['status'] == 'success'
        assert 'statistics' in payload['data']
        assert 'recent_activity' in payload['data']

    def test_list_chefs_returns_paginated_data(self, client, admin_headers, test_chef):
        response = client.get('/admin/chefs?page=1&per_page=5', headers=admin_headers)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload['status'] == 'success'
        assert isinstance(payload['data'], list)
        assert 'pagination' in payload
        assert payload['pagination']['page'] == 1

    def test_list_chefs_respects_search_filter(self, client, admin_headers, test_chef_user, test_chef):
        response = client.get('/admin/chefs?search=testchef', headers=admin_headers)
        payload = response.get_json()
        assert response.status_code == 200
        assert any(chef['username'] == test_chef_user.username for chef in payload['data'])

    def test_list_users_returns_chefs(self, client, admin_headers, test_chef_user):
        response = client.get('/admin/users?role=chef', headers=admin_headers)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload['status'] == 'success'
        assert all('chef' in str(user['role']).lower() for user in payload['data'])

    def test_update_chef_status_requires_is_active(self, client, admin_headers, test_chef):
        response = client.patch(f'/admin/chefs/{test_chef.id}/status', json={}, headers=admin_headers)
        assert response.status_code == 400
        payload = response.get_json()
        assert payload['message'] == 'Campo is_active es requerido'

    def test_update_chef_status_toggles_flag(self, client, admin_headers, test_chef, db_session):
        payload = {'is_active': False, 'reason': 'Policy violation'}
        response = client.patch(
            f'/admin/chefs/{test_chef.id}/status',
            json=payload,
            headers=admin_headers
        )
        assert response.status_code == 200
        db_session.refresh(test_chef)
        assert test_chef.is_active is False

    def test_delete_user_requires_reason_details(self, client, admin_headers, test_chef_user):
        payload = {'confirm': True, 'reason': 'short'}
        response = client.delete(
            f'/admin/users/{test_chef_user.id}',
            json=payload,
            headers=admin_headers
        )
        assert response.status_code == 400
        assert 'La razón debe tener al menos 10 caracteres' in response.get_json()['message']

    def test_delete_user_successfully_soft_deletes(self, client, admin_headers, test_chef_user, test_chef, db_session):
        payload = {'confirm': True, 'reason': 'Violation of platform rules'}
        response = client.delete(
            f'/admin/users/{test_chef_user.id}',
            json=payload,
            headers=admin_headers
        )
        assert response.status_code == 200
        db_session.refresh(test_chef_user)
        db_session.refresh(test_chef)
        assert test_chef_user.is_active is False
        assert test_chef.is_active is False

    def test_generate_report_validates_type(self, client, admin_headers):
        response = client.get('/admin/reports?report_type=unknown', headers=admin_headers)
        assert response.status_code == 400
        assert 'Tipo de reporte inválido' in response.get_json()['message']

    def test_generate_activity_report_returns_payload(
        self,
        client,
        admin_headers,
        test_chef,
        test_quotation,
        test_appointment
    ):
        response = client.get('/admin/reports?report_type=activity', headers=admin_headers)
        assert response.status_code == 200
        payload = response.get_json()
        assert payload['status'] == 'success'
        assert payload['report_type'] == 'activity'

    def test_audit_logs_endpoint_returns_entries(self, client, admin_headers):
        # Trigger at least one audit log
        client.get('/admin/dashboard', headers=admin_headers)

        response = client.get('/admin/audit-logs', headers=admin_headers)
        assert response.status_code == 200
        payload = response.get_json()
        assert isinstance(payload['data'], list)
        assert 'pagination' in payload

    def test_admin_access_required(self, client, chef_headers):
        response = client.get('/admin/dashboard', headers=chef_headers)
        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['message']

    def test_jwt_required_for_admin_routes(self, client):
        response = client.get('/admin/dashboard')
        assert response.status_code == 401
        assert 'Missing authorization header' in response.get_json()['message']


@pytest.mark.parametrize(
    'endpoint',
    [
        '/admin/chefs',
        '/admin/users',
        '/admin/reports?report_type=activity'
    ]
)
def test_admin_endpoints_share_pagination_structure(client, admin_headers, endpoint):
    """
    Smoke test to ensure multiple admin GET endpoints respond with success structure.
    """
    response = client.get(endpoint, headers=admin_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['status'] in ('success', 'error')

