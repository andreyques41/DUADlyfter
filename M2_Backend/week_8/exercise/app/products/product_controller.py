from flask import jsonify, request
from datetime import date

class ProductController:
    def __init__(self, product_service, logger):
        """
        Product controller: Handles presentation logic and HTTP responses.
        """
        self.product_service = product_service
        self.logger = logger

    def get_all(self):
        """
        Return a list of all products.
        """
        products = self.product_service.get_all_products()
        return jsonify({"products": products}), 200

    def get_by_id(self, product_id):
        """
        Return a product by its ID.
        """
        product = self.product_service.get_product_by_id(product_id)
        if product is None:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"product": product}), 200

    def post(self):
        """
        Create a new product. Admin only.
        """
        try:
            data = request.get_json()
            if not data:
                self.logger.warning("No JSON data provided in product creation")
                return jsonify({"error": "No JSON data provided"}), 400
            required_fields = ["name", "price", "quantity"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.logger.warning(f"Missing fields in product creation: {missing_fields}")
                return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
            if data.get("entry_date"):
                try:
                    entry_date = date.fromisoformat(data["entry_date"])
                except ValueError:
                    self.logger.warning("Invalid date format in product creation")
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            else:
                entry_date = date.today()
            product_id = self.product_service.create_product(
                name=data["name"],
                price=data["price"],
                quantity=data["quantity"],
                entry_date=entry_date
            )
            if not product_id:
                self.logger.error("Product creation failed in service")
                return jsonify({"error": "Product creation failed"}), 500
            return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
        except Exception as e:
            self.logger.error(f"Create product error: {e}")
            return jsonify({"error": "Product creation failed"}), 500

    def put(self, product_id):
        """
        Update an existing product. Admin only.
        """
        try:
            data = request.get_json()
            if not data:
                self.logger.warning("No JSON data provided in product update")
                return jsonify({"error": "No JSON data provided"}), 400
            if data.get("entry_date"):
                try:
                    data["entry_date"] = date.fromisoformat(data["entry_date"])
                except ValueError:
                    self.logger.warning("Invalid date format in product update")
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            else:
                data["entry_date"] = date.today()
            result = self.product_service.update_product(product_id, **data)
            if not result:
                self.logger.error("Product update failed in service")
                return jsonify({"error": "Product update failed"}), 500
            return jsonify({"message": "Product updated successfully"}), 200
        except Exception as e:
            self.logger.error(f"Update product error: {e}")
            return jsonify({"error": "Product update failed"}), 500

    def delete(self, product_id):
        """
        Delete an existing product. Admin only.
        """
        try:
            success, error = self.product_service.delete_product(product_id)
            if not success:
                if error == "Product not found":
                    self.logger.warning(f"Product not found for delete: {product_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Product delete failed: {error}")
                return jsonify({"error": error}), 500
            return jsonify({"message": "Product deleted successfully"}), 200
        except Exception as e:
            self.logger.error(f"Delete product error: {e}")
            return jsonify({"error": "Product deletion failed"}), 500
