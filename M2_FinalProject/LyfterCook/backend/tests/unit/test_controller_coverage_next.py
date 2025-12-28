"""Additional controller-focused tests to boost coverage.

These tests intentionally target low-covered controller branches (chef/menu/quotation)
without modifying application code.
"""

from __future__ import annotations

import pytest

from tests.unit.test_helpers import (
    assert_success_response,
    assert_error_response,
    assert_not_found_error,
)


class TestChefProfileController:
    def test_get_my_profile_not_found_for_user_without_profile(self, client, auth_headers):
        res = client.get("/chefs/profile", headers=auth_headers)
        assert_not_found_error(res)

    def test_create_profile_success_for_user_without_profile(self, client, auth_headers):
        payload = {
            "bio": "New chef bio",
            "specialty": "BBQ",
            "phone": "+1-555-0303",
            "location": "Austin, TX",
        }
        res = client.post("/chefs/profile", json=payload, headers=auth_headers)
        data = assert_success_response(res, 201)
        assert data.get("data") is not None

        # After creation, profile should be retrievable.
        res2 = client.get("/chefs/profile", headers=auth_headers)
        data2 = assert_success_response(res2, 200)
        assert data2["data"].get("location") == "Austin, TX"

    def test_create_profile_duplicate_returns_400(self, client, chef_headers):
        res = client.post("/chefs/profile", json={"bio": "dup"}, headers=chef_headers)
        assert_error_response(res, 400)

    def test_update_profile_success(self, client, chef_headers):
        res = client.put(
            "/chefs/profile",
            json={"location": "Seattle, WA", "is_active": True},
            headers=chef_headers,
        )
        data = assert_success_response(res, 200)
        assert data["data"].get("location") == "Seattle, WA"

    def test_update_profile_not_found_for_user_without_profile(self, client, auth_headers):
        res = client.put("/chefs/profile", json={"location": "Nowhere"}, headers=auth_headers)
        assert_not_found_error(res)


class TestMenuControllerBranches:
    def test_create_menu_requires_chef_profile(self, client, auth_headers, sample_menu_data):
        # User is authenticated but lacks a chef profile, so controller should map to 400.
        res = client.post("/menus", json=sample_menu_data, headers=auth_headers)
        assert_error_response(res, 400)

    def test_update_menu_access_denied_returns_404(self, client, other_chef, other_chef_headers, test_menu):
        res = client.put(f"/menus/{test_menu.id}", json={"name": "Hacked"}, headers=other_chef_headers)
        assert_not_found_error(res)

    def test_assign_dishes_rejects_other_chefs_dish(self, client, chef_headers, test_menu, other_dish):
        res = client.put(
            f"/menus/{test_menu.id}/dishes",
            json={"dishes": [{"dish_id": other_dish.id, "order_position": 0}]},
            headers=chef_headers,
        )
        assert_error_response(res, 400)

    def test_delete_menu_access_denied_returns_404(self, client, other_chef, other_chef_headers, test_menu):
        res = client.delete(f"/menus/{test_menu.id}", headers=other_chef_headers)
        assert_not_found_error(res)


class TestQuotationControllerBranches:
    def test_list_quotations_requires_chef_profile(self, client, auth_headers):
        # User is authenticated but lacks a chef profile.
        res = client.get("/quotations", headers=auth_headers)
        assert_error_response(res, 400)

    def test_update_status_invalid_transition_returns_400(self, client, chef_headers, test_quotation):
        # draft -> accepted is invalid (must be sent first)
        res = client.patch(
            f"/quotations/{test_quotation.id}/status",
            json={"status": "accepted"},
            headers=chef_headers,
        )
        assert_error_response(res, 400)

    def test_update_denied_when_not_draft_returns_400(self, client, db_session, chef_headers, test_quotation):
        test_quotation.status = "sent"
        db_session.commit()

        res = client.put(
            f"/quotations/{test_quotation.id}",
            json={"notes": "attempt update"},
            headers=chef_headers,
        )
        assert_error_response(res, 400)

    def test_delete_denied_when_not_draft_returns_400(self, client, db_session, chef_headers, test_quotation):
        test_quotation.status = "sent"
        db_session.commit()

        res = client.delete(f"/quotations/{test_quotation.id}", headers=chef_headers)
        assert_error_response(res, 400)
