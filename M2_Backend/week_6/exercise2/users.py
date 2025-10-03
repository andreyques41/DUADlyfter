from sqlalchemy import Table, Column, Integer, String, MetaData, Date

def create_users(metadata_obj: MetaData):
    """Creates the users table - main entity for the system."""
    users_table = Table(
        "users",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("full_name", String(100), nullable=False),
        Column("email", String(100), nullable=False),
        Column("username", String(50), nullable=False),
        Column("phone", String(20), nullable=True),
        Column("birthday", Date, nullable=True)
    )
    return users_table
