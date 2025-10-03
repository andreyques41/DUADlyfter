from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

def create_addresses(metadata_obj: MetaData):
    """Create locations and addresses tables."""
    locations_table = Table(
        "locations",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("city", String(100), nullable=False),
        Column("state", String(50), nullable=True),
        Column("country", String(50), nullable=False),
    )
    
    addresses_table = Table(
        "addresses",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("street", String(100), nullable=False),
        Column("postal_code", String(20), nullable=True),
        Column("location_id", ForeignKey("locations.id"), nullable=False),
        Column("user_id", ForeignKey("users.id"), nullable=False)
    )
    
    return locations_table, addresses_table
