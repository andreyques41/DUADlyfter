"""
Quotation Controller - HTTP request/response handling for quotation endpoints
"""
from flask import request, jsonify, g
from app.quotations.schemas import (
    QuotationCreateSchema,
    QuotationUpdateSchema,
    QuotationResponseSchema,
    QuotationStatusUpdateSchema
)
from app.quotations.services import QuotationService
from app.quotations.repositories import QuotationRepository
from app.chefs.repositories import ChefRepository
from app.clients.repositories import ClientRepository
from app.menus.repositories import MenuRepository
from app.dishes.repositories import DishRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class QuotationController:
    """Controller for quotation operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get quotation service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        quotation_repo = QuotationRepository(db)
        chef_repo = ChefRepository(db)
        client_repo = ClientRepository(db)
        menu_repo = MenuRepository(db)
        dish_repo = DishRepository(db)
        return QuotationService(quotation_repo, chef_repo, client_repo, menu_repo, dish_repo)
    
    @validate_json(QuotationCreateSchema)
    def create_quotation(self, current_user):
        """
        Create a new quotation with items
        
        Request body:
            {
                "client_id": 1,  // Optional
                "menu_id": 2,  // Optional
                "event_date": "2025-12-15",  // Optional
                "number_of_people": 50,  // Optional
                "notes": "Special dietary requirements",
                "terms_and_conditions": "Payment terms...",
                "items": [
                    {
                        "dish_id": 1,  // Optional, can be custom item
                        "item_name": "Paella",
                        "description": "Traditional Spanish paella",
                        "quantity": 10,
                        "unit_price": 25.50
                    }
                ]
            }
        
        Returns:
            201: Quotation created successfully
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            quotation_data = request.validated_data
            
            quotation = service.create_quotation(current_user['id'], quotation_data)
            
            # Serialize response
            schema = QuotationResponseSchema()
            result = schema.dump(quotation)
            
            self.logger.info(f"Quotation created for user {current_user['id']}")
            return success_response(
                data=result,
                message="Quotation created successfully",
                status=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Quotation creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating quotation: {e}", exc_info=True)
            return error_response("Failed to create quotation", 500)
    
    def get_all_quotations(self, current_user):
        """
        Get all quotations for the current chef
        
        Query params:
            status: str (optional) - Filter by status (draft, sent, accepted, rejected, expired)
        
        Returns:
            200: List of quotations with items
            400: Chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            
            # Get status filter from query params
            status = request.args.get('status')
            
            quotations = service.get_all_quotations(current_user['id'], status=status)
            
            # Serialize response
            schema = QuotationResponseSchema(many=True)
            result = schema.dump(quotations)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} quotations"
            )
            
        except ValueError as e:
            self.logger.warning(f"Get quotations failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving quotations: {e}", exc_info=True)
            return error_response("Failed to retrieve quotations", 500)
    
    def get_quotation_by_id(self, quotation_id: int, current_user):
        """
        Get quotation by ID with items
        
        Args:
            quotation_id: Quotation ID from URL parameter
        
        Returns:
            200: Quotation data with items
            404: Quotation not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            quotation = service.get_quotation_by_id(quotation_id, current_user['id'])
            
            if not quotation:
                return error_response("Quotation not found or access denied", 404)
            
            # Serialize response
            schema = QuotationResponseSchema()
            result = schema.dump(quotation)
            
            return success_response(data=result)
            
        except ValueError as e:
            self.logger.warning(f"Get quotation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving quotation {quotation_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve quotation", 500)
    
    @validate_json(QuotationUpdateSchema)
    def update_quotation(self, quotation_id: int, current_user):
        """
        Update quotation (only draft status)
        
        Args:
            quotation_id: Quotation ID from URL parameter
        
        Request body (all fields optional):
            {
                "client_id": 2,
                "menu_id": 3,
                "event_date": "2025-12-20",
                "number_of_people": 75,
                "notes": "Updated notes",
                "items": [...]  // If provided, replaces all items
            }
        
        Returns:
            200: Quotation updated successfully
            400: Validation error or quotation not in draft status
            404: Quotation not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            quotation = service.update_quotation(quotation_id, current_user['id'], update_data)
            
            # Serialize response
            schema = QuotationResponseSchema()
            result = schema.dump(quotation)
            
            self.logger.info(f"Quotation {quotation_id} updated")
            return success_response(
                data=result,
                message="Quotation updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Quotation update failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error updating quotation {quotation_id}: {e}", exc_info=True)
            return error_response("Failed to update quotation", 500)
    
    @validate_json(QuotationStatusUpdateSchema)
    def update_quotation_status(self, quotation_id: int, current_user):
        """
        Update quotation status
        
        Args:
            quotation_id: Quotation ID from URL parameter
        
        Request body:
            {
                "status": "sent"  // draft, sent, accepted, rejected, expired
            }
        
        Returns:
            200: Status updated successfully
            400: Invalid status transition
            404: Quotation not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            data = request.validated_data
            status = data['status']
            
            quotation = service.update_quotation_status(quotation_id, current_user['id'], status)
            
            # Serialize response
            schema = QuotationResponseSchema()
            result = schema.dump(quotation)
            
            self.logger.info(f"Quotation {quotation_id} status updated to {status}")
            return success_response(
                data=result,
                message=f"Quotation status updated to '{status}'"
            )
            
        except ValueError as e:
            self.logger.warning(f"Status update failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error updating quotation status {quotation_id}: {e}", exc_info=True)
            return error_response("Failed to update quotation status", 500)
    
    def delete_quotation(self, quotation_id: int, current_user):
        """
        Delete quotation (only draft status)
        
        Args:
            quotation_id: Quotation ID from URL parameter
        
        Returns:
            200: Quotation deleted successfully
            400: Quotation not in draft status
            404: Quotation not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            service.delete_quotation(quotation_id, current_user['id'])
            
            self.logger.info(f"Quotation {quotation_id} deleted")
            return success_response(
                message="Quotation deleted successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Quotation deletion failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error deleting quotation {quotation_id}: {e}", exc_info=True)
            return error_response("Failed to delete quotation", 500)
