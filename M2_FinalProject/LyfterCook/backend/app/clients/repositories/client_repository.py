"""
Client Repository - Data access layer for Client model
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.clients.models.client_model import Client
from config.logging import get_logger

logger = get_logger(__name__)


class ClientRepository:
    """Repository for Client database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, client_data: dict) -> Client:
        """
        Create a new client
        
        Args:
            client_data: Dictionary with client information
            
        Returns:
            Created Client instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            client = Client(**client_data)
            self.db.add(client)
            self.db.flush()
            logger.info(f"Client created with ID: {client.id}")
            return client
        except SQLAlchemyError as e:
            logger.error(f"Error creating client: {e}", exc_info=True)
            raise
    
    def get_by_id(self, client_id: int) -> Optional[Client]:
        """
        Get client by ID
        
        Args:
            client_id: Client ID
            
        Returns:
            Client instance or None if not found
        """
        try:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if client:
                logger.debug(f"Retrieved client ID: {client_id}")
            return client
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving client by ID {client_id}: {e}", exc_info=True)
            raise
    
    def get_by_email(self, email: str) -> Optional[Client]:
        """
        Get client by email
        
        Args:
            email: Client email (case-insensitive)
            
        Returns:
            Client instance or None if not found
        """
        try:
            client = self.db.query(Client).filter(
                Client.email.ilike(email)  # Case-insensitive comparison
            ).first()
            return client
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving client by email {email}: {e}", exc_info=True)
            raise
    
    def get_by_chef_id(self, chef_id: int) -> List[Client]:
        """
        Get all clients for a specific chef
        
        Args:
            chef_id: Chef ID
            
        Returns:
            List of Client instances
        """
        try:
            clients = self.db.query(Client).filter(Client.chef_id == chef_id).all()
            logger.debug(f"Retrieved {len(clients)} clients for chef {chef_id}")
            return clients
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving clients for chef {chef_id}: {e}", exc_info=True)
            raise
    
    def update(self, client: Client, update_data: dict) -> Client:
        """
        Update client
        
        Args:
            client: Client instance to update
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Client instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            for key, value in update_data.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            
            self.db.flush()
            logger.info(f"Updated client ID: {client.id}")
            return client
        except SQLAlchemyError as e:
            logger.error(f"Error updating client ID {client.id}: {e}", exc_info=True)
            raise
    
    def delete(self, client: Client) -> None:
        """
        Delete client
        
        Args:
            client: Client instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(client)
            self.db.flush()
            logger.info(f"Deleted client ID: {client.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting client ID {client.id}: {e}", exc_info=True)
            raise
