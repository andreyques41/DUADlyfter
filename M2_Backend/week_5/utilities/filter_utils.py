def build_dynamic_where_clause(request_args, allowed_filters):
    """
    Build a dynamic WHERE clause for SQL queries based on request arguments.

    Args:
        request_args (dict): Dictionary containing filter parameters from request
        allowed_filters (dict): Dictionary mapping allowed filter keys to database column names
        Format: {"request_key": "db_column_name"}

    Returns:
        tuple: (where_clause, query_params) or (None, []) if no valid filters
    """
    # Define which fields should use case-insensitive partial matching
    text_fields = ["full_name", "email", "username", "name", "description", "title"]

    where_conditions = []
    query_params = []

    for key, value in request_args.items():
        if key in allowed_filters:
            db_column = allowed_filters[key]

            # Use ILIKE for case-insensitive partial matching on text fields
            if db_column in text_fields:
                where_conditions.append(f"{db_column} ILIKE %s")
                query_params.append(f"%{value}%")
            else:
                # Exact match for other fields (IDs, dates, numbers, etc.)
                where_conditions.append(f"{db_column} = %s")
                query_params.append(value)

    if not where_conditions:
        # No valid filters provided
        return None, []

    # Build the WHERE clause
    where_clause = " WHERE " + " AND ".join(where_conditions)
    return where_clause, query_params
