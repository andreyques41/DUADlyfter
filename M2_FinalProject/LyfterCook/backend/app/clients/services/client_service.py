"""
Client Service - Business logic for client management
"""
from typing import Optional, List
from app.clients.repositories.client_repository import ClientRepository
from app.clients.models.client_model import Client
from app.chefs.repositories.chef_repository import ChefRepository
from config.logging import get_logger

logger = get_logger(__name__)


class ClientService:
    """Service for client business logic"""
    
    def __init__(self, client_repository: ClientRepository, chef_repository: ChefRepository):
        self.client_repository = client_repository
        self.chef_repository = chef_repository
    
    def create_client(self, user_id: int, client_data: dict) -> Client:
        """
        Create a new client for a chef
        
        Args:
            user_id: User ID of the chef
            client_data: Dictionary with client information
            
        Returns:
            Created Client instance
            
        Raises:
            ValueError: If chef profile not found or email already exists
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to create client for user {user_id} without chef profile")
            raise ValueError("Chef profile not found. Please create your chef profile first.")
        
        # Check for duplicate email
        email = client_data.get('email', '').strip()
        if email:
            existing_client = self.client_repository.get_by_email(email)
            if existing_client:
                logger.warning(f"Attempted to create client with duplicate email: {email}")
                raise ValueError(f"A client with email '{email}' already exists.")
        
        # Add chef_id to client data
        client_data['chef_id'] = chef.id
        
        client = self.client_repository.create(client_data)
        logger.info(f"Created client {client.id} for chef {chef.id}")
        return client
    
    def get_client_by_id(self, client_id: int, user_id: int) -> Optional[Client]:
        """
        Get client by ID (only if owned by the chef)
        
        Args:
            client_id: Client ID
            user_id: User ID of the chef
            
        Returns:
            Client instance or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get client
        client = self.client_repository.get_by_id(client_id)
        
        # Verify ownership
        if client and client.chef_id != chef.id:
            logger.warning(f"User {user_id} attempted to access client {client_id} owned by chef {client.chef_id}")
            return None
        
        return client
    
    def get_all_clients(self, user_id: int) -> List[Client]:
        """
        Get all clients for a chef
        
        Args:
            user_id: User ID of the chef
            
        Returns:
            List of Client instances
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.client_repository.get_by_chef_id(chef.id)
    
    def update_client(self, client_id: int, user_id: int, update_data: dict) -> Client:
        """
        Update client (only if owned by the chef)
        
        Args:
            client_id: Client ID
            user_id: User ID of the chef
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Client instance
            
        Raises:
            ValueError: If client not found or not owned by chef
        """
        # Get client with ownership check
        client = self.get_client_by_id(client_id, user_id)
        if not client:
            raise ValueError("Client not found or access denied")
        
        # Filter out None values and fields that shouldn't be updated
        filtered_data = {
            k: v for k, v in update_data.items() 
            if v is not None and k in ['name', 'email', 'phone', 'company', 'notes']
        }
        
        updated_client = self.client_repository.update(client, filtered_data)
        logger.info(f"Updated client {client_id}")
        
        # Note: ClientService doesn't currently use caching, but adding invalidation for future compatibility
        # If caching is added later, ensure cache keys match the get methods
        
        return updated_client
    
    def delete_client(self, client_id: int, user_id: int) -> None:
        """
        Delete client (only if owned by the chef)
        
        Args:
            client_id: Client ID
            user_id: User ID of the chef
            
        Raises:
            ValueError: If client not found or not owned by chef
        """
        # Get client with ownership check
        client = self.get_client_by_id(client_id, user_id)
        if not client:
            raise ValueError("Client not found or access denied")
        
        self.client_repository.delete(client)
        logger.info(f"Deleted client {client_id}")
