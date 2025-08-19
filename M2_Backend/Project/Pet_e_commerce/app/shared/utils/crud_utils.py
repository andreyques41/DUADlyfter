"""
Shared CRUD Utilities for Data Persistence and ID Generation

This module provides reusable CRUD operations that can be used across different 
services (auth, products, cart, orders, etc.) to avoid code duplication while 
keeping domain-specific logic separate.

Key Features:
- Flexible serialization/deserialization methods
- Automatic ID generation with collision prevention
- Comprehensive error handling and logging
- Support for different model types (User, Product, etc.)
- JSON file-based persistence (easily replaceable with database)

Architecture Pattern:
- Services use these utilities for data persistence
- Domain logic remains in service classes
- Models handle their own serialization methods
- Error handling bubbles up to service layer

Usage Examples:
    # Save multiple models
    save_models_to_json(users, 'users.json', 'to_dict_with_password')
    
    # Load all models
    users = load_models_from_json('users.json', User, 'from_dict_with_password')
    
    # Load single model
    user = load_single_model_by_field('users.json', User, 'id', 1, 'from_dict_with_password')
    
    # Find cart by user_id
    cart = load_single_model_by_field('carts.json', Cart, 'user_id', 456)
    
    # Generate next ID
    new_id = generate_next_id(existing_users)
"""
import logging
from config.logging_config import EXC_INFO_LOG_ERRORS
from app.shared.json_db.json_handler import read_json, write_json

logger = logging.getLogger(__name__)


def save_models_to_json(models, db_path, serialize_method='to_dict'):
    """Save list of model objects to JSON file.
    
    Args:
        models (list): List of model objects to save
        db_path (str): Path to the JSON file
        serialize_method (str): Method name to call on each model for serialization
        
    Raises:
        Exception: If serialization or file writing fails
    """
    try:
        logger.debug(f"Serialize method: {serialize_method}")

        # Use getattr to call the specified method
        model_dicts = [getattr(model, serialize_method)() for model in models]
        
        write_json(model_dicts, db_path)
        logger.debug(f"Successfully saved {len(models)} models to {db_path}")
        
    except Exception as e:
        logger.error(f"Error saving models to {db_path}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        raise


def load_models_from_json(db_path, model_class, deserialize_method='from_dict'):
    """Load model objects from JSON file.
    
    Args:
        db_path (str): Path to the JSON file
        model_class (class): Model class to instantiate
        deserialize_method (str): Class method name to call for deserialization
        
    Returns:
        list: List of model objects, empty list if file doesn't exist or error occurs
    """
    try:
        raw_data = read_json(db_path)
        
        logger.debug(f"Deserialize method: {deserialize_method}")

        # Use getattr to call the specified class method
        method = getattr(model_class, deserialize_method)
        models = [method(item_data) for item_data in raw_data]
        
        logger.debug(f"Successfully loaded {len(models)} models from {db_path}")
        return models
        
    except Exception as e:
        logger.error(f"Error loading models from {db_path}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        return []


def load_single_model_by_field(db_path, model_class, field_name, field_value, deserialize_method='from_dict'):
    """Load a single model object by any field from JSON file.
    
    Args:
        db_path (str): Path to the JSON file
        model_class (class): Model class to instantiate
        field_name (str): Name of the field to search by (e.g., 'id', 'user_id', 'email')
        field_value: Value to search for in the specified field
        deserialize_method (str): Class method name to call for deserialization
        
    Returns:
        object or None: Model object if found, None otherwise
        
    Examples:
        # Find user by ID (equivalent to old load_single_model_from_json)
        user = load_single_model_by_field('users.json', User, 'id', 123)
        
        # Find cart by user_id
        cart = load_single_model_by_field('carts.json', Cart, 'user_id', 456)
        
        # Find user by email
        user = load_single_model_by_field('users.json', User, 'email', 'john@example.com')
    """
    try:
        logger.debug(f"Deserialize method: {deserialize_method}")

        raw_data = read_json(db_path)
        
        for item_data in raw_data:
            if item_data.get(field_name) == field_value:
                method = getattr(model_class, deserialize_method)
                return method(item_data)
        
        return None
        
    except Exception as e:
        logger.error(f"Error loading model by {field_name}={field_value} from {db_path}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        return None


def generate_next_id(existing_models):
    """Generate the next available ID based on existing models.
    
    Args:
        existing_models (list): List of model objects with 'id' attribute
        
    Returns:
        int: Next available ID (starts from 1)
    """
    try:
        if not existing_models:
            return 1
        return max(model.id for model in existing_models) + 1
    except Exception as e:
        logger.error(f"Error generating next ID: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        return 1
