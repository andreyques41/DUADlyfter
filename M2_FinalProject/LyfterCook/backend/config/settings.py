"""
Application Configuration Module
Centralized configuration for the LyfterCook application.
Loads configuration from .env file for security and flexibility.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from config/.env
config_dir = Path(__file__).parent
env_path = config_dir / '.env'
load_dotenv(dotenv_path=env_path)




# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
JWT_REFRESH_EXPIRATION_DAYS = int(os.getenv('JWT_REFRESH_EXPIRATION_DAYS', 7))

# Database Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'lyftercook')

# Schemas organization (no need for env var, defined in models)
# auth: users, refresh_tokens
# core: chefs, clients, dishes, ingredients, menus, menu_dishes, quotations, quotation_items
# integrations: appointments, price_sources, scraped_prices

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_KEY_PREFIX = os.getenv('REDIS_KEY_PREFIX', f"lyftercook:{FLASK_ENV}")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')

# Default Admin User (for seeding)
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@lyftercook.com')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'Admin123!@#')  # CHANGE IN PRODUCTION!

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

# SendGrid Configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@lyftercook.com')
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'LyfterCook')

# Calendly Configuration
CALENDLY_API_KEY = os.getenv('CALENDLY_API_KEY', '')
CALENDLY_USER_URI = os.getenv('CALENDLY_USER_URI', '')

# Application URLs
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')


class Settings:
    """Settings class for easier imports"""
    # Flask
    FLASK_ENV = FLASK_ENV
    FLASK_DEBUG = FLASK_DEBUG
    SECRET_KEY = SECRET_KEY
    
    # JWT
    JWT_SECRET_KEY = JWT_SECRET_KEY
    JWT_ALGORITHM = JWT_ALGORITHM
    JWT_EXPIRATION_HOURS = JWT_EXPIRATION_HOURS
    JWT_REFRESH_EXPIRATION_DAYS = JWT_REFRESH_EXPIRATION_DAYS
    
    # Database
    DB_USER = DB_USER
    DB_PASSWORD = DB_PASSWORD
    DB_HOST = DB_HOST
    DB_PORT = DB_PORT
    DB_NAME = DB_NAME
    
    # Redis
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_PASSWORD = REDIS_PASSWORD
    REDIS_DB = REDIS_DB
    REDIS_KEY_PREFIX = REDIS_KEY_PREFIX
    
    # CORS
    ALLOWED_ORIGINS = ALLOWED_ORIGINS
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY = CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET
    
    # SendGrid
    SENDGRID_API_KEY = SENDGRID_API_KEY
    SENDGRID_FROM_EMAIL = SENDGRID_FROM_EMAIL
    SENDGRID_FROM_NAME = SENDGRID_FROM_NAME
    
    # Calendly
    CALENDLY_API_KEY = CALENDLY_API_KEY
    CALENDLY_USER_URI = CALENDLY_USER_URI
    
    # URLs
    FRONTEND_URL = FRONTEND_URL
    BACKEND_URL = BACKEND_URL
    
    @staticmethod
    def get_database_url():
        """
        Build database URL from environment variables.
        
        Returns:
            str: PostgreSQL connection URL
        """
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    @staticmethod
    def get_redis_url():
        """
        Build Redis URL from environment variables.
        
        Returns:
            str: Redis connection URL
        """
        if REDIS_PASSWORD:
            return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        return f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


# Global settings instance
settings = Settings()
