from flask import jsonify
import logging
import jwt
from datetime import datetime, timedelta
from app.shared.utils import read_json, write_json
from app.auth.models import User, UserRole
from config.security_config import get_jwt_secret, get_jwt_algorithm, get_jwt_expiration_hours

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for authentication and user management operations"""
    
    def __init__(self, db_path='./users.json'):
        self.db_path = db_path
        self.logger = logger

    # ============ USER RETRIEVAL METHODS ============
    
    def get_users(self, user_id=None):
        """
        Unified method to get all users or a specific user by ID.
        
        Args:
            user_id (int, optional): If provided, returns single user. 
            If None, returns all users.
        
        Returns:
            list[User] or User or None: List of users, single user, or None if not found
        """
        return _get_user(self.db_path, User, id=user_id)

    def get_user_by_username(self, username):
        """Get a user by username"""
        users = self.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

    # ============ USER VALIDATION METHODS ============
    
    def check_username_exists(self, username):
        """Check if username already exists"""
        return self.get_user_by_username(username) is not None

    def check_email_exists(self, email):
        """Check if email already exists"""
        users = self.get_all_users()
        for user in users:
            if user.email == email:
                return True
        return False

    # ============ USER CRUD OPERATIONS ============
    
    def create_user(self, validated_data, password_hash):
        """Create a new user with validated data and hashed password."""
        try:
            new_user = User.from_dict(
                data=validated_data,
                id=self._generate_new_id(),
                password_hash=password_hash
            )
            
            # Save user to database
            all_users = self.get_all_users()
            all_users.append(new_user)
            _save_users(all_users, self.db_path)
            
            self.logger.info(f"User created successfully: {new_user.username}")
            return new_user, None
            
        except Exception as e:
            error_msg = f"Error creating user: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def update_user_password(self, user_id, new_password_hash):
        """Update user password"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None, "User not found"
            
            user.password_hash = new_password_hash
            self._update_single_user(user)
            
            self.logger.info(f"Password updated for user: {user.username}")
            return user, None
            
        except Exception as e:
            error_msg = f"Error updating password: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def update_user_profile(self, user_id, validated_data):
        """Update user profile (non-password fields)"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None, "User not found"
            
            # Update user fields directly from validated data
            for key, value in validated_data.items():
                if hasattr(user, key) and key != 'password_hash':
                    setattr(user, key, value)
            
            self._update_single_user(user)
            
            self.logger.info(f"Profile updated for user: {user.username}")
            return user, None
            
        except Exception as e:
            error_msg = f"Error updating profile: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def delete_user(self, user_id):
        """Delete a user account"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Remove user from database
            all_users = self.get_all_users()
            all_users = [u for u in all_users if u.id != user_id]
            _save_users(all_users, self.db_path)
            
            self.logger.info(f"User deleted: {user.username}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting user: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    # ============ JWT TOKEN MANAGEMENT ============
    
    def generate_jwt_token(self, user):
        """Generate JWT token for authenticated user"""
        try:
            payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role.value,
                'exp': datetime.utcnow() + timedelta(hours=get_jwt_expiration_hours()),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())
            self.logger.info(f"JWT token generated for user: {user.username}")
            return token

        except Exception as e:
            self.logger.error(f"Error generating JWT token: {e}")
            return None
        
    def verify_jwt_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid JWT token")
            return None

    # ============ PRIVATE INSTANCE METHODS ============
    
    def _generate_new_id(self):
        """Generate a new unique user ID based on existing users."""
        try:
            users = self.get_all_users()
            if not users:
                return 1
            return max(user.id for user in users) + 1
        except:
            return 1

    def _update_single_user(self, updated_user):
        """Efficiently update a single user in the database without loading all users"""
        try:
            raw_data = read_json(self.db_path)
            
            # Find and update the specific user in the raw data
            for i, user_data in enumerate(raw_data):
                if user_data.get('id') == updated_user.id:
                    raw_data[i] = updated_user.to_dict_with_password()
                    break
            
            # Save back to file
            write_json(raw_data, self.db_path)
            
        except Exception as e:
            self.logger.error(f"Error updating single user: {e}")
            raise


# ============ MODULE-LEVEL UTILITY FUNCTIONS ============

def _save_users(users, db_path):
    """Save list of User objects to JSON file.
    
    Reusable utility function for saving users that can be used by other services.
    Uses to_dict_with_password() for complete internal storage including password hashes.
    """
    user_dicts = [user.to_dict_with_password() for user in users]
    write_json(user_dicts, db_path)

def _get_user(db_path, model, id=None):
    """Load user(s) from JSON file and return as User object(s).
    
    Reusable utility function for loading users that can be used by other services.
    """
    try:
        raw_data = read_json(db_path)
        
        if id is None:
            return [model.from_dict_with_password(user_data) for user_data in raw_data]
        else:
            for user_data in raw_data:
                if user_data.get('id') == id:
                    return model.from_dict_with_password(user_data)
            return None
                
    except Exception as e:
        logger.error(f"Error loading user(s): {e}")
        return [] if id is None else None

