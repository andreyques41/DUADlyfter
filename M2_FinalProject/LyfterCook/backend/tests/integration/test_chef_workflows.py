"""
Integration tests covering multi-module chef workflows.
"""

from datetime import datetime, timedelta

import pytest

from tests.unit.test_helpers import assert_success_response


@pytest.mark.integration
class TestChefMenuAndAppointmentFlow:
    """Cross-module workflows for chefs."""

    def test_create_menu_and_schedule_appointment(
        self,
        client,
        chef_headers,
        test_chef
    ):
        """Chef creates dish, menu, client, and schedules appointment."""
        # Create a dish
        dish_payload = {
            'name': 'Integration Test Dish',
            'description': 'Created during integration workflow',
            'category': 'Main Course',
            'price': 24.99,
            'prep_time': 30,
            'servings': 4,
            'ingredients': [
                {'name': 'Protein', 'quantity': 300, 'unit': 'g'},
                {'name': 'Seasoning', 'quantity': 10, 'unit': 'g'}
            ]
        }
        dish_response = client.post('/dishes', json=dish_payload, headers=chef_headers)
        dish_result = assert_success_response(dish_response, 201)
        dish_id = dish_result['data']['id']

        # Create a menu
        menu_payload = {
            'name': 'Integration Menu',
            'description': 'Workflow menu',
            'status': 'draft'
        }
        menu_response = client.post('/menus', json=menu_payload, headers=chef_headers)
        menu_result = assert_success_response(menu_response, 201)
        menu_id = menu_result['data']['id']

        # Assign the dish to the menu
        assign_payload = {
            'dishes': [
                {'dish_id': dish_id, 'order_position': 0}
            ]
        }
        assign_response = client.put(
            f'/menus/{menu_id}/dishes',
            json=assign_payload,
            headers=chef_headers
        )
        assert_success_response(assign_response, 200)

        # Verify menu now exposes dish details
        menu_detail_response = client.get(f'/menus/{menu_id}', headers=chef_headers)
        menu_detail = assert_success_response(menu_detail_response, 200)
        dishes = menu_detail['data'].get('dishes', [])
        assert menu_detail['data']['dish_count'] == 1
        assert dishes
        assert dishes[0]['dish']['id'] == dish_id

        # Create a client profile
        client_payload = {
            'name': 'Integration Client',
            'email': 'integration-client@example.com',
            'phone': '+1-555-0300',
            'company': 'Integration Co',
            'notes': 'Created during integration workflow'
        }
        client_response = client.post('/clients', json=client_payload, headers=chef_headers)
        client_result = assert_success_response(client_response, 201)
        client_id = client_result['data']['id']

        # Schedule an appointment for that client
        future_time = (datetime.utcnow() + timedelta(days=3)).isoformat()
        appointment_payload = {
            'client_id': client_id,
            'title': 'Integration Planning Session',
            'description': 'Discuss menu and logistics',
            'scheduled_at': future_time,
            'duration_minutes': 60,
            'location': 'Virtual'
        }
        appointment_response = client.post(
            '/appointments',
            json=appointment_payload,
            headers=chef_headers
        )
        appointment_result = assert_success_response(appointment_response, 201)
        appointment_id = appointment_result['data']['id']
        assert appointment_result['data']['client_id'] == client_id

        # Ensure appointment listing surfaces the scheduled meeting
        appointments_response = client.get('/appointments', headers=chef_headers)
        appointments_result = assert_success_response(appointments_response, 200)
        assert any(
            appt['id'] == appointment_id for appt in appointments_result['data']
        )
