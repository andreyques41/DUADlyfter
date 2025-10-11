import jwt
from datetime import datetime, timedelta
from config.security_config import get_jwt_secret, get_jwt_algorithm, get_jwt_expiration_hours
from flask import request

class JWT_Manager():
    def __init__(self):
        self.secret = get_jwt_secret()
        self.algorithm = get_jwt_algorithm()
        
    def generate_jwt_token(self, user):
        try:
            # Handle both object and dictionary formats
            if isinstance(user, dict):
                user_id = user.get('id')
                username = user.get('username')
                role_id = user.get('role_id')
                is_admin = user.get('is_admin', role_id == 1 if role_id else False)
            else:
                user_id = user.id
                username = user.username
                role_id = user.role_id if hasattr(user, 'role_id') else user.role.id
                is_admin = role_id == 1
            
            payload = {
                'user_id': user_id,
                'username': username,
                'role_id': role_id,
                'is_admin': is_admin,
                'exp': datetime.utcnow() + timedelta(hours=get_jwt_expiration_hours()),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            return token

        except Exception as e:
            print(f"[ERROR] Token generation error: {e}")
            return None
        
    def verify_jwt_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def decode_jwt_token(self, token):
        """Alias for verify_jwt_token for consistency."""
        return self.verify_jwt_token(token)
    
    def get_user_from_request(self):
        """Extract and verify user info from Authorization header in current request."""
        try:
            token = request.headers.get('Authorization')
            if not token:
                return None
            
            # Remove 'Bearer ' prefix if present
            token = token.replace("Bearer ", "")
            payload = self.verify_jwt_token(token)
            return payload
        except Exception as e:
            print(f"[ERROR] Token extraction error: {e}")
            return None
    
    def is_admin(self, user_repository, user_id):
        """Check if a user has admin role."""
        try:
            return user_repository.is_admin(user_id)
        except Exception as e:
            print(f"[ERROR] Admin check error: {e}")
            return False