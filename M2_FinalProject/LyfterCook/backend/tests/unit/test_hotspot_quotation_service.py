"""Targeted unit tests for QuotationService.

Testing scope only: exercises business logic paths that are currently low coverage.
Does not require quotation creation via HTTP (controller serialization issues are avoided).
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from app.quotations.services.quotation_service import QuotationService
from app.quotations.repositories.quotation_repository import QuotationRepository
from app.chefs.repositories.chef_repository import ChefRepository
from app.clients.repositories.client_repository import ClientRepository
from app.menus.repositories.menu_repository import MenuRepository
from app.dishes.repositories.dish_repository import DishRepository
from app.core.lib.time_utils import utcnow_naive


@pytest.fixture()
def quotation_service(db_session):
    return QuotationService(
        QuotationRepository(db_session),
        ChefRepository(db_session),
        ClientRepository(db_session),
        MenuRepository(db_session),
        DishRepository(db_session),
    )


def test_create_quotation_autofills_item_name_and_price(
    quotation_service,
    db_session,
    test_chef_user,
    test_chef,
    test_client_profile,
    test_dish,
    test_menu,
):
    # Ensure the menu belongs to this chef and is usable.
    assert test_menu.chef_id == test_chef.id

    quotation = quotation_service.create_quotation(
        test_chef_user.id,
        {
            "client_id": test_client_profile.id,
            "menu_id": test_menu.id,
            "event_date": (utcnow_naive() + timedelta(days=30)).date(),
            "number_of_people": 10,
            "notes": "unit test",
            "items": [
                {
                    "dish_id": test_dish.id,
                    "description": "auto-fill",
                    "quantity": 2,
                    # omit item_name and unit_price to trigger auto-fill
                }
            ],
        },
    )

    assert quotation.id is not None
    assert quotation.chef_id == test_chef.id
    assert quotation.status == "draft"

    # Items should exist and be auto-filled.
    assert quotation.items
    assert quotation.items[0].item_name == test_dish.name
    assert float(quotation.items[0].unit_price) == float(test_dish.price)


def test_update_quotation_status_transitions(quotation_service, test_chef_user, test_quotation):
    # Draft -> sent
    updated = quotation_service.update_quotation_status(test_quotation.id, test_chef_user.id, "sent")
    assert updated.status == "sent"
    assert updated.sent_at is not None

    # sent -> accepted
    updated = quotation_service.update_quotation_status(test_quotation.id, test_chef_user.id, "accepted")
    assert updated.status == "accepted"
    assert updated.responded_at is not None

    # accepted -> rejected is invalid
    with pytest.raises(ValueError):
        quotation_service.update_quotation_status(test_quotation.id, test_chef_user.id, "rejected")


def test_update_quotation_denied_when_not_draft(quotation_service, test_chef_user, test_quotation):
    quotation_service.update_quotation_status(test_quotation.id, test_chef_user.id, "sent")

    with pytest.raises(ValueError):
        quotation_service.update_quotation(test_quotation.id, test_chef_user.id, {"notes": "nope"})
