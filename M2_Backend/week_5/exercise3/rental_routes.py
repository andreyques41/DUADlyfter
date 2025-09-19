import logging
from flask import request, jsonify
from flask.views import MethodView
from exercise2.rental_repository import RentalRepository

logger = logging.getLogger(__name__)


class RentalAPI(MethodView):
    """CRUD operations for rentals - Complete rental management functionality"""

    init_every_request = False

    def __init__(self, db_manager):
        self.logger = logger
        self.rental_repository = RentalRepository(db_manager)

    def get(self, rental_id=None):
        """Retrieve all rentals or specific rental."""
        try:
            # Get rental(s) using repository method with optional filters
            result = self.rental_repository.get_rentals(
                rental_id, request_args=request.args if rental_id is None else None
            )

            # Handle not found case for single rental
            if rental_id is not None and result is None:
                self.logger.warning(f"Rental not found: {rental_id}")
                return jsonify({"error": "Rental not found"}), 404

            # Handle database errors
            if result is False:
                self.logger.error("Database error occurred while retrieving rentals")
                return jsonify({"error": "Database error occurred"}), 500

            self.logger.info(
                f"Rental(s) retrieved: {'all' if rental_id is None else rental_id}"
            )
            return jsonify(
                {"rentals": result if isinstance(result, list) else [result]}
            )

        except Exception as e:
            self.logger.error(f"Error retrieving rental(s): {e}")
            return jsonify({"error": "Failed to retrieve rental data"}), 500

    def post(self):
        """Create new rental with validation."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Basic validation for required fields
            required_fields = ["user_id", "car_id"]
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

            # Create rental using repository
            result = self.rental_repository.insert_new_rental(
                user_id=data["user_id"], car_id=data["car_id"]
            )

            if result is False:
                self.logger.error("Rental creation failed in database")
                return jsonify({"error": "Rental creation failed"}), 500

            self.logger.info(
                f"Rental created: user_id {data['user_id']}, car_id {data['car_id']}"
            )
            return jsonify({"message": "Rental created successfully"}), 201

        except Exception as e:
            self.logger.error(f"Error creating rental: {e}")
            return jsonify({"error": "Rental creation failed"}), 500

    def put(self, rental_id):
        """Update rental data - only provided fields are updated, existing values are kept for missing fields."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Check if rental exists first and get existing data
            existing_rental = self.rental_repository.get_by_id(rental_id)
            if existing_rental is None:
                self.logger.warning(
                    f"Rental update attempt for non-existent rental: {rental_id}"
                )
                return jsonify({"error": "Rental not found"}), 404

            if existing_rental is False:
                return jsonify({"error": "Database error occurred"}), 500

            # Merge request data with existing rental data (request data takes priority)
            updated_data = {
                "user_id": data.get("user_id", existing_rental["user_id"]),
                "car_id": data.get("car_id", existing_rental["car_id"]),
                "state_id": data.get("state_id", existing_rental["state_id"]),
            }

            # Update rental using repository
            result = self.rental_repository.update_rental(
                _id=rental_id,
                user_id=updated_data["user_id"],
                car_id=updated_data["car_id"],
                state_id=updated_data["state_id"],
            )

            if result is False:
                self.logger.error(f"Rental update failed for {rental_id}")
                return jsonify({"error": "Rental update failed"}), 500

            self.logger.info(f"Rental updated: {rental_id}")
            return jsonify({"message": "Rental updated successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error updating rental: {e}")
            return jsonify({"error": "Rental update failed"}), 500

    def delete(self, rental_id):
        """Delete rental by ID."""
        try:
            success, error = self.rental_repository.delete_rental(rental_id)

            if not success:
                if error == "Rental not found":
                    self.logger.warning(
                        f"Delete attempt for non-existent rental: {rental_id}"
                    )
                    return jsonify({"error": error}), 404
                self.logger.error(f"Rental deletion failed for {rental_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Rental deleted: {rental_id}")
            return jsonify({"message": "Rental deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting rental: {e}")
            return jsonify({"error": "Rental deletion failed"}), 500
