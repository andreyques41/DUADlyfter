"""
Quotation Service - Business logic for quotation management
"""
from typing import Optional, List
from app.quotations.repositories.quotation_repository import QuotationRepository
from app.quotations.models.quotation_model import Quotation
from app.chefs.repositories.chef_repository import ChefRepository
from app.clients.repositories.client_repository import ClientRepository
from app.menus.repositories.menu_repository import MenuRepository
from app.dishes.repositories.dish_repository import DishRepository
from config.logging import get_logger

logger = get_logger(__name__)


class QuotationService:
    """Service for quotation business logic"""
    
    def __init__(
        self,
        quotation_repository: QuotationRepository,
        chef_repository: ChefRepository,
        client_repository: ClientRepository,
        menu_repository: MenuRepository,
        dish_repository: DishRepository
    ):
        self.quotation_repository = quotation_repository
        self.chef_repository = chef_repository
        self.client_repository = client_repository
        self.menu_repository = menu_repository
        self.dish_repository = dish_repository
    
    def create_quotation(self, user_id: int, quotation_data: dict) -> Quotation:
        """
        Create a new quotation for a chef
        
        Args:
            user_id: User ID of the chef
            quotation_data: Dictionary with quotation information and items
            
        Returns:
            Created Quotation instance
            
        Raises:
            ValueError: If chef profile not found or validation fails
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to create quotation for user {user_id} without chef profile")
            raise ValueError("Chef profile not found. Please create your chef profile first.")
        
        # Validate client if provided
        if quotation_data.get('client_id'):
            client = self.client_repository.get_by_id(quotation_data['client_id'])
            if not client or client.chef_id != chef.id:
                raise ValueError("Client not found or does not belong to you")
        
        # Validate menu if provided
        if quotation_data.get('menu_id'):
            menu = self.menu_repository.get_by_id(quotation_data['menu_id'], include_dishes=False)
            if not menu or menu.chef_id != chef.id:
                raise ValueError("Menu not found or does not belong to you")
        
        # Extract items
        items_data = quotation_data.pop('items', [])
        if not items_data:
            raise ValueError("At least one item is required")
        
        # Validate dishes in items
        for item in items_data:
            if item.get('dish_id'):
                dish = self.dish_repository.get_by_id(item['dish_id'], include_ingredients=False)
                if not dish or dish.chef_id != chef.id:
                    raise ValueError(f"Dish {item['dish_id']} not found or does not belong to you")
                # Auto-fill item_name from dish if not provided
                if not item.get('item_name'):
                    item['item_name'] = dish.name
                if not item.get('unit_price'):
                    item['unit_price'] = dish.price
        
        # Add chef_id to quotation data
        quotation_data['chef_id'] = chef.id
        quotation_data['status'] = 'draft'
        
        quotation = self.quotation_repository.create(quotation_data, items_data)
        logger.info(f"Created quotation {quotation.quotation_number} for chef {chef.id}")
        return quotation
    
    def get_quotation_by_id(self, quotation_id: int, user_id: int) -> Optional[Quotation]:
        """
        Get quotation by ID (only if owned by the chef)
        
        Args:
            quotation_id: Quotation ID
            user_id: User ID of the chef
            
        Returns:
            Quotation instance or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get quotation
        quotation = self.quotation_repository.get_by_id(quotation_id)
        
        # Verify ownership
        if quotation and quotation.chef_id != chef.id:
            logger.warning(f"User {user_id} attempted to access quotation {quotation_id} owned by chef {quotation.chef_id}")
            return None
        
        return quotation
    
    def get_all_quotations(self, user_id: int, status: str = None) -> List[Quotation]:
        """
        Get all quotations for a chef
        
        Args:
            user_id: User ID of the chef
            status: Optional status filter
            
        Returns:
            List of Quotation instances with items
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.quotation_repository.get_by_chef_id(chef.id, status=status)
    
    def update_quotation(self, quotation_id: int, user_id: int, update_data: dict) -> Quotation:
        """
        Update quotation (only if owned by the chef and status is draft)
        
        Args:
            quotation_id: Quotation ID
            user_id: User ID of the chef
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Quotation instance
            
        Raises:
            ValueError: If quotation not found, not owned, or not in draft status
        """
        # Get quotation with ownership check
        quotation = self.get_quotation_by_id(quotation_id, user_id)
        if not quotation:
            raise ValueError("Quotation not found or access denied")
        
        # Only allow updates if quotation is in draft status
        if quotation.status != 'draft':
            raise ValueError(f"Cannot update quotation with status '{quotation.status}'. Only draft quotations can be updated.")
        
        # Get chef for validations
        chef = self.chef_repository.get_by_user_id(user_id)
        
        # Validate client if being updated
        if 'client_id' in update_data and update_data['client_id']:
            client = self.client_repository.get_by_id(update_data['client_id'])
            if not client or client.chef_id != chef.id:
                raise ValueError("Client not found or does not belong to you")
        
        # Validate menu if being updated
        if 'menu_id' in update_data and update_data['menu_id']:
            menu = self.menu_repository.get_by_id(update_data['menu_id'], include_dishes=False)
            if not menu or menu.chef_id != chef.id:
                raise ValueError("Menu not found or does not belong to you")
        
        # Extract items if provided
        items_data = update_data.pop('items', None)
        
        # Validate dishes in items
        if items_data:
            for item in items_data:
                if item.get('dish_id'):
                    dish = self.dish_repository.get_by_id(item['dish_id'], include_ingredients=False)
                    if not dish or dish.chef_id != chef.id:
                        raise ValueError(f"Dish {item['dish_id']} not found or does not belong to you")
                    # Auto-fill from dish
                    if not item.get('item_name'):
                        item['item_name'] = dish.name
                    if not item.get('unit_price'):
                        item['unit_price'] = dish.price
        
        # Filter allowed fields
        allowed_fields = ['client_id', 'menu_id', 'event_date', 'number_of_people', 'notes', 'terms_and_conditions']
        filtered_data = {
            k: v for k, v in update_data.items() 
            if k in allowed_fields
        }
        
        updated_quotation = self.quotation_repository.update(quotation, filtered_data, items_data)
        logger.info(f"Updated quotation {quotation_id}")
        return updated_quotation
    
    def update_quotation_status(self, quotation_id: int, user_id: int, status: str) -> Quotation:
        """
        Update quotation status
        
        Args:
            quotation_id: Quotation ID
            user_id: User ID of the chef
            status: New status
            
        Returns:
            Updated Quotation instance
            
        Raises:
            ValueError: If quotation not found or invalid status transition
        """
        # Get quotation with ownership check
        quotation = self.get_quotation_by_id(quotation_id, user_id)
        if not quotation:
            raise ValueError("Quotation not found or access denied")
        
        # Validate status transitions
        current_status = quotation.status
        valid_transitions = {
            'draft': ['sent', 'expired'],
            'sent': ['accepted', 'rejected', 'expired'],
            'accepted': ['expired'],
            'rejected': [],
            'expired': []
        }
        
        if status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Cannot transition from '{current_status}' to '{status}'")
        
        updated_quotation = self.quotation_repository.update_status(quotation, status)
        logger.info(f"Quotation {quotation_id} status updated to {status}")
        return updated_quotation
    
    def delete_quotation(self, quotation_id: int, user_id: int) -> None:
        """
        Delete quotation (only if owned by the chef and status is draft)
        
        Args:
            quotation_id: Quotation ID
            user_id: User ID of the chef
            
        Raises:
            ValueError: If quotation not found, not owned, or not in draft status
        """
        # Get quotation with ownership check
        quotation = self.get_quotation_by_id(quotation_id, user_id)
        if not quotation:
            raise ValueError("Quotation not found or access denied")
        
        # Only allow deletion if quotation is in draft status
        if quotation.status != 'draft':
            raise ValueError(f"Cannot delete quotation with status '{quotation.status}'. Only draft quotations can be deleted.")
        
        self.quotation_repository.delete(quotation)
        logger.info(f"Deleted quotation {quotation_id}")
