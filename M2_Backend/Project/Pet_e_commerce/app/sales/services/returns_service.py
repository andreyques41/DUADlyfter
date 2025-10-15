"""
Return Service Module

This module provides comprehensive return management functionality including:
- CRUD operations for returns (Create, Read, Update, Delete)
- Return status management and validation
- Business logic for return calculations and refund amounts
- Uses ReturnRepository for data access layer

Used by: Return routes for API operations
Dependencies: Return models, ReturnRepository
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.return_repository import ReturnRepository
from app.sales.models.returns import Return, ReturnItem, ReturnStatus

logger = logging.getLogger(__name__)

class ReturnService:
    """
    Service class for return management operations.
    
    Handles all business logic for return CRUD operations, status management,
    and data validation. Provides a clean interface for routes.
    """
    
    def __init__(self):
        """Initialize return service with ReturnRepository."""
        self.repository = ReturnRepository()
        self.logger = logger

    # ============ RETURN RETRIEVAL METHODS ============

    def get_return_by_id(self, return_id: int) -> Optional[Return]:
        """
        Retrieve return by ID.
        
        Args:
            return_id: Return ID to retrieve
            
        Returns:
            Return object or None if not found
        """
        return self.repository.get_by_id(return_id)

    def get_returns_by_order_id(self, order_id: int) -> List[Return]:
        """
        Retrieve all returns for a specific order.
        
        Args:
            order_id: Order ID to retrieve returns for
            
        Returns:
            List of Return objects
        """
        return self.repository.get_by_order_id(order_id)

    def get_returns_by_user_id(self, user_id: int) -> List[Return]:
        """
        Retrieve all returns for a specific user.
        
        Args:
            user_id: User ID to retrieve returns for
            
        Returns:
            List of Return objects
        """
        return self.repository.get_by_user_id(user_id)

    def get_all_returns(self) -> List[Return]:
        """
        Retrieve all returns.
        
        Returns:
            List of all Return objects
        """
        return self.repository.get_all()

    def get_returns_by_filters(self, **filters) -> List[Return]:
        """
        Retrieve returns by filters.
        
        Args:
            **filters: Filter criteria (status, start_date, end_date)
            
        Returns:
            List of filtered Return objects
        """
        return self.repository.get_by_filters(filters)

    # ============ RETURN CREATION ============

    def create_return(self, **return_data) -> Optional[Return]:
        """
        Create a new return with validation.
        
        Args:
            **return_data: Return fields (order_id, user_id, items, total_refund, etc.)
            
        Returns:
            Created Return object or None on error
        """
        try:
            # Validate required fields
            if not return_data.get('order_id'):
                self.logger.error("Cannot create return without order_id")
                return None
                
            if not return_data.get('user_id'):
                self.logger.error("Cannot create return without user_id")
                return None

            # Set defaults
            return_data.setdefault('created_at', datetime.utcnow())
            return_data.setdefault('status', ReturnStatus.REQUESTED)

            # Create Return instance
            return_obj = Return(**return_data)
            
            # Validate return data
            validation_errors = self.validate_return_data(return_obj)
            if validation_errors:
                self.logger.warning(f"Return validation failed: {'; '.join(validation_errors)}")
                return None
                
            # Save to database
            created_return = self.repository.create(return_obj)
            
            if created_return:
                self.logger.info(f"Return created successfully: {created_return.id}")
            else:
                self.logger.error("Failed to create return")
                
            return created_return
            
        except Exception as e:
            self.logger.error(f"Error creating return: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ RETURN UPDATE ============

    def update_return(self, return_id: int, **updates) -> Optional[Return]:
        """
        Update an existing return with new data.
        
        Args:
            return_id: Return ID to update
            **updates: Fields to update (items, status, total_refund, etc.)
            
        Returns:
            Updated Return object or None on error
        """
        try:
            existing_return = self.repository.get_by_id(return_id)
            if not existing_return:
                self.logger.warning(f"Attempt to update non-existent return {return_id}")
                return None
                
            # Update fields
            if 'items' in updates:
                existing_return.items = updates['items']
                # Recalculate total if items changed
                if updates['items']:
                    existing_return.total_refund = sum(
                        item.refund_amount for item in updates['items']
                    )
                    
            if 'status' in updates:
                existing_return.status = updates['status']
                
            if 'total_refund' in updates:
                existing_return.total_refund = updates['total_refund']

            # Validate updated return
            validation_errors = self.validate_return_data(existing_return)
            if validation_errors:
                self.logger.warning(f"Return validation failed: {'; '.join(validation_errors)}")
                return None
                
            # Save updated return
            updated_return = self.repository.update(existing_return)
            
            if updated_return:
                self.logger.info(f"Return updated successfully: {return_id}")
            else:
                self.logger.error(f"Failed to update return {return_id}")
                
            return updated_return
            
        except Exception as e:
            self.logger.error(f"Error updating return: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ RETURN DELETION ============

    def delete_return(self, return_id: int) -> bool:
        """
        Delete a return by ID (only if status allows).
        
        Args:
            return_id: ID of return to delete
            
        Returns:
            True on success, False on failure
            
        Note:
            Can only delete returns with REQUESTED or REJECTED status
        """
        try:
            return_obj = self.repository.get_by_id(return_id)
            if not return_obj:
                self.logger.warning(f"Attempt to delete non-existent return {return_id}")
                return False
                
            # Check if return can be deleted based on status
            # Only allow deletion of requested or rejected returns
            deletable_statuses = [ReturnStatus.REQUESTED, ReturnStatus.REJECTED]
            if return_obj.status not in deletable_statuses:
                self.logger.warning(
                    f"Cannot delete return {return_id} with status {return_obj.status.value}"
                )
                return False
                
            deleted = self.repository.delete(return_id)
            
            if deleted:
                self.logger.info(f"Return deleted successfully: {return_id}")
            else:
                self.logger.error(f"Failed to delete return {return_id}")
                
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting return: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False

    # ============ RETURN STATUS MANAGEMENT ============

    def update_return_status(self, return_id: int, new_status: ReturnStatus) -> Optional[Return]:
        """
        Update return status with validation.
        
        Args:
            return_id: Return ID to update
            new_status: New status to set
            
        Returns:
            Updated Return object or None on error
        """
        try:
            return_obj = self.repository.get_by_id(return_id)
            if not return_obj:
                self.logger.warning(f"Attempt to update status of non-existent return {return_id}")
                return None
                
            # Validate status transition
            if not self._is_valid_status_transition(return_obj.status, new_status):
                self.logger.warning(
                    f"Invalid status transition for return {return_id}: "
                    f"{return_obj.status.value} -> {new_status.value}"
                )
                return None
                
            # Update status
            return_obj.status = new_status
            updated_return = self.repository.update(return_obj)
            
            if updated_return:
                self.logger.info(f"Return {return_id} status updated to {new_status.value}")
            else:
                self.logger.error(f"Failed to update status for return {return_id}")
                
            return updated_return
            
        except Exception as e:
            self.logger.error(
                f"Error updating return status for {return_id}: {e}", 
                exc_info=EXC_INFO_LOG_ERRORS
            )
            return None

    def get_status_by_name(self, status_name: str) -> Optional[ReturnStatus]:
        """
        Get return status enum by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            ReturnStatus enum or None if not found
        """
        return self.repository.get_status_by_name(status_name)

    # ============ VALIDATION HELPERS ============

    def validate_return_data(self, return_obj: Return) -> List[str]:
        """
        Validate return data against business rules.
        
        Args:
            return_obj: Return object to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not hasattr(return_obj, 'order_id') or return_obj.order_id is None:
            errors.append("order_id is required")
            
        if not hasattr(return_obj, 'user_id') or return_obj.user_id is None:
            errors.append("user_id is required")
            
        if not hasattr(return_obj, 'status') or return_obj.status is None:
            errors.append("status is required")
            
        if not hasattr(return_obj, 'total_refund') or return_obj.total_refund is None:
            errors.append("total_refund is required")
        elif return_obj.total_refund < 0:
            errors.append("total_refund must be non-negative")
            
        # Validate items if present
        if hasattr(return_obj, 'items') and return_obj.items:
            if len(return_obj.items) == 0:
                errors.append("Return must have at least one item")
                
            for idx, item in enumerate(return_obj.items):
                if not hasattr(item, 'product_id') or item.product_id is None:
                    errors.append(f"Item {idx}: product_id is required")
                    
                if not hasattr(item, 'quantity') or item.quantity is None:
                    errors.append(f"Item {idx}: quantity is required")
                elif item.quantity <= 0:
                    errors.append(f"Item {idx}: quantity must be positive")
                    
                if not hasattr(item, 'reason') or not item.reason:
                    errors.append(f"Item {idx}: reason is required")
                    
                if not hasattr(item, 'refund_amount') or item.refund_amount is None:
                    errors.append(f"Item {idx}: refund_amount is required")
                elif item.refund_amount < 0:
                    errors.append(f"Item {idx}: refund_amount must be non-negative")
        
        # Validate return timeframe (example: 30 days from creation)
        if hasattr(return_obj, 'created_at') and return_obj.created_at:
            days_since_creation = (datetime.utcnow() - return_obj.created_at).days
            if days_since_creation > 30:
                errors.append("Returns can only be processed within 30 days of request")
                
        return errors

    # ============ ACCESS CONTROL METHODS ============

    def check_user_access(self, current_user, is_admin: bool, 
                         return_id: int = None, user_id: int = None) -> bool:
        """
        Check if current user can access the specified return or user's returns.
        
        Args:
            current_user: Current authenticated user object
            is_admin: Whether current user is admin
            return_id: Return ID to check access for (optional)
            user_id: User ID to check access for (optional)
            
        Returns:
            True if access allowed, False otherwise
        """
        # Admins can access any return
        if is_admin:
            return True
        
        # Check return-specific access
        if return_id:
            return_obj = self.repository.get_by_id(return_id)
            if return_obj:
                return current_user.id == return_obj.user_id
            return False
        
        # Check user-specific access
        if user_id:
            return current_user.id == user_id
            
        return False

    # ============ PRIVATE HELPER METHODS ============

    def _is_valid_status_transition(self, current_status: ReturnStatus, 
                                    new_status: ReturnStatus) -> bool:
        """
        Validate if status transition is allowed.
        
        Args:
            current_status: Current return status
            new_status: Proposed new status
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            ReturnStatus.REQUESTED: [ReturnStatus.APPROVED, ReturnStatus.REJECTED],
            ReturnStatus.APPROVED: [ReturnStatus.PROCESSED],
            ReturnStatus.REJECTED: [],  # Final state
            ReturnStatus.PROCESSED: []  # Final state
        }
        
        return new_status in valid_transitions.get(current_status, [])
