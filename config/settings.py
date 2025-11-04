"""
Security Configuration Module
Centralized configuration for JWT and database settings.
Loads configuration from .env file for security and flexibility.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
config_dir = Path(__file__).parent
env_path = config_dir / '.env'
load_dotenv(dotenv_path=env_path)

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-very-secure-secret-key-here')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Database Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'lyfter')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'lyfter_backend_project')

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_DB = int(os.getenv('REDIS_DB', 0))

def get_jwt_secret():
    """Get the JWT secret key from environment or default."""
    return JWT_SECRET_KEY

def get_jwt_algorithm():
    """Get the JWT algorithm."""
    return JWT_ALGORITHM

def get_jwt_expiration_hours():
    """Get the JWT token expiration time in hours."""
    return JWT_EXPIRATION_HOURS

def get_database_url():
    """
    Build database URL from environment variables.
    
    NOTE: Reads DB_NAME from os.environ at call time (not import time) 
    to support test database override.
    """
    db_name = os.getenv('DB_NAME', 'lyfter')
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{db_name}"

def get_database_config():
    """Get database configuration as a dictionary."""
    return {
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': DB_HOST,
        'port': DB_PORT,
        'database': DB_NAME,
        'schema': DB_SCHEMA
    }
