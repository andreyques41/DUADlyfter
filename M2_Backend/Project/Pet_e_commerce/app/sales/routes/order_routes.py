"""
Orders Routes Module

Provides RESTful API endpoints for orders management:
- GET /orders/<order_id> - Get specific order (user access)
- GET /orders/user/<user_id> - Get user's orders (user access)
- POST /orders - Create new order (user/admin)
- PUT /orders/<order_id> - Update order (admin only)
- PATCH /orders/<order_id>/status - Update order status (admin only)
- DELETE /orders/<order_id> - Delete order (admin only, limited status)
- POST /orders/<order_id>/cancel - Cancel order (user access)
- GET /admin/orders - Get all orders (admin only)

Features:
- User authentication required for all operations
- Users can only access their own orders (or admins can access any)
- Comprehensive order business logic through service layer
- Input validation using schemas
- Detailed error handling and logging
"""
from flask import request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from app.sales.services.order_service import OrdersService
from app.sales.schemas.order_schema import (
    order_registration_schema,
    order_update_schema,
    order_status_update_schema,
    order_response_schema,
    orders_response_schema
)
from app.sales.models.order import OrderStatus
from app.auth.services import token_required, admin_required
from app.shared.utils import is_admin_user
from config.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

DB_PATH = './orders.json'

class OrderAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.order_service = OrdersService(DB_PATH)

    @token_required
    def get(self, order_id):
        try:
            if not self.order_service.check_user_access(g.current_user, is_admin_user(), order_id=order_id):
                return jsonify({"error": "Access denied"}), 403
            
            order = self.order_service.get_orders(order_id)
            if order is None:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify(order_response_schema.dump(order)), 200
        except Exception:
            return jsonify({"error": "Failed to retrieve order"}), 500

    @token_required
    def post(self):
        try:
            order_data = order_registration_schema.load(request.json)
            
            if not is_admin_user() and order_data.user_id != g.current_user.id:
                return jsonify({"error": "Access denied"}), 403
            
            created_order, error = self.order_service.create_order(order_data)
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Order created successfully",
                "order": order_response_schema.dump(created_order)
            }), 201
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception:
            return jsonify({"error": "Failed to create order"}), 500

    @token_required
    @admin_required
    def put(self, order_id):
        try:
            order_data = order_update_schema.load(request.json)
            
            existing_order = self.order_service.get_orders(order_id)
            if not existing_order:
                return jsonify({"error": "Order not found"}), 404
            
            for key, value in order_data.items():
                if key == 'status':
                    value = OrderStatus(value)
                setattr(existing_order, key, value)
            
            updated_order, error = self.order_service.update_order(order_id, existing_order)
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Order updated successfully",
                "order": order_response_schema.dump(updated_order)
            }), 200
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception:
            return jsonify({"error": "Failed to update order"}), 500

    @token_required
    @admin_required
    def delete(self, order_id):
        try:
            success, error = self.order_service.delete_order(order_id)
            if error:
                return jsonify({"error": error}), 400 if "No order found" not in error else 404
            
            return jsonify({"message": "Order deleted successfully"}), 200
        except Exception:
            return jsonify({"error": "Failed to delete order"}), 500

class UserOrdersAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.order_service = OrdersService(DB_PATH)

    @token_required
    def get(self, user_id):
        try:
            if not self.order_service.check_user_access(g.current_user, is_admin_user(), user_id=user_id):
                return jsonify({"error": "Access denied"}), 403
            
            user_orders = self.order_service.get_orders(user_id=user_id)
            return jsonify({
                "total_orders": len(user_orders),
                "orders": orders_response_schema.dump(user_orders)
            }), 200
        except Exception:
            return jsonify({"error": "Failed to retrieve orders"}), 500

class OrderStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.order_service = OrdersService(DB_PATH)

    @token_required
    @admin_required
    def patch(self, order_id):
        try:
            status_data = order_status_update_schema.load(request.json)
            new_status = OrderStatus(status_data['status'])
            
            updated_order, error = self.order_service.update_order_status(order_id, new_status)
            if error:
                return jsonify({"error": error}), 400 if "No order found" not in error else 404
            
            return jsonify({
                "message": f"Order status updated to {new_status.value}",
                "order": order_response_schema.dump(updated_order)
            }), 200
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception:
            return jsonify({"error": "Failed to update order status"}), 500

class OrderCancelAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.order_service = OrdersService(DB_PATH)

    @token_required
    def post(self, order_id):
        try:
            if not self.order_service.check_user_access(g.current_user, is_admin_user(), order_id=order_id):
                return jsonify({"error": "Access denied"}), 403
            
            updated_order, error = self.order_service.cancel_order(order_id)
            if error:
                return jsonify({"error": error}), 400 if "No order found" not in error else 404
            
            return jsonify({
                "message": "Order cancelled successfully",
                "order": order_response_schema.dump(updated_order)
            }), 200
        except Exception:
            return jsonify({"error": "Failed to cancel order"}), 500

class AdminOrdersAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.order_service = OrdersService(DB_PATH)

    @token_required
    @admin_required  
    def get(self):
        try:
            all_orders = self.order_service.get_orders()
            return jsonify({
                "total_orders": len(all_orders),
                "orders": orders_response_schema.dump(all_orders)
            }), 200
        except Exception:
            return jsonify({"error": "Failed to retrieve orders"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

def register_orders_routes():
    # Individual order operations
    sales_bp.add_url_rule('/orders', methods=['POST'], view_func=OrderAPI.as_view('order_create'))
    sales_bp.add_url_rule('/orders/<int:order_id>', view_func=OrderAPI.as_view('order'))
    
    # User orders operations
    sales_bp.add_url_rule('/orders/user/<int:user_id>', view_func=UserOrdersAPI.as_view('user_orders'))
    
    # Order status operations
    sales_bp.add_url_rule('/orders/<int:order_id>/status', view_func=OrderStatusAPI.as_view('order_status'))
    
    # Order cancel operations
    sales_bp.add_url_rule('/orders/<int:order_id>/cancel', view_func=OrderCancelAPI.as_view('order_cancel'))
    
    # Admin order operations
    sales_bp.add_url_rule('/admin/orders', view_func=AdminOrdersAPI.as_view('admin_orders'))

register_orders_routes()
