"""
Chef Controller - HTTP request/response handling for chef endpoints
"""
from flask import request, jsonify, g
from app.chefs.schemas import (
    ChefCreateSchema,
    ChefUpdateSchema,
    ChefResponseSchema,
    ChefPublicSchema
)
from app.chefs.services import ChefService
from app.chefs.repositories import ChefRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class ChefController:
    """Controller for chef profile operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get chef service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        chef_repo = ChefRepository(db)
        return ChefService(chef_repo)
    
    @validate_json(ChefCreateSchema)
    def create_profile(self, current_user):
        """
        Create chef profile for authenticated user
        
        Request body:
            {
                "bio": "Passionate chef...",
                "specialty": "Italian Cuisine",
                "phone": "+1234567890",
                "location": "New York, NY"
            }
        
        Returns:
            201: Profile created successfully
            400: Validation error or profile already exists
            500: Server error
        """
        try:
            service = self._get_service()
            profile_data = request.validated_data
            
            # Create profile for current user
            chef = service.create_profile(current_user['id'], profile_data)
            
            # Serialize response
            schema = ChefResponseSchema()
            result = schema.dump(chef)
            
            self.logger.info(f"Chef profile created for user {current_user['id']}")
            return success_response(
                data=result,
                message="Chef profile created successfully",
                status_code=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Profile creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating chef profile: {e}", exc_info=True)
            return error_response("Failed to create chef profile", 500)
    
    def get_my_profile(self, current_user):
        """
        Get current user's chef profile
        
        Returns:
            200: Profile data
            404: Profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            chef = service.get_profile_by_user_id(current_user['id'])
            
            if not chef:
                return error_response("Chef profile not found", 404)
            
            # Serialize response
            schema = ChefResponseSchema()
            result = schema.dump(chef)
            
            return success_response(data=result)
            
        except Exception as e:
            self.logger.error(f"Error retrieving chef profile: {e}", exc_info=True)
            return error_response("Failed to retrieve chef profile", 500)
    
    @validate_json(ChefUpdateSchema)
    def update_my_profile(self, current_user):
        """
        Update current user's chef profile
        
        Request body:
            {
                "bio": "Updated bio...",
                "specialty": "French Cuisine",
                "phone": "+0987654321",
                "location": "Paris, France",
                "is_active": true
            }
        
        Returns:
            200: Profile updated successfully
            404: Profile not found
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            # Update profile
            chef = service.update_profile(current_user['id'], update_data)
            
            # Serialize response
            schema = ChefResponseSchema()
            result = schema.dump(chef)
            
            self.logger.info(f"Chef profile updated for user {current_user['id']}")
            return success_response(
                data=result,
                message="Chef profile updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Profile update failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error updating chef profile: {e}", exc_info=True)
            return error_response("Failed to update chef profile", 500)
    
    def get_all_chefs(self):
        """
        Get all active chef profiles (public endpoint)
        
        Query params:
            include_inactive: bool (optional, default=false)
        
        Returns:
            200: List of chef profiles
            500: Server error
        """
        try:
            service = self._get_service()
            
            # Check if we should include inactive chefs
            include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
            active_only = not include_inactive
            
            chefs = service.get_all_profiles(active_only=active_only)
            
            # Serialize response (public schema)
            schema = ChefPublicSchema(many=True)
            result = schema.dump(chefs)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} chef profiles"
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving chefs: {e}", exc_info=True)
            return error_response("Failed to retrieve chef profiles", 500)
    
    def get_chef_by_id(self, chef_id: int):
        """
        Get chef profile by ID (public endpoint)
        
        Args:
            chef_id: Chef ID from URL parameter
        
        Returns:
            200: Chef profile data
            404: Chef not found
            500: Server error
        """
        try:
            service = self._get_service()
            chef = service.get_profile_by_id(chef_id)
            
            if not chef:
                return error_response("Chef profile not found", 404)
            
            # Only return active profiles for public view
            if not chef.is_active:
                return error_response("Chef profile not found", 404)
            
            # Serialize response (public schema)
            schema = ChefPublicSchema()
            result = schema.dump(chef)
            
            return success_response(data=result)
            
        except Exception as e:
            self.logger.error(f"Error retrieving chef {chef_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve chef profile", 500)
