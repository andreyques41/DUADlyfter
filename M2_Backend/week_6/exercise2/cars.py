from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

def create_cars(metadata_obj: MetaData):
    """Creates brands and cars tables with normalization."""
    
    # Brands table - reference data for car manufacturers
    brands_table = Table(
        "brands",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(50), nullable=False, unique=True),
        Column("country_origin", String(50), nullable=True)
    )
    
    # Cars table - individual vehicle records
    cars_table = Table(
        "cars",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("brand_id", ForeignKey("brands.id"), nullable=False),
        Column("model", String(50), nullable=False),
        Column("year", Integer, nullable=True),
        Column("color", String(30), nullable=True),
        Column("license_plate", String(20), nullable=False),
        Column("user_id", ForeignKey("users.id"), nullable=True)  # Optional owner
    )
    
    return brands_table, cars_table

