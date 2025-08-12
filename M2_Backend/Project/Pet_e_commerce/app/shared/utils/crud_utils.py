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
    user = load_single_model_from_json('users.json', User, 1, 'from_dict_with_password')
    
    # Generate next ID
    new_id = generate_next_id(existing_users)
"""
import logging
from .json_handler import read_json, write_json

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
        if serialize_method == 'to_dict':
            model_dicts = [model.to_dict() for model in models]
        elif serialize_method == 'to_dict_with_password':
            model_dicts = [model.to_dict_with_password() for model in models]
        else:
            # Use getattr to call the specified method
            model_dicts = [getattr(model, serialize_method)() for model in models]
        
        write_json(model_dicts, db_path)
        logger.debug(f"Successfully saved {len(models)} models to {db_path}")
        
    except Exception as e:
        logger.error(f"Error saving models to {db_path}: {e}")
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
        
        if deserialize_method == 'from_dict':
            models = [model_class.from_dict(item_data) for item_data in raw_data]
        elif deserialize_method == 'from_dict_with_password':
            models = [model_class.from_dict_with_password(item_data) for item_data in raw_data]
        else:
            # Use getattr to call the specified class method
            method = getattr(model_class, deserialize_method)
            models = [method(item_data) for item_data in raw_data]
        
        logger.debug(f"Successfully loaded {len(models)} models from {db_path}")
        return models
        
    except Exception as e:
        logger.error(f"Error loading models from {db_path}: {e}")
        return []


def load_single_model_from_json(db_path, model_class, model_id, deserialize_method='from_dict'):
    """Load a single model object by ID from JSON file.
    
    Args:
        db_path (str): Path to the JSON file
        model_class (class): Model class to instantiate
        model_id (int): ID of the model to load
        deserialize_method (str): Class method name to call for deserialization
        
    Returns:
        object or None: Model object if found, None otherwise
    """
    try:
        raw_data = read_json(db_path)
        
        for item_data in raw_data:
            if item_data.get('id') == model_id:
                if deserialize_method == 'from_dict':
                    return model_class.from_dict(item_data)
                elif deserialize_method == 'from_dict_with_password':
                    return model_class.from_dict_with_password(item_data)
                else:
                    method = getattr(model_class, deserialize_method)
                    return method(item_data)
        
        return None
        
    except Exception as e:
        logger.error(f"Error loading model {model_id} from {db_path}: {e}")
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
        logger.error(f"Error generating next ID: {e}")
        return 1
