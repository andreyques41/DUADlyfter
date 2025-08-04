from flask import jsonify
import logging
from json_handler import read_json, write_json

logger = logging.getLogger(__name__)

def get_new_id(tasks):
    # Generate unique ID by finding max existing ID and adding 1
    if not tasks:
        logger.info("No existing tasks found, starting with ID 1")
        return 1
    
    ids = [task.id for task in tasks]
    new_id = max(ids) + 1
    logger.info(f"Generated new task ID: {new_id}")
    return new_id

def tasks_to_json(tasks):
    # Convert list of Task objects to JSON response
    return jsonify([task.to_dict() for task in tasks])

def save_tasks(tasks, db_path):
    # Save list of Task objects to JSON file
    task_dicts = [task.to_dict() for task in tasks]
    write_json(task_dicts, db_path)

def load_tasks(db_path, task_class):
    # Load tasks from JSON file and return as Task objects
    try:
        raw_tasks = read_json(db_path)
        
        # Handle both single dict and list of dicts
        if isinstance(raw_tasks, dict):
            # Single task stored as dict, convert to list
            raw_tasks = [raw_tasks]
        elif isinstance(raw_tasks, list):
            # List of tasks, process directly
            pass
        else:
            logger.warning("Unexpected data type in JSON file, treating as empty")
            return []
        
        # Convert raw data to Task objects
        return [task_class.from_dict(task_data, task_data["id"]) for task_data in raw_tasks]
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        return []

def validate_task_data(request_body, required_fields=None):
    # Validate that request body contains all required task fields
    if not request_body:
        return False, "Request body cannot be empty"
    
    # Default required fields for a complete task
    if required_fields is None:
        required_fields = ["title", "description", "state"]
    
    # Check for missing fields
    missing_fields = []
    for field in required_fields:
        if field not in request_body:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate state field specifically
    if "state" in request_body:
        from models import State
        valid_states = State.get_valid_values()
        provided_state = request_body["state"]
        
        if provided_state not in valid_states:
            logger.warning(f"Invalid state '{provided_state}' provided. Valid options: {valid_states}")
            return False, f"Invalid state '{provided_state}'. Valid options: {valid_states}"
    
    return True, "Valid"
