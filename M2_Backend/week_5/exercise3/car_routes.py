import logging
from flask import request, jsonify
from flask.views import MethodView
from exercise2.car_repository import CarRepository

logger = logging.getLogger(__name__)


class CarAPI(MethodView):
    """CRUD operations for cars - Complete car management functionality"""

    init_every_request = False

    def __init__(self, db_manager):
        self.logger = logger
        self.car_repository = CarRepository(db_manager)

    def get(self, car_id=None):
        """Retrieve all cars or specific car."""
        try:
            # Get car(s) using repository method with optional filters
            result = self.car_repository.get_cars(
                car_id, request_args=request.args if car_id is None else None
            )

            # Handle not found case for single car
            if car_id is not None and result is None:
                self.logger.warning(f"Car not found: {car_id}")
                return jsonify({"error": "Car not found"}), 404

            # Handle database errors
            if result is False:
                self.logger.error("Database error occurred while retrieving cars")
                return jsonify({"error": "Database error occurred"}), 500

            self.logger.info(f"Car(s) retrieved: {'all' if car_id is None else car_id}")
            return jsonify({"cars": result if isinstance(result, list) else [result]})

        except Exception as e:
            self.logger.error(f"Error retrieving car(s): {e}")
            return jsonify({"error": "Failed to retrieve car data"}), 500

    def post(self):
        """Create new car with validation."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Basic validation for required fields
            required_fields = ["model_id", "year", "state_id"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    400,
                )

            # Create car using repository
            result = self.car_repository.insert_new_car(
                model_id=data["model_id"], year=data["year"], state_id=data["state_id"]
            )

            if result is False:
                self.logger.error("Car creation failed in database")
                return jsonify({"error": "Car creation failed"}), 500

            self.logger.info(
                f"Car created: model_id {data['model_id']}, year {data['year']}"
            )
            return jsonify({"message": "Car created successfully"}), 201

        except Exception as e:
            self.logger.error(f"Error creating car: {e}")
            return jsonify({"error": "Car creation failed"}), 500

    def put(self, car_id):
        """Update car data - only provided fields are updated, existing values are kept for missing fields."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Check if car exists first and get existing data
            existing_car = self.car_repository.get_by_id(car_id)
            if existing_car is None:
                self.logger.warning(
                    f"Car update attempt for non-existent car: {car_id}"
                )
                return jsonify({"error": "Car not found"}), 404

            if existing_car is False:
                return jsonify({"error": "Database error occurred"}), 500

            # Merge request data with existing car data (request data takes priority)
            updated_data = {
                "model_id": data.get("model_id", existing_car["model_id"]),
                "year": data.get("year", existing_car["year"]),
                "state_id": data.get("state_id", existing_car["state_id"]),
            }

            # Update car using repository
            result = self.car_repository.update_car(
                _id=car_id,
                model_id=updated_data["model_id"],
                year=updated_data["year"],
                state_id=updated_data["state_id"],
            )

            if result is False:
                self.logger.error(f"Car update failed for {car_id}")
                return jsonify({"error": "Car update failed"}), 500

            self.logger.info(f"Car updated: {car_id}")
            return jsonify({"message": "Car updated successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error updating car: {e}")
            return jsonify({"error": "Car update failed"}), 500

    def delete(self, car_id):
        """Delete car by ID."""
        try:
            success, error = self.car_repository.delete_car(car_id)

            if not success:
                if error == "Car not found":
                    self.logger.warning(
                        f"Delete attempt for non-existent car: {car_id}"
                    )
                    return jsonify({"error": error}), 404
                self.logger.error(f"Car deletion failed for {car_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Car deleted: {car_id}")
            return jsonify({"message": "Car deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting car: {e}")
            return jsonify({"error": "Car deletion failed"}), 500
