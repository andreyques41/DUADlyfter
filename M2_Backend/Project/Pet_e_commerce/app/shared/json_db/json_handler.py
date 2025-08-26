import json
import logging
from config.logging_config import EXC_INFO_LOG_ERRORS

logger = logging.getLogger(__name__)

def read_json(path):
    # Read data from a JSON file and return it as a Python object
    try:
        with open(path, 'r', encoding='utf-8') as file:
            py_dict = json.load(file)
            return py_dict
    except FileNotFoundError:
        logger.error(f"The file at '{path}' was not found", exc_info=EXC_INFO_LOG_ERRORS)
        return []
    except json.JSONDecodeError:
        logger.error(f"The file at '{path}' contains invalid JSON", exc_info=EXC_INFO_LOG_ERRORS)
        return []

def write_json(data_list, path):
    # Write a Python list to a JSON file
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data_list, file, indent=4)
        logger.info(f"Successfully saved {len(data_list)} items to {path}")
    except (PermissionError, IOError) as e:
        logger.error(f"Failed to write to file {path}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        raise  # Re-raise to let caller handle the error
    except Exception as e:
        logger.error(f"Unexpected error writing to file {path}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        raise
