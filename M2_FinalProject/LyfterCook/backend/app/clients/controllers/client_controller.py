"""
Client Controller - HTTP request/response handling for client endpoints
"""
from flask import request, jsonify, g
from app.clients.schemas import (
    ClientCreateSchema,
    ClientUpdateSchema,
    ClientResponseSchema
)
from app.clients.services import ClientService
from app.clients.repositories import ClientRepository
from app.chefs.repositories import ChefRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class ClientController:
    """Controller for client operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get client service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        client_repo = ClientRepository(db)
        chef_repo = ChefRepository(db)
        return ClientService(client_repo, chef_repo)
    
    @validate_json(ClientCreateSchema)
    def create_client(self, current_user):
        """
        Create a new client
        
        Request body:
            {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "company": "ABC Corp",
                "notes": "Prefers vegetarian options"
            }
        
        Returns:
            201: Client created successfully
            400: Validation error or chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            client_data = request.validated_data
            
            client = service.create_client(current_user['id'], client_data)
            
            # Serialize response
            schema = ClientResponseSchema()
            result = schema.dump(client)
            
            self.logger.info(f"Client created for user {current_user['id']}")
            return success_response(
                data=result,
                message="Client created successfully",
                status=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Client creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating client: {e}", exc_info=True)
            return error_response("Failed to create client", 500)
    
    def get_all_clients(self, current_user):
        """
        Get all clients for the current chef
        
        Returns:
            200: List of clients
            400: Chef profile not found
            500: Server error
        """
        try:
            service = self._get_service()
            clients = service.get_all_clients(current_user['id'])
            
            # Serialize response
            schema = ClientResponseSchema(many=True)
            result = schema.dump(clients)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} clients"
            )
            
        except ValueError as e:
            self.logger.warning(f"Get clients failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving clients: {e}", exc_info=True)
            return error_response("Failed to retrieve clients", 500)
    
    def get_client_by_id(self, client_id: int, current_user):
        """
        Get client by ID
        
        Args:
            client_id: Client ID from URL parameter
        
        Returns:
            200: Client data
            404: Client not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            client = service.get_client_by_id(client_id, current_user['id'])
            
            if not client:
                return error_response("Client not found or access denied", 404)
            
            # Serialize response
            schema = ClientResponseSchema()
            result = schema.dump(client)
            
            return success_response(data=result)
            
        except ValueError as e:
            self.logger.warning(f"Get client failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving client {client_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve client", 500)
    
    @validate_json(ClientUpdateSchema)
    def update_client(self, client_id: int, current_user):
        """
        Update client
        
        Args:
            client_id: Client ID from URL parameter
        
        Request body (all fields optional):
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+0987654321",
                "company": "XYZ Inc",
                "notes": "Updated notes"
            }
        
        Returns:
            200: Client updated successfully
            404: Client not found or access denied
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            client = service.update_client(client_id, current_user['id'], update_data)
            
            # Serialize response
            schema = ClientResponseSchema()
            result = schema.dump(client)
            
            self.logger.info(f"Client {client_id} updated")
            return success_response(
                data=result,
                message="Client updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Client update failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error updating client {client_id}: {e}", exc_info=True)
            return error_response("Failed to update client", 500)
    
    def delete_client(self, client_id: int, current_user):
        """
        Delete client
        
        Args:
            client_id: Client ID from URL parameter
        
        Returns:
            200: Client deleted successfully
            404: Client not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            service.delete_client(client_id, current_user['id'])
            
            self.logger.info(f"Client {client_id} deleted")
            return success_response(
                message="Client deleted successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Client deletion failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            self.logger.error(f"Error deleting client {client_id}: {e}", exc_info=True)
            return error_response("Failed to delete client", 500)
