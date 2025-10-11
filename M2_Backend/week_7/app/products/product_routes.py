from flask import request, jsonify
from flask.views import MethodView
from app.products.product_repository import ProductRepository
from app.auth.user_repository import UserRepository
from app.utilities.jwt_manager import JWT_Manager
from datetime import date

jwt_manager = JWT_Manager()


class ProductAPI(MethodView):
    """CRUD operations for products."""
    
    def __init__(self, db_manager):
        self.product_repository = ProductRepository(db_manager)
        self.user_repository = UserRepository(db_manager)
    
    def get(self, product_id=None):
        """Get all products or specific product by ID."""
        try:
            if product_id:
                result = self.product_repository.get_by_id(product_id)
                if result is False:
                    return jsonify({"error": "Database error"}), 500
                if result is None:
                    return jsonify({"error": "Product not found"}), 404
                return jsonify({"product": result}), 200
            else:
                result = self.product_repository.get_all()
                if result is False:
                    return jsonify({"error": "Database error"}), 500
                return jsonify({"products": result}), 200
        except Exception as e:
            print(f"[ERROR] Get product error: {e}")
            return jsonify({"error": "Failed to retrieve products"}), 500
    
    def post(self):
        """Create new product. Only admin can create products."""
        try:
            # Verify token and check admin role
            user_data = jwt_manager.get_user_from_request()
            if not user_data:
                return jsonify({"error": "Unauthorized"}), 401
            
            user_id = user_data.get('user_id')
            if not jwt_manager.is_admin(self.user_repository, user_id):
                return jsonify({"error": "Forbidden: Admin access required"}), 403
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            required_fields = ["name", "price", "quantity"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
            
            # Parse entry_date if provided
            entry_date = None
            if data.get("entry_date"):
                try:
                    entry_date = date.fromisoformat(data["entry_date"])
                except ValueError:
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
            product_id = self.product_repository.create_product(
                name=data["name"],
                price=data["price"],
                quantity=data["quantity"],
                entry_date=entry_date
            )
            
            if product_id is False:
                return jsonify({"error": "Product creation failed"}), 500
            
            return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
        except Exception as e:
            print(f"[ERROR] Create product error: {e}")
            return jsonify({"error": "Product creation failed"}), 500
    
    def put(self, product_id):
        """Update product. Only admin can update products."""
        try:
            # Verify token and check admin role
            user_data = jwt_manager.get_user_from_request()
            if not user_data:
                return jsonify({"error": "Unauthorized"}), 401
            
            user_id = user_data.get('user_id')
            if not jwt_manager.is_admin(self.user_repository, user_id):
                return jsonify({"error": "Forbidden: Admin access required"}), 403
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            # Check if product exists
            existing = self.product_repository.get_by_id(product_id)
            if existing is False:
                return jsonify({"error": "Database error"}), 500
            if existing is None:
                return jsonify({"error": "Product not found"}), 404
            
            # Parse entry_date if provided
            if data.get("entry_date"):
                try:
                    data["entry_date"] = date.fromisoformat(data["entry_date"])
                except ValueError:
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
            result = self.product_repository.update_product(product_id, **data)
            
            if result is False:
                return jsonify({"error": "Product update failed"}), 500
            
            return jsonify({"message": "Product updated successfully"}), 200
        except Exception as e:
            print(f"[ERROR] Update product error: {e}")
            return jsonify({"error": "Product update failed"}), 500
    
    def delete(self, product_id):
        """Delete product. Only admin can delete products."""
        try:
            # Verify token and check admin role
            user_data = jwt_manager.get_user_from_request()
            if not user_data:
                return jsonify({"error": "Unauthorized"}), 401
            
            user_id = user_data.get('user_id')
            if not jwt_manager.is_admin(self.user_repository, user_id):
                return jsonify({"error": "Forbidden: Admin access required"}), 403
            
            success, error = self.product_repository.delete_product(product_id)
            
            if not success:
                if error == "Product not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Product deleted successfully"}), 200
        except Exception as e:
            print(f"[ERROR] Delete product error: {e}")
            return jsonify({"error": "Product deletion failed"}), 500
