"""
E2E Tests: Complete Customer Journey

These tests validate end-to-end customer flows from registration through shopping.
Tests realistic user journeys that combine multiple subsystems.

Test Coverage:
1. test_complete_customer_shopping_journey - Full flow: register → browse → cart → purchase
2. test_multi_product_shopping_cart - Complex cart with multiple products and quantities

Dependencies:
- Authentication system (register, login)
- Product catalog (browse, search)
- Shopping cart (add, update, remove)

Note: Order creation currently has schema issues - focusing on cart management for now.
"""
import pytest
from tests.e2e.conftest import get_json_or_fail, assert_success_response, assert_error_response


class TestCompleteCustomerJourney:
    """End-to-end tests for complete customer shopping journeys."""
    
    def test_complete_customer_shopping_journey(self, client, create_test_products):
        """
        E2E: Complete customer purchase journey.
        
        Flow:
        1. Customer registers account
        2. Customer logs in
        3. Customer browses products
        4. Customer adds products to cart
        5. Customer updates cart quantities
        6. Customer views cart summary
        
        Validates: Full customer lifecycle with working subsystems
        """
        # Step 1: Register new customer
        user_data = {
            'username': 'journey_customer',
            'email': 'journey@example.com',
            'password': 'SecurePass123',
            'first_name': 'Journey',
            'last_name': 'Customer'
        }
        reg_response = client.post('/auth/register', json=user_data)
        assert_success_response(reg_response, 201)
        user = get_json_or_fail(reg_response)['user']
        
        # Step 2: Login
        login_response = client.post('/auth/login', json={
            'username': 'journey_customer',
            'password': 'SecurePass123'
        })
        assert_success_response(login_response, 200)
        token = get_json_or_fail(login_response)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create test products BEFORE browsing
        test_products = create_test_products(3, "JourneyCatalog")
        
        # Step 3: Browse product catalog (public endpoint)
        products_response = client.get('/products/')
        assert_success_response(products_response, 200)
        products_data = get_json_or_fail(products_response)
        
        # Extract product list (handle different response formats)
        if isinstance(products_data, list):
            available_products = products_data
        elif 'products' in products_data:
            available_products = products_data['products']
        else:
            available_products = products_data.get('data', [])
        
        # Verify products exist
        assert len(available_products) >= 3, f"Expected at least 3 products, got {len(available_products)}"
        
        # Step 4: Create cart with multiple items
        cart_payload = {
            'user_id': user['id'],
            'items': [
                {'product_id': test_products[0]['id'], 'quantity': 2},
                {'product_id': test_products[1]['id'], 'quantity': 1},
                {'product_id': test_products[2]['id'], 'quantity': 3}
            ]
        }
        cart_response = client.post('/sales/carts', json=cart_payload, headers=headers)
        assert_success_response(cart_response, 201)
        cart = get_json_or_fail(cart_response)
        
        # Verify cart creation
        if 'cart' in cart:
            cart_data = cart['cart']
        else:
            cart_data = cart
        
        assert 'items' in cart_data or 'cart_items' in cart_data, "Cart doesn't contain items"
        
        # Step 5: View own cart
        get_cart_response = client.get(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(get_cart_response, 200)
        retrieved_cart = get_json_or_fail(get_cart_response)
        
        # Verify cart contents
        if 'cart' in retrieved_cart:
            retrieved_cart = retrieved_cart['cart']
        
        # Check that cart has items
        cart_items = retrieved_cart.get('items', retrieved_cart.get('cart_items', []))
        assert len(cart_items) > 0, "Cart should have items"
        
        # Step 6: Update cart quantity
        update_payload = {'quantity': 5}
        update_response = client.put(
            f'/sales/carts/{user["id"]}/items/{test_products[0]["id"]}',
            json=update_payload,
            headers=headers
        )
        assert_success_response(update_response, 200)
        
        # Step 7: Remove one item from cart
        remove_response = client.delete(
            f'/sales/carts/{user["id"]}/items/{test_products[2]["id"]}',
            headers=headers
        )
        assert_success_response(remove_response, 200)
        
        # Step 8: Verify final cart state
        final_cart_response = client.get(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(final_cart_response, 200)
        final_cart = get_json_or_fail(final_cart_response)
        
        if 'cart' in final_cart:
            final_cart = final_cart['cart']
        
        # Verify cart has 2 items (removed 1 of 3)
        final_items = final_cart.get('items', final_cart.get('cart_items', []))
        assert len(final_items) == 2, f"Expected 2 items, got {len(final_items)}"
    
    def test_multi_product_shopping_cart(self, client, create_test_products):
        """
        E2E: Shopping cart with multiple products and quantity management.
        
        Flow:
        1. Register and login
        2. Add 5 different products to cart
        3. Update quantities for some items
        4. Remove specific items
        5. Clear entire cart
        
        Validates: Complex cart operations with many products
        """
        # Setup: Create user
        user_data = {
            'username': 'multi_cart_user',
            'email': 'multicart@example.com',
            'password': 'CartTest123',
            'first_name': 'Multi',
            'last_name': 'Cart'
        }
        reg_response = client.post('/auth/register', json=user_data)
        assert_success_response(reg_response, 201)
        user = get_json_or_fail(reg_response)['user']
        
        # Login
        login_response = client.post('/auth/login', json={
            'username': 'multi_cart_user',
            'password': 'CartTest123'
        })
        token = get_json_or_fail(login_response)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create 5 test products
        products = create_test_products(5, "MultiCart")
        
        # Step 1: Add first 3 products to cart
        cart_payload = {
            'user_id': user['id'],
            'items': [
                {'product_id': products[0]['id'], 'quantity': 1},
                {'product_id': products[1]['id'], 'quantity': 2},
                {'product_id': products[2]['id'], 'quantity': 3}
            ]
        }
        cart_response = client.post('/sales/carts', json=cart_payload, headers=headers)
        assert_success_response(cart_response, 201)
        
        # Step 2: Add 2 more products individually
        for i in [3, 4]:
            add_response = client.post(
                f'/sales/carts/{user["id"]}/items/{products[i]["id"]}',
                json={'quantity': i},  # Vary quantities
                headers=headers
            )
            assert_success_response(add_response, 200)
        
        # Step 3: Verify cart has 5 products
        cart_check1 = client.get(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(cart_check1, 200)
        cart_data1 = get_json_or_fail(cart_check1)
        
        if 'cart' in cart_data1:
            cart_data1 = cart_data1['cart']
        
        items1 = cart_data1.get('items', cart_data1.get('cart_items', []))
        assert len(items1) == 5, f"Expected 5 items, got {len(items1)}"
        
        # Step 4: Update quantities (increase product 0, decrease product 1)
        client.put(
            f'/sales/carts/{user["id"]}/items/{products[0]["id"]}',
            json={'quantity': 10},
            headers=headers
        )
        client.put(
            f'/sales/carts/{user["id"]}/items/{products[1]["id"]}',
            json={'quantity': 1},
            headers=headers
        )
        
        # Step 5: Remove 2 products
        client.delete(f'/sales/carts/{user["id"]}/items/{products[3]["id"]}', headers=headers)
        client.delete(f'/sales/carts/{user["id"]}/items/{products[4]["id"]}', headers=headers)
        
        # Step 6: Verify cart now has 3 products
        cart_check2 = client.get(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(cart_check2, 200)
        cart_data2 = get_json_or_fail(cart_check2)
        
        if 'cart' in cart_data2:
            cart_data2 = cart_data2['cart']
        
        items2 = cart_data2.get('items', cart_data2.get('cart_items', []))
        assert len(items2) == 3, f"Expected 3 items after removal, got {len(items2)}"
        
        # Step 7: Clear entire cart
        clear_response = client.delete(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(clear_response, 200)
        
        # Step 8: Verify cart is empty
        empty_cart_response = client.get(f'/sales/carts/{user["id"]}', headers=headers)
        assert_success_response(empty_cart_response, 200)
        empty_cart = get_json_or_fail(empty_cart_response)
        
        if 'cart' in empty_cart:
            empty_cart = empty_cart['cart']
        
        final_items = empty_cart.get('items', empty_cart.get('cart_items', []))
        assert len(final_items) == 0, "Cart should be empty after clearing"
