class UserRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _format_user(self, user_record):
        return {
            "id": user_record[0],
            "full_name": user_record[1],
            "email": user_record[2],
            "username": user_record[3],
            "password": user_record[4],
            "birthday": user_record[5],
            "account_status_id": user_record[6],
        }

    def get_all(self):
        try:
            results = self.db_manager.execute_query(
                "SELECT * FROM lyfter_car_rental.users;"
            )
            formatted_results = [self._format_user(result) for result in results]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all users from the database: ", error)
            return False

    def get_by_id(self, user_id):
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM lyfter_car_rental.users WHERE id = %s;", user_id
            )
            if result:
                return self._format_user(result[0])
            return None
        except Exception as error:
            print("[ERROR] Error getting user by id from the database: ", error)
            return False

    def insert_new_user(
        self, full_name, email, username, password, birthday, account_status_id
    ):
        try:
            self.db_manager.execute_query(
                """
                INSERT INTO lyfter_car_rental.users (full_name, email, username, password, birthday, account_status_id) VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                (full_name, email, username, password, birthday, account_status_id),
            )

        except Exception as error:
            print("[ERROR] Error inserting a user into the database: ", error)
            return False

    def update_user(
        self, _id, full_name, email, username, password, birthday, account_status_id
    ):
        try:
            self.db_manager.execute_query(
                "UPDATE lyfter_car_rental.users SET (full_name, email, username, password, birthday, account_status_id) = (%s, %s, %s, %s, %s, %s) WHERE id = %s",
                (
                    full_name,
                    email,
                    username,
                    password,
                    birthday,
                    account_status_id,
                    _id,
                ),
            )
            print("[INFO] User updated successfully")
            return True
        except Exception as error:
            print("[ERROR] Error updating a user from the database: ", error)
            return False

    def update_user_status(self, user_id, account_status_id):
        """Update only the account status of a user"""
        try:
            self.db_manager.execute_query(
                """
                UPDATE lyfter_car_rental.users SET account_status_id = %s WHERE id = %s
                """,
                (account_status_id, user_id),
            )
            print(f"[INFO] User ID#{user_id} status updated to {account_status_id}")
            return True
        except Exception as error:
            print(f"[ERROR] Error updating user status for User ID#{user_id}: ", error)
            return False
