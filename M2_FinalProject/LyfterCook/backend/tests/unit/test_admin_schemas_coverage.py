"""Unit tests to exercise admin Marshmallow schemas.

These tests are intentionally lightweight (no Flask app context) and focus on:
- importing schemas (coverage for module/class definitions)
- required-field and validation branches via Schema.load()
- representative nested serialization via Schema.dump()
"""

from datetime import datetime, timezone

import pytest
from marshmallow import ValidationError


def test_admin_schemas_exports_and_instantiation():
    import app.admin.schemas as admin_schemas

    # Ensure __all__ stays in sync with exports.
    assert isinstance(admin_schemas.__all__, list)
    for name in admin_schemas.__all__:
        schema_cls = getattr(admin_schemas, name)
        instance = schema_cls()
        assert instance is not None


def test_chef_status_update_schema_requires_is_active_and_allows_none_reason():
    from app.admin.schemas.admin_schemas import ChefStatusUpdateSchema

    schema = ChefStatusUpdateSchema()

    with pytest.raises(ValidationError):
        schema.load({})

    payload = schema.load({"is_active": True, "reason": None})
    assert payload["is_active"] is True
    assert payload["reason"] is None


def test_user_delete_schema_validates_reason_min_length():
    from app.admin.schemas.admin_schemas import UserDeleteSchema

    schema = UserDeleteSchema()

    with pytest.raises(ValidationError) as excinfo:
        schema.load({"confirm": True, "reason": "short"})

    # Marshmallow stores field errors under the field name.
    assert "reason" in excinfo.value.messages

    payload = schema.load({"confirm": True, "reason": "long enough reason"})
    assert payload["confirm"] is True


def test_admin_response_schemas_dump_nested_payloads():
    from app.admin.schemas.admin_schemas import (
        ChefDetailsResponseSchema,
        ChefListResponseSchema,
        DashboardResponseSchema,
        UserListResponseSchema,
    )

    now = datetime(2025, 12, 28, 12, 0, 0, tzinfo=timezone.utc)

    chef_list_payload = {
        "status": "success",
        "data": [
            {
                "id": 1,
                "username": "chef1",
                "email": "chef1@example.com",
                "specialty": "pasta",
                "bio": "bio",
                "is_active": True,
                "created_at": now,
                "stats": {"clients": 1, "dishes": 2, "menus": 3},
            }
        ],
        "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1},
    }

    dumped_list = ChefListResponseSchema().dump(chef_list_payload)
    assert dumped_list["status"] == "success"
    assert isinstance(dumped_list["data"], list)
    assert dumped_list["data"][0]["created_at"]

    chef_details_payload = {
        "status": "success",
        "data": {
            "id": 1,
            "user_id": 10,
            "username": "chef1",
            "email": "chef1@example.com",
            "specialty": "pasta",
            "bio": "bio",
            "phone": "123",
            "is_active": True,
            "created_at": now,
            "statistics": {
                "clients": 1,
                "dishes_total": 2,
                "dishes_active": 2,
                "menus_total": 1,
                "menus_active": 1,
                "quotations_by_status": {"draft": 1},
                "appointments_by_status": {"scheduled": 1},
            },
            "recent_activity": {
                "last_login": None,
                "last_dish_created": now,
                "last_quotation_sent": None,
            },
        },
    }

    dumped_details = ChefDetailsResponseSchema().dump(chef_details_payload)
    assert dumped_details["data"]["recent_activity"]["last_login"] is None

    dashboard_payload = {
        "status": "success",
        "data": {"statistics": {"chefs_total": 1}, "recent_activity": {"new_chefs": 0}},
    }
    dumped_dashboard = DashboardResponseSchema().dump(dashboard_payload)
    assert dumped_dashboard["status"] == "success"

    user_list_payload = {
        "status": "success",
        "data": [
            {
                "id": 1,
                "username": "u1",
                "email": "u1@example.com",
                "role": "chef",
                "is_active": True,
                "created_at": now,
                "last_login": None,
            }
        ],
        "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1},
    }

    dumped_users = UserListResponseSchema().dump(user_list_payload)
    assert dumped_users["data"][0]["last_login"] is None
