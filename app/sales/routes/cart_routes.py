"""
Cart Routes Module

Provides RESTful API endpoints for shopping cart management.
Delegates to CartController for request processing.

Endpoints:
- GET /carts - Get all carts (admin) or own cart (customer)
- POST /carts - Create new cart
- GET /carts/<user_id> - Get specific user's cart
- PUT /carts/<user_id> - Update cart contents
- DELETE /carts/<user_id> - Clear entire cart
- POST /carts/<user_id>/items/<product_id> - Add item to cart
- PUT /carts/<user_id>/items/<product_id> - Update item quantity
- DELETE /carts/<user_id>/items/<product_id> - Remove item from cart

Features:
- User authentication required for all operations
- Role-based access: users access own cart, admins access any cart
- Caching for improved performance (5 min TTL)
- Automatic cache invalidation on modifications
"""
from flask import Blueprint
from flask.views import MethodView
from app.core.middleware import token_required_with_repo
from app.sales.controllers.cart_controller import CartController


class CartAPI(MethodView):
    """CRUD operations for shopping carts - user authentication required"""
    
    init_every_request = False

    def __init__(self):
        """Initialize the cart API with controller dependency."""
        self.controller = CartController()

    @token_required_with_repo
    def get(self, user_id=None):
        """
        Retrieve cart(s):
        - No user_id (GET /carts): Admins see all carts, customers see own cart
        - With user_id (GET /carts/<user_id>): Access specific user's cart
        """
        return self.controller.get(user_id)

    @token_required_with_repo  
    def post(self):
        """
        Create new cart for user.
        Users can create own cart, admins can create any.
        """
        return self.controller.post()

    @token_required_with_repo
    def put(self, user_id):
        """
        Update cart contents.
        Users can update own cart, admins can update any.
        """
        return self.controller.put(user_id)

    @token_required_with_repo
    def delete(self, user_id):
        """
        Clear entire cart.
        Users can clear own cart, admins can clear any.
        """
        return self.controller.delete(user_id)


class CartItemAPI(MethodView):
    """Operations for cart items - add/update/remove items"""
    
    init_every_request = False

    def __init__(self):
        """Initialize cart item API with controller dependency."""
        self.controller = CartController()

    @token_required_with_repo
    def post(self, user_id, product_id):
        """
        Add item to cart or update quantity if already exists.
        Users can add to own cart, admins can add to any.
        """
        return self.controller.add_item(user_id, product_id)

    @token_required_with_repo
    def put(self, user_id, product_id):
        """
        Update quantity of an existing item in cart.
        Users can update own cart, admins can update any.
        """
        return self.controller.update_item(user_id, product_id)

    @token_required_with_repo
    def delete(self, user_id, product_id):
        """
        Remove specific item from cart.
        Users can remove from own cart, admins can remove from any.
        """
        return self.controller.remove_item(user_id, product_id)


# Register routes when this module is imported by sales/__init__.py
def register_cart_routes(sales_bp):
    """Register all cart routes with the sales blueprint."""
    # Cart operations - RESTful pattern
    sales_bp.add_url_rule('/carts', methods=['GET', 'POST'], view_func=CartAPI.as_view('carts_list'))
    sales_bp.add_url_rule('/carts/<int:user_id>', methods=['GET', 'PUT', 'DELETE'], view_func=CartAPI.as_view('carts'))

    # Cart item operations (nested resource)
    sales_bp.add_url_rule('/carts/<int:user_id>/items/<int:product_id>', 
                          methods=['POST', 'PUT', 'DELETE'], 
                          view_func=CartItemAPI.as_view('cart_items'))
