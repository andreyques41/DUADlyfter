from week_5.utilities.filter_utils import (
    build_dynamic_where_clause,
)

# Base query for all user SELECT operations
USER_BASE_QUERY = """
SET search_path TO lyfter_car_rental;
SELECT users.id, users.full_name, users.email, users.username, 
       users.password, users.birthday,
       account_status.name AS account_status_name
FROM users 
INNER JOIN account_status ON users.account_status_id = account_status.id
"""


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
            "account_status_name": user_record[6],
        }

    def get_users(self, user_id=None, request_args=None):
        """
        Get users based on different criteria:
        - If user_id is provided, get specific user by ID
        - If request_args is provided, filter users by those arguments
        - Otherwise, return all users
        """
        try:
            if user_id is not None:
                return self.get_by_id(user_id)

            if request_args:
                return self.get_by_filter(request_args)

            return self.get_all_users()

        except Exception as error:
            print("[ERROR] Error in get_users method: ", error)
            return False

    def get_by_id(self, user_id):
        try:
            result = self.db_manager.execute_query(
                USER_BASE_QUERY + "WHERE users.id = %s;",
                user_id,
            )
            if result:
                return self._format_user(result[0])
            return None
        except Exception as error:
            print("[ERROR] Error getting user by id from the database: ", error)
            return False

    def get_by_filter(self, request_args):
        """Get users based on filter parameters from request arguments"""
        try:
            # Define allowed filter fields specific to users table
            allowed_filters = {
                "full_name": "users.full_name",
                "email": "users.email",
                "username": "users.username",
                "account_status_id": "users.account_status_id",
                "birthday": "users.birthday",
            }

            # Use utility function to build WHERE clause
            where_clause, query_params = build_dynamic_where_clause(
                request_args, allowed_filters
            )

            if where_clause is None:
                # No valid filters provided, return all users
                return self.get_all_users()

            # Construct the final query with INNER JOIN
            final_query = USER_BASE_QUERY + where_clause + ";"

            result = self.db_manager.execute_query(final_query, *query_params)
            formatted_results = [self._format_user(record) for record in result]
            return formatted_results

        except Exception as error:
            print("[ERROR] Error getting users by filter from the database: ", error)
            return False

    def get_all_users(self):
        """Get all users without any filters"""
        try:
            result = self.db_manager.execute_query(
                USER_BASE_QUERY + "ORDER BY users.id ASC;"
            )
            formatted_results = [self._format_user(record) for record in result]
            return formatted_results
        except Exception as error:
            print("[ERROR] Error getting all users from the database: ", error)
            return False

    def insert_new_user(
        self, full_name, email, username, password, birthday, account_status_id
    ):
        try:
            self.db_manager.execute_query(
                """
                INSERT INTO users (full_name, email, username, password, birthday, account_status_id) VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                full_name,
                email,
                username,
                password,
                birthday,
                account_status_id,
            )

        except Exception as error:
            print("[ERROR] Error inserting a user into the database: ", error)
            return False

    def update_user(
        self, _id, full_name, email, username, password, birthday, account_status_id
    ):
        try:
            self.db_manager.execute_query(
                "UPDATE users SET (full_name, email, username, password, birthday, account_status_id) = (%s, %s, %s, %s, %s, %s) WHERE id = %s",
                full_name,
                email,
                username,
                password,
                birthday,
                account_status_id,
                _id,
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
                UPDATE users SET account_status_id = %s WHERE id = %s
                """,
                account_status_id,
                user_id,
            )
            print(f"[INFO] User ID#{user_id} status updated to {account_status_id}")
            return True
        except Exception as error:
            print(f"[ERROR] Error updating user status for User ID#{user_id}: ", error)
            return False

    def delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            # First check if user exists
            existing_user = self.get_by_id(user_id)
            if existing_user is None:
                return False, "User not found"
            if existing_user is False:
                return False, "Database error"

            # Delete the user
            self.db_manager.execute_query(
                "DELETE FROM users WHERE id = %s",
                user_id,
            )
            print(f"[INFO] User ID#{user_id} deleted successfully")
            return True, None
        except Exception as error:
            print(f"[ERROR] Error deleting user ID#{user_id}: ", error)
            return False, "Delete operation failed"
