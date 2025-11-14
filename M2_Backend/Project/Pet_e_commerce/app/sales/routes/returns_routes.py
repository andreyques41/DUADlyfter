"""
Returns Routes Module

Provides RESTful API endpoints for returns management:
- GET /returns - List returns (REST standard: auto-filtered by user role)
- GET /returns/<return_id> - Get specific return (user access)
- POST /returns - Create new return request (user access)
- PUT /returns/<return_id> - Update return (admin only)
- PATCH /returns/<return_id>/status - Update return status (admin only)
- DELETE /returns/<return_id> - Delete return (admin only, limited status)

Features:
- REST standard: GET /returns auto-filters based on user role
- User authentication required for all operations
- Users can only access their own returns (or admins can access any)
- Comprehensive return business logic delegated to ReturnController
- Input validation handled by controller layer
- Detailed error handling and logging in controller
"""

# Common imports
from flask import Blueprint
from flask.views import MethodView

# Auth imports (for decorators)
from app.core.middleware import token_required_with_repo, admin_required_with_repo

# Controller imports
from app.sales.controllers.return_controller import ReturnController

class ReturnListAPI(MethodView):
    """
    REST standard GET /returns endpoint.
    
    Behavior:
    - Regular users: See only their own returns (auto-filtered by user_id)
    - Admins: See all returns in the system
    """
    init_every_request = False

    def __init__(self):
        self.controller = ReturnController()

    @token_required_with_repo
    def get(self):
        """Get returns collection - auto-filtered based on user role."""
        return self.controller.get_list()

class ReturnAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = ReturnController()

    @token_required_with_repo
    def get(self, return_id):
        """Get specific return by ID."""
        return self.controller.get(return_id)

    @token_required_with_repo
    def post(self):
        """Create new return request."""
        return self.controller.post()

    @admin_required_with_repo
    def put(self, return_id):
        """Update existing return (admin only)."""
        return self.controller.put(return_id)

    @admin_required_with_repo
    def delete(self, return_id):
        """Delete return (admin only, limited status)."""
        return self.controller.delete(return_id)

class ReturnStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = ReturnController()

    @admin_required_with_repo
    def patch(self, return_id):
        """Update return status (admin only)."""
        return self.controller.patch_status(return_id)

# Import blueprint from sales module
from app.sales import sales_bp

# Register routes when this module is imported by sales/__init__.py
def register_returns_routes(sales_bp):
    # REST standard: Collection endpoint (auto-filtered by role)
    sales_bp.add_url_rule('/returns', methods=['GET'], view_func=ReturnListAPI.as_view('return_list'))
    
    # REST standard: Create and individual operations
    sales_bp.add_url_rule('/returns', methods=['POST'], view_func=ReturnAPI.as_view('return_create'))
    sales_bp.add_url_rule('/returns/<int:return_id>', view_func=ReturnAPI.as_view('return'))
    
    # Return status operations
    sales_bp.add_url_rule('/returns/<int:return_id>/status', view_func=ReturnStatusAPI.as_view('return_status'))
