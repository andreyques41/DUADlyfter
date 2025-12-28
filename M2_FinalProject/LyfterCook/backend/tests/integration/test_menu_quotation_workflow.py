"""Integration-style workflow: Menu -> Quotation (service-level).

Note: quotation creation via HTTP is currently avoided due to serialization behavior.
This test still exercises the real DB + repositories + QuotationService business logic.
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


@pytest.mark.integration
def test_menu_to_quotation_service_flow(db_session, test_chef_user, test_chef, test_client_profile, test_dish, test_menu):
    # Ensure upstream entities exist (menu/dish/client belong to chef).
    assert test_menu.chef_id == test_chef.id
    assert test_dish.chef_id == test_chef.id
    assert test_client_profile.chef_id == test_chef.id

    service = QuotationService(
        QuotationRepository(db_session),
        ChefRepository(db_session),
        ClientRepository(db_session),
        MenuRepository(db_session),
        DishRepository(db_session),
    )

    quotation = service.create_quotation(
        test_chef_user.id,
        {
            "client_id": test_client_profile.id,
            "menu_id": test_menu.id,
            "event_date": (utcnow_naive() + timedelta(days=10)).date(),
            "number_of_people": 12,
            "notes": "Integration workflow quotation",
            "items": [
                {
                    "dish_id": test_dish.id,
                    "quantity": 3,
                    "description": "Dish-based item",
                }
            ],
        },
    )

    assert quotation.id is not None
    assert quotation.items
    assert quotation.items[0].dish_id == test_dish.id
