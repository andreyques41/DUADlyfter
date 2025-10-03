from sqlalchemy import select, update, delete, insert

class CarRepository:
    def __init__(self, metadata_obj, schema="backend_week6"):
        """Initialize repository with metadata object"""
        self.metadata = metadata_obj
        
        # Get tables by name from metadata
        table_prefix = f"{schema}." if schema else ""
        self.cars_table = metadata_obj.tables[f'{table_prefix}cars']
        self.brands_table = metadata_obj.tables[f'{table_prefix}brands']
        self.users_table = metadata_obj.tables[f'{table_prefix}users']

    def create_car(self, connection, brand_id, model, year=None, color=None, license_plate=None, user_id=None):
        """Create a new car"""
        try:
            stmt = (
                insert(self.cars_table)
                .values(
                    brand_id=brand_id,
                    model=model,
                    year=year,
                    color=color,
                    license_plate=license_plate,
                    user_id=user_id
                )
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] New car {model} created successfully")
                return True
            else:
                print("[WARNING] Failed to create car")
                return False
        except Exception as error:
            print(f"[ERROR] Error creating car: {error}")
            return False
        
    def get_all(self, connection):
        """Get all cars with brand information"""
        try:
            stmt = (
                select(
                    self.cars_table.c.id,
                    self.cars_table.c.model,
                    self.cars_table.c.year,
                    self.cars_table.c.color,
                    self.cars_table.c.license_plate,
                    self.cars_table.c.user_id,
                    self.brands_table.c.name.label('brand')
                    )
                .join(
                    self.brands_table,
                    self.cars_table.c.brand_id == self.brands_table.c.id
                )
                .order_by(self.cars_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting all cars from database: {error}")
            return []

    def get_by_id(self, connection, car_id):
        """Get a specific car by ID with brand information"""
        try:
            stmt = (
                select(
                    self.cars_table.c.id,
                    self.cars_table.c.model,
                    self.cars_table.c.year,
                    self.cars_table.c.color,
                    self.cars_table.c.license_plate,
                    self.cars_table.c.user_id,
                    self.brands_table.c.name.label('brand')
                    )
                .join(
                    self.brands_table,
                    self.cars_table.c.brand_id == self.brands_table.c.id
                )
                .where(self.cars_table.c.id == car_id)
            )
            return connection.execute(stmt).fetchone()
        
        except Exception as error:
            print(f"[ERROR] Error getting car ID {car_id} from database: {error}")
            return None

    def update_car(self, connection, car_id, **kwargs):
        """Update car information"""
        try:
            stmt = (
                update(self.cars_table)
                .where(self.cars_table.c.id == car_id)
                .values(**kwargs)
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] Car ID {car_id} updated successfully")
                return True
            else:
                print(f"[WARNING] Car ID {car_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error updating car ID {car_id}: {error}")
            return False

    def assign_user_to_car(self, connection, car_id, user_id):
        """Assign a user to a car (set ownership)"""
        try:
            # First check if the car exists
            car_check = self.get_by_id(connection, car_id)
            if not car_check:
                print(f"[WARNING] Car ID {car_id} not found")
                return False
            
            # Check if user exists
            user_check_stmt = select(self.users_table.c.id).where(self.users_table.c.id == user_id)
            user_exists = connection.execute(user_check_stmt).fetchone()
            
            if not user_exists:
                print(f"[WARNING] User ID {user_id} not found")
                return False
            
            # Update the car with the new user_id
            stmt = (
                update(self.cars_table)
                .where(self.cars_table.c.id == car_id)
                .values(user_id=user_id)
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] Car ID {car_id} successfully assigned to User ID {user_id}")
                return True
            else:
                print(f"[WARNING] Failed to assign car ID {car_id} to user")
                return False
                
        except Exception as error:
            print(f"[ERROR] Error assigning user to car: {error}")
            return False

    def get_cars_without_users(self, connection):
        """Get all cars that don't have an associated user"""
        try:
            stmt = (
                select(
                    self.cars_table.c.id,
                    self.cars_table.c.model,
                    self.cars_table.c.year,
                    self.cars_table.c.color,
                    self.cars_table.c.license_plate,
                    self.brands_table.c.name.label('brand')
                )
                .join(
                    self.brands_table,
                    self.cars_table.c.brand_id == self.brands_table.c.id
                )
                .where(self.cars_table.c.user_id.is_(None))
                .order_by(self.cars_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting cars without users: {error}")
            return []

    def delete_car(self, connection, car_id):
        """Delete a car by ID"""
        try:
            stmt = (
                delete(self.cars_table)
                .where(self.cars_table.c.id == car_id)
            )
            result = connection.execute(stmt)

            if result.rowcount > 0:
                print(f"[INFO] Car ID {car_id} deleted successfully")
                return True
            else:
                print(f"[WARNING] Car ID {car_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error deleting car ID {car_id}: {error}")
            return False
