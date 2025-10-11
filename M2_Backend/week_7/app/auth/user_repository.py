from app.utilities.base_model import User, Role
from sqlalchemy.exc import IntegrityError


class UserRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_by_id(self, user_id):
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    return {"id": user.id, "username": user.username, "role_id": user.role_id, "role_name": user.role.name}
                return None
        except Exception as e:
            print(f"[ERROR] Error getting user by id: {e}")
            return False
    
    def get_by_username(self, username):
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(username=username).first()
                if user:
                    return {"id": user.id, "username": user.username, "password": user.password, "role_id": user.role_id, "role_name": user.role.name}
                return None
        except Exception as e:
            print(f"[ERROR] Error getting user by username: {e}")
            return False
    
    def get_all(self):
        try:
            with self.db_manager.get_session() as session:
                users = session.query(User).all()
                return [{"id": u.id, "username": u.username, "role_id": u.role_id, "role_name": u.role.name} for u in users]
        except Exception as e:
            print(f"[ERROR] Error getting all users: {e}")
            return False
    
    def create_user(self, username, password, role_id=2):
        try:
            with self.db_manager.get_session() as session:
                new_user = User(username=username, password=password, role_id=role_id)
                session.add(new_user)
                session.commit()
                return new_user.id
        except IntegrityError:
            return None
        except Exception as e:
            print(f"[ERROR] Error creating user: {e}")
            return False
    
    def update_user(self, user_id, **kwargs):
        """Update user fields dynamically."""
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return None
                
                # Update only provided fields
                for key, value in kwargs.items():
                    if hasattr(user, key) and value is not None:
                        setattr(user, key, value)
                
                session.commit()
                return True
        except IntegrityError:
            # Username already exists
            return False
        except Exception as e:
            print(f"[ERROR] Error updating user: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete user by ID."""
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return False, "User not found"
                
                session.delete(user)
                session.commit()
                return True, None
        except Exception as e:
            print(f"[ERROR] Error deleting user: {e}")
            return False, str(e)
    
    def is_admin(self, user_id):
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                return user and user.role_id == 1
        except Exception:
            return False
