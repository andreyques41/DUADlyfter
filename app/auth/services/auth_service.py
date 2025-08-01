from flask import jsonify
import logging
from app.shared.utils.json_handler import read_json, write_json

logger = logging.getLogger(__name__)

def users_to_json(users):
    # Convert list of User objects to JSON response
    return jsonify([user.to_dict() for user in users])

def save_users(users, db_path):
    # Save list of User objects to JSON file
    user_dicts = [user.to_dict() for user in users]
    write_json(user_dicts, db_path)

def get_user(db_path, model, id=None):
    # Load user(s) from JSON file and return as User object(s)
    try:
        raw_data = read_json(db_path)
        
        if id is None:
            # Return all users as a list
            return [model.from_dict(user_data) for user_data in raw_data]
        else:
            # Find and return specific user by id
            for user_data in raw_data:
                if user_data.get('id') == id:
                    return model.from_dict(user_data)
            return None  # User not found
                
    except Exception as e:
        logger.error(f"Error loading user(s): {e}")
        return [] if id is None else None

# def validate_task_data(request_body, required_fields=None):
#     # Validate that request body contains all required task fields
#     if not request_body:
#         return False, "Request body cannot be empty"
    
#     # Default required fields for a complete task
#     if required_fields is None:
#         required_fields = ["id", "title", "description", "state"]
    
#     # Check for missing fields
#     missing_fields = []
#     for field in required_fields:
#         if field not in request_body:
#             missing_fields.append(field)
    
#     if missing_fields:
#         return False, f"Missing required fields: {', '.join(missing_fields)}"
    
#     return True, "Valid"
#     missing_fields = []
#     for field in required_fields:
#         if field not in request_body:
#             missing_fields.append(field)
    
#     if missing_fields:
#         return False, f"Missing required fields: {', '.join(missing_fields)}"
    
#     return True, "Valid"
