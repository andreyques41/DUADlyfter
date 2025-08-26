"""
Centralized logging configuration for the Pet E-commerce application.

LOG_LEVEL and EXC_INFO_LOG_ERRORS are global config variables for logging.

LOG_LEVEL controls the minimum severity of messages that will be logged (applies everywhere):
    logging.DEBUG    # Shows DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging.INFO     # Shows INFO, WARNING, ERROR, CRITICAL
    logging.WARNING  # Shows WARNING, ERROR, CRITICAL
    logging.ERROR    # Shows ERROR, CRITICAL
    logging.CRITICAL # Shows only CRITICAL

EXC_INFO_LOG_ERRORS controls whether stack traces are included in error logs across the app.
Set to True for debugging, False for production if you want to hide stack traces.

Security Considerations:
- In production, use LOG_LEVEL=logging.WARNING or higher to avoid logging sensitive debug information.
- Always store logs securely and restrict access to authorized personnel only.
- Never expose logs (especially with stack traces or DEBUG info) to end users.
- If using EXC_INFO_LOG_ERRORS=True, ensure logs are not accessible to the public, as stack traces may reveal sensitive implementation details.
"""

import logging

# === GLOBAL LOGGING CONFIGURATION VARIABLES ===
LOG_LEVEL = logging.DEBUG  # Change this to set the global log level
EXC_INFO_LOG_ERRORS = False  # Change this to control exc_info for error logs globally

import os
from datetime import datetime


def setup_logging(log_level=LOG_LEVEL, log_file=None):
    """
    Configure logging for the entire application.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional log file path. If None, logs only to console.
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Define log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        filename=log_file,
        filemode='a' if log_file else None,
        force=True  # This ensures we override any existing configuration
    )
    
    # Also log to console if we're logging to file
    if log_file:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        
        # Add console handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Default configuration - can be called once at app startup
def configure_app_logging(log_level=LOG_LEVEL, log_file=None, environment='development'):
    """
    Default logging configuration for the application.
    Industry standard: Use parameters instead of hardcoded values.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional log file path. If None, uses environment-based default
        environment: Environment name ('development', 'production', 'testing')
    """
    # Set default log file based on environment if not specified
    if log_file is None and environment == 'production':
        log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    setup_logging(log_level=log_level, log_file=log_file)
