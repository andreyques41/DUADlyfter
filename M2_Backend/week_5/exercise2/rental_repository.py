from utilities.filter_utils import build_dynamic_where_clause

# Base query for all rental SELECT operations
RENTAL_BASE_QUERY = """
SET search_path TO lyfter_car_rental;
SELECT rentals.id, rentals.created_date, rentals.user_id, rentals.car_id, rentals.state_id,
       users.full_name AS user_full_name, users.email AS user_email, 
       account_status.name AS user_account_status,
       model.brand AS car_brand, model.name AS car_model_name, 
       cars.year AS car_year, car_state.state AS car_state,
       rent_state.state AS rental_state
FROM rentals
INNER JOIN users ON rentals.user_id = users.id
INNER JOIN account_status ON users.account_status_id = account_status.id
INNER JOIN cars ON rentals.car_id = cars.id
INNER JOIN model ON cars.model_id = model.id
INNER JOIN car_state ON cars.state_id = car_state.id
INNER JOIN rent_state ON rentals.state_id = rent_state.id
"""


class RentalRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _format_rental(self, rental_record):
        return {
            "id": rental_record[0],
            "created_date": rental_record[1],
            "user_id": rental_record[2],
            "car_id": rental_record[3],
            "state_id": rental_record[4],
            "user_full_name": rental_record[5],
            "user_email": rental_record[6],
            "user_account_status": rental_record[7],
            "car_brand": rental_record[8],
            "car_model_name": rental_record[9],
            "car_year": rental_record[10],
            "car_state": rental_record[11],
            "rental_state": rental_record[12],
        }

    def get_all(self):
        try:
            results = self.db_manager.execute_query(
                RENTAL_BASE_QUERY + "ORDER BY rentals.id ASC;"
            )
            formatted_results = [self._format_rental(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all rentals from the database: ", error)
            return False

    def get_by_id(self, rental_id):
        try:
            result = self.db_manager.execute_query(
                RENTAL_BASE_QUERY + "WHERE rentals.id = %s;",
                rental_id,
            )
            if result:
                return self._format_rental(result[0])
            return None
        except Exception as error:
            print("[ERROR] Error getting rental by id from the database: ", error)
            return False

    def insert_new_rental(self, user_id, car_id):
        try:
            self.db_manager.execute_query(
                """
                INSERT INTO rentals (user_id, car_id, state_id) VALUES
                (%s, %s, %s)
                """,
                user_id,
                car_id,
                1,  # state_id=1 for active
            )
        except Exception as error:
            print("[ERROR] Error inserting a rental into the database: ", error)
            return False

    def update_rental(self, _id, user_id, car_id, state_id):
        try:
            self.db_manager.execute_query(
                """
                UPDATE rentals SET (user_id, car_id, state_id) = (%s, %s, %s) WHERE id = %s
                """,
                user_id,
                car_id,
                state_id,
                _id,
            )
            print("[INFO] Rental updated successfully")
            return True
        except Exception as error:
            print("[ERROR] Error updating a rental from the database: ", error)
            return False

    def complete_rental(self, rental_id, car_repository):
        try:
            # Set rental to completed
            self.db_manager.execute_query(
                """
                UPDATE rentals SET state_id = 2 WHERE id = %s
                """,
                rental_id,
            )

            # Get car_id for this rental
            result = self.db_manager.execute_query(
                "SELECT car_id FROM rentals WHERE id = %s;", rental_id
            )
            if not result:
                print(f"[ERROR] Rental ID#{rental_id} not found")
                return False

            car_id = result[0][0]

            # Use CarRepository to set car to available
            car_repository.update_state(car_id, 1)

            print(
                f"[INFO] Rental ID#{rental_id} updated to completed, and Car ID#{car_id} updated to available"
            )
            return True

        except Exception as error:
            print("[ERROR] Error updating a rental from the database: ", error)
            return False

    def get_rentals(self, rental_id=None, request_args=None):
        """
        Get rentals based on different criteria:
        - If rental_id is provided, get specific rental by ID
        - If request_args is provided, filter rentals by those arguments
        - Otherwise, return all rentals
        """
        try:
            if rental_id is not None:
                return self.get_by_id(rental_id)

            if request_args:
                return self.get_by_filter(request_args)

            return self.get_all()

        except Exception as error:
            print("[ERROR] Error in get_rentals method: ", error)
            return False

    def get_by_filter(self, request_args):
        """Get rentals based on filter parameters from request arguments"""
        try:
            # Define allowed filter fields specific to rentals table
            allowed_filters = {
                "user_id": "rentals.user_id",
                "car_id": "rentals.car_id",
                "state_id": "rentals.state_id",
                "created_date": "rentals.created_date",
            }

            # Use utility function to build WHERE clause
            where_clause, query_params = build_dynamic_where_clause(
                request_args, allowed_filters
            )

            if where_clause is None:
                # No valid filters provided, return all rentals
                return self.get_all()

            # Construct the final query with INNER JOIN
            final_query = RENTAL_BASE_QUERY + where_clause + ";"

            result = self.db_manager.execute_query(final_query, *query_params)
            formatted_results = [self._format_rental(record) for record in result]
            return formatted_results

        except Exception as error:
            print("[ERROR] Error getting rentals by filter from the database: ", error)
            return False

    def delete_rental(self, rental_id):
        """Delete a rental by ID"""
        try:
            # First check if rental exists
            existing_rental = self.get_by_id(rental_id)
            if existing_rental is None:
                return False, "Rental not found"
            if existing_rental is False:
                return False, "Database error"

            # Delete the rental
            self.db_manager.execute_query(
                "DELETE FROM rentals WHERE id = %s",
                rental_id,
            )
            print(f"[INFO] Rental ID#{rental_id} deleted successfully")
            return True, None
        except Exception as error:
            print(f"[ERROR] Error deleting rental ID#{rental_id}: ", error)
            return False, "Delete operation failed"
