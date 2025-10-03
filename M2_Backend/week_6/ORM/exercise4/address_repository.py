from sqlalchemy import select, update, delete, insert

class AddressRepository:
    def __init__(self, metadata_obj, schema="backend_week6"):
        """Initialize repository with metadata object"""
        self.metadata = metadata_obj
        
        # Get tables by name from metadata
        table_prefix = f"{schema}." if schema else ""
        self.addresses_table = metadata_obj.tables[f'{table_prefix}addresses']
        self.locations_table = metadata_obj.tables[f'{table_prefix}locations']
        self.users_table = metadata_obj.tables[f'{table_prefix}users']

    def create_address(self, connection, street, postal_code, location_id, user_id):
        """Create a new address"""
        try:
            stmt = (
                insert(self.addresses_table)
                .values(
                    street=street,
                    postal_code=postal_code,
                    location_id=location_id,
                    user_id=user_id
                )
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] New address for user ID {user_id} created successfully")
                return True
            else:
                print("[WARNING] Failed to create address")
                return False
        except Exception as error:
            print(f"[ERROR] Error creating address: {error}")
            return False
        
    def get_all(self, connection):
        """Get all addresses with location and user information"""
        try:
            stmt = (
                select(
                    self.addresses_table.c.id,
                    self.addresses_table.c.street,
                    self.addresses_table.c.postal_code,
                    self.locations_table.c.city,
                    self.locations_table.c.state,
                    self.locations_table.c.country,
                    self.users_table.c.full_name.label('user_name'),
                    self.users_table.c.username
                )
                .join(
                    self.locations_table,
                    self.addresses_table.c.location_id == self.locations_table.c.id
                )
                .join(
                    self.users_table,
                    self.addresses_table.c.user_id == self.users_table.c.id
                )
                .order_by(self.addresses_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting all addresses from database: {error}")
            return []

    def get_by_id(self, connection, address_id):
        """Get a specific address by ID with location and user information"""
        try:
            stmt = (
                select(
                    self.addresses_table.c.id,
                    self.addresses_table.c.street,
                    self.addresses_table.c.postal_code,
                    self.locations_table.c.city,
                    self.locations_table.c.state,
                    self.locations_table.c.country,
                    self.users_table.c.full_name.label('user_name'),
                    self.users_table.c.username
                )
                .join(
                    self.locations_table,
                    self.addresses_table.c.location_id == self.locations_table.c.id
                )
                .join(
                    self.users_table,
                    self.addresses_table.c.user_id == self.users_table.c.id
                )
                .where(self.addresses_table.c.id == address_id)
            )
            return connection.execute(stmt).fetchone()
        
        except Exception as error:
            print(f"[ERROR] Error getting address ID {address_id} from database: {error}")
            return None

    def get_by_user_id(self, connection, user_id):
        """Get all addresses for a specific user"""
        try:
            stmt = (
                select(
                    self.addresses_table.c.id,
                    self.addresses_table.c.street,
                    self.addresses_table.c.postal_code,
                    self.locations_table.c.city,
                    self.locations_table.c.state,
                    self.locations_table.c.country
                )
                .join(
                    self.locations_table,
                    self.addresses_table.c.location_id == self.locations_table.c.id
                )
                .where(self.addresses_table.c.user_id == user_id)
                .order_by(self.addresses_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting addresses for user ID {user_id}: {error}")
            return []

    def update_address(self, connection, address_id, **kwargs):
        """Update address information"""
        try:
            stmt = (
                update(self.addresses_table)
                .where(self.addresses_table.c.id == address_id)
                .values(**kwargs)
            )
            result = connection.execute(stmt)
            
            if result.rowcount > 0:
                print(f"[INFO] Address ID {address_id} updated successfully")
                return True
            else:
                print(f"[WARNING] Address ID {address_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error updating address ID {address_id}: {error}")
            return False

    def get_addresses_containing_substring(self, connection, substring):
        """Get all addresses that contain a specific substring in the street name"""
        try:
            stmt = (
                select(
                    self.addresses_table.c.id,
                    self.addresses_table.c.street,
                    self.addresses_table.c.postal_code,
                    self.locations_table.c.city,
                    self.locations_table.c.state,
                    self.locations_table.c.country,
                    self.users_table.c.full_name.label('user_name'),
                    self.users_table.c.username
                )
                .join(
                    self.locations_table,
                    self.addresses_table.c.location_id == self.locations_table.c.id
                )
                .join(
                    self.users_table,
                    self.addresses_table.c.user_id == self.users_table.c.id
                )
                .where(self.addresses_table.c.street.ilike(f'%{substring}%'))
                .order_by(self.addresses_table.c.id)
            )
            return connection.execute(stmt).fetchall()
        
        except Exception as error:
            print(f"[ERROR] Error getting addresses containing '{substring}': {error}")
            return []

    def delete_address(self, connection, address_id):
        """Delete an address by ID"""
        try:
            stmt = (
                delete(self.addresses_table)
                .where(self.addresses_table.c.id == address_id)
            )
            result = connection.execute(stmt)

            if result.rowcount > 0:
                print(f"[INFO] Address ID {address_id} deleted successfully")
                return True
            else:
                print(f"[WARNING] Address ID {address_id} not found")
                return False
        except Exception as error:
            print(f"[ERROR] Error deleting address ID {address_id}: {error}")
            return False