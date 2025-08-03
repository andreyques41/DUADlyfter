from flask import jsonify
import logging
from app.shared.utils.json_handler import read_json, write_json
from app.auth.models.user import User, UserRole

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for authentication and user management operations"""
    
    def __init__(self, db_path='./users.json'):
        self.db_path = db_path
        self.logger = logger

    def generate_new_id(self):
        """Generate a new unique user ID based on existing users."""
        try:
            users = self.get_all_users()
            if not users:
                return 1
            return max(user.id for user in users) + 1
        except:
            return 1

    def get_all_users(self):
        """Get all users from database"""
        return _get_user(self.db_path, User)

    def get_user_by_id(self, user_id):
        """Get a specific user by ID"""
        return _get_user(self.db_path, User, id=user_id)

    def get_user_by_username(self, username):
        """Get a user by username"""
        users = self.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None

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

    def create_user(self, validated_data, password_hash):
        """Create a new user with validated data and hashed password."""
        try:
            new_user = User(
                id=self.generate_new_id(),
                username=validated_data['username'],
                email=validated_data['email'],
                password_hash=password_hash,
                role=validated_data['role'],
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                phone=validated_data.get('phone')
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
            
            # Update password
            user.password_hash = new_password_hash
            
            # Save updated user
            all_users = self.get_all_users()
            for i, u in enumerate(all_users):
                if u.id == user_id:
                    all_users[i] = user
                    break
            _save_users(all_users, self.db_path)
            
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
            
            # Update user fields
            for key, value in validated_data.items():
                setattr(user, key, value)
            
            # Save updated user
            all_users = self.get_all_users()
            for i, u in enumerate(all_users):
                if u.id == user_id:
                    all_users[i] = user
                    break
            _save_users(all_users, self.db_path)
            
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

# Private helper methods for the AuthService class
def _save_users(users, db_path):
    """Save list of User objects to JSON file."""
    user_dicts = [user.to_dict() for user in users]
    write_json(user_dicts, db_path)

def _get_user(db_path, model, id=None):
    """Load user(s) from JSON file and return as User object(s)."""
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

