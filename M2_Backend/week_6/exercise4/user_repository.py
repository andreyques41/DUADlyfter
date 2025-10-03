from sqlalchemy import select, update, delete, insert, func

class UserRepository:
    def __init__(self, metadata_obj, schema="backend_week6"):
        """Initialize repository with metadata object"""
        self.metadata = metadata_obj
        
        # Get tables by name from metadata
        table_prefix = f"{schema}." if schema else ""
        self.users_table = metadata_obj.tables[f'{table_prefix}users']
        self.cars_table = metadata_obj.tables[f'{table_prefix}cars']

    def create_user(self, connection, full_name, email, username, phone=None, birthday=None):
        """Create a new user"""
        try:
            stmt = (
                insert(self.users_table)
                .values(
                    full_name=full_name,
                    email=email,
                    username=username,
                    phone=phone,
                    birthday=birthday
                )
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] New user {username} created successfully")
                return True
            else:
                print("[WARNING] Failed to create user")
                return False
        except Exception as error:
            print(f"[ERROR] Error creating user: {error}")
            return False
        
    def get_all(self, connection):
        """Get all users"""
        try:
            stmt = (
                select(
                    self.users_table.c.id,
                    self.users_table.c.full_name,
                    self.users_table.c.email,
                    self.users_table.c.username,
                    self.users_table.c.phone,
                    self.users_table.c.birthday
                )
                .order_by(self.users_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting all users from database: {error}")
            return []

    def get_by_id(self, connection, user_id):
        """Get a specific user by ID"""
        try:
            stmt = (
                select(
                    self.users_table.c.id,
                    self.users_table.c.full_name,
                    self.users_table.c.email,
                    self.users_table.c.username,
                    self.users_table.c.phone,
                    self.users_table.c.birthday
                )
                .where(self.users_table.c.id == user_id)
            )
            return connection.execute(stmt).fetchone()
        
        except Exception as error:
            print(f"[ERROR] Error getting user ID {user_id} from database: {error}")
            return None

    def get_by_username(self, connection, username):
        """Get a specific user by username"""
        try:
            stmt = (
                select(
                    self.users_table.c.id,
                    self.users_table.c.full_name,
                    self.users_table.c.email,
                    self.users_table.c.username,
                    self.users_table.c.phone,
                    self.users_table.c.birthday
                )
                .where(self.users_table.c.username == username)
            )
            return connection.execute(stmt).fetchone()
        
        except Exception as error:
            print(f"[ERROR] Error getting user '{username}' from database: {error}")
            return None

    def update_user(self, connection, user_id, **kwargs):
        """Update user information"""
        try:
            stmt = (
                update(self.users_table)
                .where(self.users_table.c.id == user_id)
                .values(**kwargs)
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] User ID {user_id} updated successfully")
                return True
            else:
                print(f"[WARNING] User ID {user_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error updating user ID {user_id}: {error}")
            return False

    def get_users_with_multiple_cars(self, connection):
        """Get all users that have more than 1 car associated"""
        try:
            stmt = (
                select(
                    self.users_table.c.id,
                    self.users_table.c.full_name,
                    self.users_table.c.email,
                    self.users_table.c.username,
                    func.count(self.cars_table.c.id).label('car_count')
                )
                .join(
                    self.cars_table,
                    self.users_table.c.id == self.cars_table.c.user_id
                )
                .group_by(
                    self.users_table.c.id,
                    self.users_table.c.full_name,
                    self.users_table.c.email,
                    self.users_table.c.username
                )
                .having(func.count(self.cars_table.c.id) > 1)
                .order_by(func.count(self.cars_table.c.id).desc())
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting users with multiple cars: {error}")
            return []

    def delete_user(self, connection, user_id):
        """Delete a user by ID"""
        try:
            stmt = (
                delete(self.users_table)
                .where(self.users_table.c.id == user_id)
            )
            result = connection.execute(stmt)

            if result.rowcount > 0:
                print(f"[INFO] User ID {user_id} deleted successfully")
                return True
            else:
                print(f"[WARNING] User ID {user_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error deleting user ID {user_id}: {error}")
            return False