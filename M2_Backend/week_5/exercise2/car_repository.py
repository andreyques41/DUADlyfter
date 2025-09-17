class CarRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _format_car(self, car_record):
        return {
            "id": car_record[0],
            "brand": car_record[1],
            "model": car_record[2],
            "year": car_record[3],
            "state": car_record[4],
        }

    def get_all(self):
        try:
            results = self.db_manager.execute_query(
                """
                SET search_path TO lyfter_car_rental;
                SELECT cars.id, model.brand AS brand, model.name AS model, year, car_state.state 
                FROM cars 
                INNER JOIN model ON cars.model_id = model.id
                INNER JOIN car_state ON cars.state_id = car_state.id
                ORDER BY id ASC 
                """
            )
            formatted_results = [self._format_car(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all cars from the database: ", error)
            return False

    def get_by_id(self, car_id):
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM cars WHERE id = %s;", car_id
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
                """
                SET search_path TO lyfter_car_rental;
                SELECT cars.id, model.brand AS brand, model.name AS model, year, car_state.state 
                FROM cars 
                INNER JOIN model ON cars.model_id = model.id
                INNER JOIN car_state ON cars.state_id = car_state.id
                WHERE state_id = 3
                ORDER BY id ASC 
                """
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
                """
                SET search_path TO lyfter_car_rental;
                SELECT cars.id, model.brand AS brand, model.name AS model, year, car_state.state 
                FROM cars 
                INNER JOIN model ON cars.model_id = model.id
                INNER JOIN car_state ON cars.state_id = car_state.id
                WHERE state_id = 1
                ORDER BY id ASC 
                """
            )
            formatted_results = [self._format_car(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting available cars from the database: ", error)
            return False
