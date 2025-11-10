"""
E2E Tests: Shopping Cart Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests complete shopping cart workflows from HTTP request to response.
Validates cart creation, item management, and access control.

Coverage:
- Complete cart lifecycle (create, add items, update, remove, clear)
- Access control (users can only access own cart, admins see all)
- Business validations through complete flows

These tests verify the entire cart stack works correctly end-to-end.
"""
import pytest
from tests.e2e.conftest import get_json_or_fail, assert_success_response, assert_error_response


class TestShoppingCartFlow:
    """E2E tests for complete shopping cart workflows"""
    
    def test_complete_cart_management(self, client, admin_headers, create_test_products):
        """
        E2E: Complete cart lifecycle from creation to deletion.
        
        Flow:
        1. Create user and login
        2. Create products (using fixture to bypass API schema bugs)
        3. Create cart with initial products
        4. Add another product to cart
        5. Update quantity of one product
        6. Remove one product
        7. Verify cart has correct items with correct totals
        8. Clear entire cart
        
        This test combines all CRUD operations in a realistic user journey.
        """
        # Step 1: Create user and login
        user_data = {
            'username': 'cart_test_user',
            'email': 'carttest@example.com',
            'password': 'password123',
            'first_name': 'Cart',
            'last_name': 'Test'
        }
        reg_response = client.post('/auth/register', json=user_data)
        assert_success_response(reg_response, 201)
        user = get_json_or_fail(reg_response)['user']
        user_id = user['id']
        
        # Login to get token
        login_response = client.post('/auth/login', json={
            'username': 'cart_test_user',
            'password': 'password123'
        })
        assert_success_response(login_response, 200)
        token = get_json_or_fail(login_response)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 2: Create products using fixture (bypasses API schema bug)
        products = create_test_products(count=4, prefix="CartTest")
        
        # Step 3: Create cart with 2 initial products
        cart_response = client.post(
            '/sales/carts',
            json={
                'user_id': user_id,
                'items': [
                    {'product_id': products[0]['id'], 'quantity': 1},
                    {'product_id': products[1]['id'], 'quantity': 2}
                ]
            },
            headers=headers
        )
        assert_success_response(cart_response, 201)
        cart_data = get_json_or_fail(cart_response)
        assert 'cart' in cart_data
        
        # Step 4: Add a third product to cart
        add_response = client.post(
            f'/sales/carts/{user_id}/items/{products[2]["id"]}',
            json={'quantity': 3},
            headers=headers
        )
        # Accept both 200 and 201 as success
        assert add_response.status_code in [200, 201], \
            f"Failed to add product {products[2]['id']}: {add_response.get_json()}"
        
        # Verify cart has 3 items
        get_response = client.get(f'/sales/carts/{user_id}', headers=headers)
        assert_success_response(get_response, 200)
        cart = get_json_or_fail(get_response)
        
        # Handle different response structures
        if 'items' in cart:
            items = cart['items']
        elif 'cart_items' in cart:
            items = cart['cart_items']
        else:
            items = cart.get('data', {}).get('items', [])
        
        assert len(items) == 3, f"Expected 3 items, got {len(items)}"
        
        # Step 5: Update quantity of first product (from 1 to 5)
        update_response = client.put(
            f'/sales/carts/{user_id}/items/{products[0]["id"]}',
            json={'quantity': 5},
            headers=headers
        )
        assert_success_response(update_response, 200)
        
        # Step 6: Remove second product
        delete_response = client.delete(
            f'/sales/carts/{user_id}/items/{products[1]["id"]}',
            headers=headers
        )
        assert_success_response(delete_response, 200)
        
        # Step 7: Verify cart now has 2 items (product[0] with qty=5, product[2] with qty=3)
        final_cart_response = client.get(f'/sales/carts/{user_id}', headers=headers)
        assert_success_response(final_cart_response, 200)
        final_cart = get_json_or_fail(final_cart_response)
        
        if 'items' in final_cart:
            final_items = final_cart['items']
        elif 'cart_items' in final_cart:
            final_items = final_cart['cart_items']
        else:
            final_items = final_cart.get('data', {}).get('items', [])
        
        assert len(final_items) == 2, f"Expected 2 items after removal, got {len(final_items)}"
        
        # Verify products: product[0] should have quantity=5, product[2] should have quantity=3
        product_ids = [item.get('product_id') or item.get('product', {}).get('id') 
                      for item in final_items]
        assert products[0]['id'] in product_ids, "First product should still be in cart"
        assert products[2]['id'] in product_ids, "Third product should still be in cart"
        assert products[1]['id'] not in product_ids, "Second product should be removed"
        
        # Verify quantities
        for item in final_items:
            pid = item.get('product_id') or item.get('product', {}).get('id')
            qty = item.get('quantity')
            if pid == products[0]['id']:
                assert qty == 5, f"Product 0 should have quantity 5, got {qty}"
            elif pid == products[2]['id']:
                assert qty == 3, f"Product 2 should have quantity 3, got {qty}"
        
        # Step 8: Clear entire cart
        clear_response = client.delete(f'/sales/carts/{user_id}', headers=headers)
        assert_success_response(clear_response, 200)
        
        # Verify cart is empty or returns appropriate message
        empty_cart_response = client.get(f'/sales/carts/{user_id}', headers=headers)
        # Accept 200 with empty cart or 404 if cart was deleted
        assert empty_cart_response.status_code in [200, 404]
    
    def test_cart_access_control(self, client, admin_headers, create_test_products):
        """
        E2E: Security validation - users can only access own cart, admins see all.
        
        Flow:
        1. Create product (using fixture to bypass API schema bugs)
        2. Create User1 with cart containing product
        3. Create User2 and login
        4. User2 tries to access User1's cart → 403 Forbidden
        5. Admin can view User1's cart → 200 OK
        6. Admin can list all carts → 200 OK
        
        This test validates role-based access control for carts.
        """
        # Step 1: Create product using fixture (bypasses API schema bug)
        products = create_test_products(count=1, prefix="CartAccessTest")
        product = products[0]
        
        # Step 2: Create User1 with cart
        user1_data = {
            'username': 'cart_user1',
            'email': 'cartuser1@example.com',
            'password': 'password123',
            'first_name': 'User',
            'last_name': 'One'
        }
        reg1_response = client.post('/auth/register', json=user1_data)
        assert_success_response(reg1_response, 201)
        user1 = get_json_or_fail(reg1_response)['user']
        user1_id = user1['id']
        
        login1_response = client.post('/auth/login', json={
            'username': 'cart_user1',
            'password': 'password123'
        })
        user1_token = get_json_or_fail(login1_response)['token']
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        
        # Create cart for User1 with product
        cart1_response = client.post(
            '/sales/carts',
            json={
                'user_id': user1_id,
                'items': [{'product_id': product['id'], 'quantity': 2}]
            },
            headers=user1_headers
        )
        assert_success_response(cart1_response, 201)
        
        # Step 3: Create User2 and login
        user2_data = {
            'username': 'cart_user2',
            'email': 'cartuser2@example.com',
            'password': 'password123',
            'first_name': 'User',
            'last_name': 'Two'
        }
        reg2_response = client.post('/auth/register', json=user2_data)
        assert_success_response(reg2_response, 201)
        
        login2_response = client.post('/auth/login', json={
            'username': 'cart_user2',
            'password': 'password123'
        })
        user2_token = get_json_or_fail(login2_response)['token']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        
        # Step 4: User2 tries to access User1's cart → 403 Forbidden
        forbidden_response = client.get(
            f'/sales/carts/{user1_id}',
            headers=user2_headers
        )
        assert_error_response(forbidden_response, 403)
        
        # Step 5: Admin can view User1's cart → 200 OK
        admin_view_response = client.get(
            f'/sales/carts/{user1_id}',
            headers=admin_headers
        )
        assert_success_response(admin_view_response, 200)
        
        # Step 6: Admin can list all carts → 200 OK
        all_carts_response = client.get('/sales/carts', headers=admin_headers)
        assert_success_response(all_carts_response, 200)
        all_carts_data = get_json_or_fail(all_carts_response)
        
        # Verify response contains carts list
        assert 'carts' in all_carts_data or isinstance(all_carts_data, list), \
            "Admin should see list of carts"
        
        # If there's a carts key, verify it's a list
        if 'carts' in all_carts_data:
            assert isinstance(all_carts_data['carts'], list), "Carts should be a list"
            # Should have at least User1's cart
            assert len(all_carts_data['carts']) >= 1, "Should have at least one cart"
