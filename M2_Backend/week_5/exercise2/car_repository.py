from utilities.filter_utils import build_dynamic_where_clause

# Base query for all car SELECT operations
CAR_BASE_QUERY = """
SET search_path TO lyfter_car_rental;
SELECT cars.id, cars.year, cars.model_id, cars.state_id,
       model.brand, model.name AS model_name, car_state.state AS state_name
FROM cars 
INNER JOIN model ON cars.model_id = model.id
INNER JOIN car_state ON cars.state_id = car_state.id
"""


class CarRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _format_car(self, car_record):
        return {
            "id": car_record[0],
            "year": car_record[1],
            "model_id": car_record[2],
            "state_id": car_record[3],
            "brand": car_record[4],
            "model_name": car_record[5],
            "state_name": car_record[6],
        }

    def get_all(self):
        try:
            results = self.db_manager.execute_query(
                CAR_BASE_QUERY + "ORDER BY cars.id ASC;"
            )
            formatted_results = [self._format_car(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all cars from the database: ", error)
            return False

    def get_by_id(self, car_id):
        try:
            result = self.db_manager.execute_query(
                CAR_BASE_QUERY + "WHERE cars.id = %s;",
                car_id,
            )
            if result:
                return self._format_car(result[0])
            return None
        except Exception as error:
            print("[ERROR] Error getting car by id from the database: ", error)
            return False

    def insert_new_car(self, model_id, year, state_id):
        try:
            self.db_manager.execute_query(
                """
                INSERT INTO cars (model_id, year, state_id) VALUES
                (%s, %s, %s)
                """,
                model_id,
                year,
                state_id,
            )
        except Exception as error:
            print("[ERROR] Error inserting a car into the database: ", error)
            return False

    def update_car(self, _id, model_id, year, state_id):
        try:
            self.db_manager.execute_query(
                """
                UPDATE cars SET (model_id, year, state_id) = (%s, %s, %s) WHERE id = %s
                """,
                model_id,
                year,
                state_id,
                _id,
            )
            print("[INFO] Car updated successfully")
            return True
        except Exception as error:
            print("[ERROR] Error updating a car from the database: ", error)
            return False

    def update_state(self, car_id, state_id):
        try:
            self.db_manager.execute_query(
                """
                UPDATE cars SET state_id = %s WHERE id = %s
                """,
                state_id,
                car_id,
            )
            print(f"[INFO] Car ID#{car_id} state updated to {state_id}")
            return True
        except Exception as error:
            print(f"[ERROR] Error updating car state for Car ID#{car_id}: ", error)
            return False

    def disable_car(self, car_id):
        """Disable a car from rental by setting it to maintenance state (state_id = 2)"""
        try:
            self.db_manager.execute_query(
                """
                UPDATE cars SET state_id = 2 WHERE id = %s
                """,
                car_id,
            )
            print(f"[INFO] Car ID#{car_id} disabled from rental (set to maintenance)")
            return True
        except Exception as error:
            print(f"[ERROR] Error disabling car ID#{car_id}: ", error)
            return False

    def get_rented_cars(self):
        """Get all cars that are currently rented (state_id = 3)"""
        try:
            results = self.db_manager.execute_query(
                CAR_BASE_QUERY + "WHERE cars.state_id = 3 ORDER BY cars.id ASC;"
            )
            formatted_results = [self._format_car(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting rented cars from the database: ", error)
            return False

    def get_available_cars(self):
        """Get all cars that are available for rent (state_id = 1)"""
        try:
            results = self.db_manager.execute_query(
                CAR_BASE_QUERY + "WHERE cars.state_id = 1 ORDER BY cars.id ASC;"
            )
            formatted_results = [self._format_car(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting available cars from the database: ", error)
            return False

    def get_cars(self, car_id=None, request_args=None):
        """
        Get cars based on different criteria:
        - If car_id is provided, get specific car by ID
        - If request_args is provided, filter cars by those arguments
        - Otherwise, return all cars
        """
        try:
            if car_id is not None:
                return self.get_by_id(car_id)

            if request_args:
                return self.get_by_filter(request_args)

            return self.get_all()

        except Exception as error:
            print("[ERROR] Error in get_cars method: ", error)
            return False

    def get_by_filter(self, request_args):
        """Get cars based on filter parameters from request arguments"""
        try:
            # Define allowed filter fields specific to cars table
            allowed_filters = {
                "model_id": "cars.model_id",
                "year": "cars.year",
                "state_id": "cars.state_id",
            }

            # Use utility function to build WHERE clause
            where_clause, query_params = build_dynamic_where_clause(
                request_args, allowed_filters
            )

            if where_clause is None:
                # No valid filters provided, return all cars
                return self.get_all()

            # Construct the final query with INNER JOIN
            final_query = CAR_BASE_QUERY + where_clause + ";"

            result = self.db_manager.execute_query(final_query, *query_params)
            formatted_results = [self._format_car(record) for record in result]
            return formatted_results

        except Exception as error:
            print("[ERROR] Error getting cars by filter from the database: ", error)
            return False

    def delete_car(self, car_id):
        """Delete a car by ID"""
        try:
            # First check if car exists
            existing_car = self.get_by_id(car_id)
            if existing_car is None:
                return False, "Car not found"
            if existing_car is False:
                return False, "Database error"

            # Delete the car
            self.db_manager.execute_query(
                "DELETE FROM cars WHERE id = %s",
                car_id,
            )
            print(f"[INFO] Car ID#{car_id} deleted successfully")
            return True, None
        except Exception as error:
            print(f"[ERROR] Error deleting car ID#{car_id}: ", error)
            return False, "Delete operation failed"
