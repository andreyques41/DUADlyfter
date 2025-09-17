class RentalRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _format_rental(self, rental_record):
        return {
            "id": rental_record[0],
            "user_id": rental_record[1],
            "car_id": rental_record[2],
            "created_date": rental_record[3],
            "state_id": rental_record[4],
        }

    def get_all(self):
        try:
            results = self.db_manager.execute_query("SELECT * FROM rentals;")
            formatted_results = [self._format_rental(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all rentals from the database: ", error)
            return False

    def get_by_id(self, rental_id):
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM rentals WHERE id = %s;", rental_id
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
