"""
Orders Routes Module

Provides RESTful API endpoints for orders management:
- GET /orders - List orders (REST standard: auto-filtered by user role)
- GET /orders/<order_id> - Get specific order (user access)
- POST /orders - Create new order (user/admin)
- PUT /orders/<order_id> - Update order (admin only)
- PATCH /orders/<order_id>/status - Update order status (admin only)
- DELETE /orders/<order_id> - Delete order (admin only, limited status)
- POST /orders/<order_id>/cancel - Cancel order (user access)

Features:
- REST standard: GET /orders auto-filters based on user role
- User authentication required for all operations
- Users can only access their own orders (or admins can access any)
- Comprehensive order business logic delegated to OrderController
- Input validation handled by controller layer
- Detailed error handling and logging in controller
"""
# Common imports
from flask import Blueprint
from flask.views import MethodView

# Auth imports (for decorators)
from app.core.middleware import token_required_with_repo, admin_required_with_repo

# Controller imports
from app.sales.controllers.order_controller import OrderController

class OrderListAPI(MethodView):
    """
    REST standard GET /orders endpoint.
    
    Behavior:
    - Regular users: See only their own orders (auto-filtered by user_id)
    - Admins: See all orders in the system
    """
    init_every_request = False

    def __init__(self):
        self.controller = OrderController()

    @token_required_with_repo
    def get(self):
        """Get orders collection - auto-filtered based on user role."""
        return self.controller.get_list()

class OrderAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = OrderController()

    @token_required_with_repo
    def get(self, order_id):
        """Get specific order by ID."""
        return self.controller.get(order_id)

    @token_required_with_repo
    def post(self):
        """Create new order."""
        return self.controller.post()

    @admin_required_with_repo
    def put(self, order_id):
        """Update existing order (admin only)."""
        return self.controller.put(order_id)

    @admin_required_with_repo
    def delete(self, order_id):
        """Delete order (admin only, limited status)."""
        return self.controller.delete(order_id)

class OrderStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = OrderController()

    @admin_required_with_repo
    def patch(self, order_id):
        """Update order status (admin only)."""
        return self.controller.patch_status(order_id)

class OrderCancelAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = OrderController()

    @token_required_with_repo
    def post(self, order_id):
        """Cancel order (user access - owner or admin)."""
        return self.controller.cancel(order_id)

# Import blueprint from sales module
from app.sales import sales_bp

# Register routes when this module is imported by sales/__init__.py
def register_orders_routes(sales_bp):
    # REST standard: Collection endpoint (auto-filtered by role)
    sales_bp.add_url_rule('/orders', methods=['GET'], view_func=OrderListAPI.as_view('order_list'))
    
    # REST standard: Create and individual operations
    sales_bp.add_url_rule('/orders', methods=['POST'], view_func=OrderAPI.as_view('order_create'))
    sales_bp.add_url_rule('/orders/<int:order_id>', view_func=OrderAPI.as_view('order'))
    
    # Order status operations
    sales_bp.add_url_rule('/orders/<int:order_id>/status', view_func=OrderStatusAPI.as_view('order_status'))
    
    # Order cancel operations
    sales_bp.add_url_rule('/orders/<int:order_id>/cancel', view_func=OrderCancelAPI.as_view('order_cancel'))
