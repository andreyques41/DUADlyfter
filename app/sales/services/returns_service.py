"""
Returns Service Module

This module provides comprehensive returns management functionality including:
- CRUD operations for returns (Create, Read, Update, Delete)
- Return status management (requested, approved, rejected, processed)
- Business logic for return calculations and validation
- Data persistence and user-specific return operations

Used by: Returns routes for API operations
Dependencies: Returns models, shared CRUD utilities
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from app.sales.models.returns import Return, ReturnItem, ReturnStatus
import logging
from app.shared.utils import read_json, write_json, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id

logger = logging.getLogger(__name__)

class ReturnsService:
    """
    Service class for returns management operations.
    
    Handles all business logic for returns CRUD operations, status management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./returns.json'):
        """Initialize returns service with database path."""
        self.db_path = db_path
        self.logger = logger

    # ============ RETURNS RETRIEVAL METHODS ============

    def get_returns(self, return_id=None, user_id=None, order_id=None, bill_id=None):
        """
        Unified method to get all returns, specific return by ID, or returns by user/order/bill ID.
        
        Args:
            return_id (int, optional): If provided, returns single return by ID
            user_id (int, optional): If provided, returns returns for specific user
            order_id (int, optional): If provided, returns returns for specific order
            bill_id (int, optional): If provided, returns returns for specific bill
            
        Returns:
            list[Return] or Return or None: Returns collection, single return, or None if not found
        """
        if return_id:
            return load_single_model_by_field(self.db_path, Return, 'id', return_id)
        
        all_returns = load_models_from_json(self.db_path, Return)
        
        if user_id:
            return [ret for ret in all_returns if ret.user_id == user_id]
        
        if order_id:
            return [ret for ret in all_returns if ret.order_id == order_id]
        
        if bill_id:
            return [ret for ret in all_returns if ret.bill_id == bill_id]
            
        return all_returns

    # ============ RETURNS CRUD OPERATIONS ============

    def create_return(self, return_instance: Return) -> Tuple[Optional[Return], Optional[str]]:
        """
        Create a new return with Return instance from schema.
        
        Args:
            return_instance (Return): Return instance from schema with @post_load
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and calculates total refund amount
        """
        try:
            # Load existing returns to generate next ID
            existing_returns = load_models_from_json(self.db_path, Return)

            # Check if return already exists for this order/bill combination
            existing_return = self.get_return_by_order_and_bill(return_instance.order_id, return_instance.bill_id)
            if existing_return:
                return None, f"Return already exists for order {return_instance.order_id} and bill {return_instance.bill_id}"
            
            # Set the ID for the new return instance
            return_instance.id = generate_next_id(existing_returns)
            return_instance.created_at = datetime.now()
            
            # Calculate total refund from items
            return_instance.total_refund = sum(item.refund_amount for item in return_instance.items)
            
            # Validate return items
            validation_errors = self.validate_return_data(return_instance)
            if validation_errors:
                return None, "; ".join(validation_errors)
            
            # Save return to database
            existing_returns.append(return_instance)
            save_models_to_json(existing_returns, self.db_path)

            self.logger.info(f"Return created successfully for order {return_instance.order_id}")
            return return_instance, None
            
        except Exception as e:
            error_msg = f"Error creating return: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def update_return(self, return_id: int, return_instance: Return) -> Tuple[Optional[Return], Optional[str]]:
        """
        Update an existing return with Return instance from schema.
        
        Args:
            return_id (int): ID of the return to update
            return_instance (Return): Updated return instance from schema
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
            
        Note:
            Updates the entire return with new instance data
        """
        try:
            existing_return = self.get_returns(return_id)
            if not existing_return:
                return None, f"No return found with ID {return_id}"
            
            # Preserve original return ID and creation time
            return_instance.id = existing_return.id
            return_instance.created_at = existing_return.created_at
            
            # Recalculate total refund
            return_instance.total_refund = sum(item.refund_amount for item in return_instance.items)
            
            # Validate updated return
            validation_errors = self.validate_return_data(return_instance)
            if validation_errors:
                return None, "; ".join(validation_errors)
            
            # Load all returns, replace the specific one, and save
            all_returns = load_models_from_json(self.db_path, Return)
            for i, ret in enumerate(all_returns):
                if ret.id == return_id:
                    all_returns[i] = return_instance
                    break
            
            save_models_to_json(all_returns, self.db_path)
            
            self.logger.info(f"Return updated: {return_id}")
            return return_instance, None
            
        except Exception as e:
            error_msg = f"Error updating return: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def delete_return(self, return_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a return by ID (only if status allows).
        
        Args:
            return_id (int): ID of the return to delete
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
            
        Note:
            Can only delete returns with REQUESTED or REJECTED status
        """
        try:
            ret = self.get_returns(return_id)
            if not ret:
                return False, f"No return found with ID {return_id}"
            
            # Check if return can be deleted
            if ret.status not in [ReturnStatus.REQUESTED, ReturnStatus.REJECTED]:
                return False, f"Cannot delete return with status: {ret.status.value}"
            
            # Remove return from database
            all_returns = load_models_from_json(self.db_path, Return)
            all_returns = [r for r in all_returns if r.id != return_id]
            save_models_to_json(all_returns, self.db_path)
            
            self.logger.info(f"Return deleted: {return_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting return: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    # ============ RETURN STATUS MANAGEMENT METHODS ============

    def update_return_status(self, return_id: int, new_status: ReturnStatus) -> Tuple[Optional[Return], Optional[str]]:
        """
        Update return status with validation.
        
        Args:
            return_id (int): ID of the return
            new_status (ReturnStatus): New status to set
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
        """
        try:
            ret = self.get_returns(return_id)
            if not ret:
                return None, f"No return found with ID {return_id}"
            
            # Validate status transition
            if not self._is_valid_status_transition(ret.status, new_status):
                return None, f"Invalid status transition from {ret.status.value} to {new_status.value}"
            
            # Update status
            ret.status = new_status
            
            # Update return in database
            all_returns = load_models_from_json(self.db_path, Return)
            for i, r in enumerate(all_returns):
                if r.id == return_id:
                    all_returns[i] = ret
                    break
            
            save_models_to_json(all_returns, self.db_path)
            
            self.logger.info(f"Return {return_id} status updated to {new_status.value}")
            return ret, None
            
        except Exception as e:
            self.logger.error(f"Error updating return status for {return_id}: {e}")
            return None, f"Failed to update return status: {str(e)}"

    def approve_return(self, return_id: int) -> Tuple[Optional[Return], Optional[str]]:
        """
        Approve a return request.
        
        Args:
            return_id (int): ID of the return to approve
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
        """
        return self.update_return_status(return_id, ReturnStatus.APPROVED)

    def reject_return(self, return_id: int) -> Tuple[Optional[Return], Optional[str]]:
        """
        Reject a return request.
        
        Args:
            return_id (int): ID of the return to reject
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
        """
        return self.update_return_status(return_id, ReturnStatus.REJECTED)

    def process_return(self, return_id: int) -> Tuple[Optional[Return], Optional[str]]:
        """
        Mark return as processed (refund completed).
        
        Args:
            return_id (int): ID of the return to process
            
        Returns:
            tuple: (Return, None) on success, (None, error_message) on failure
        """
        return self.update_return_status(return_id, ReturnStatus.PROCESSED)

    def get_return_by_order_and_bill(self, order_id: int, bill_id: int) -> Optional[Return]:
        """
        Get return by order and bill ID combination.
        
        Args:
            order_id (int): ID of the order
            bill_id (int): ID of the bill
            
        Returns:
            Return or None: Return if found, None otherwise
        """
        try:
            all_returns = load_models_from_json(self.db_path, Return)
            for ret in all_returns:
                if ret.order_id == order_id and ret.bill_id == bill_id:
                    return ret
            return None
        except Exception as e:
            self.logger.error(f"Error getting return by order {order_id} and bill {bill_id}: {e}")
            return None

    def get_returns_by_status(self, status: ReturnStatus) -> List[Return]:
        """
        Get all returns with specific status.
        
        Args:
            status (ReturnStatus): Status to filter by
            
        Returns:
            list[Return]: List of returns with the specified status
        """
        try:
            all_returns = load_models_from_json(self.db_path, Return)
            return [ret for ret in all_returns if ret.status == status]
            
        except Exception as e:
            self.logger.error(f"Error getting returns by status {status.value}: {e}")
            return []

    def get_pending_returns(self) -> List[Return]:
        """
        Get all pending return requests (status = REQUESTED).
        
        Returns:
            list[Return]: List of pending returns
        """
        return self.get_returns_by_status(ReturnStatus.REQUESTED)

    # ============ ACCESS CONTROL METHODS ============

    def check_user_access(self, current_user, is_admin, return_id=None, user_id=None, order_id=None, bill_id=None):
        """
        Check if current user can access the specified return or user's returns
        
        Args:
            current_user: Current authenticated user object
            is_admin (bool): Whether current user is admin
            return_id (int, optional): Return ID to check access for
            user_id (int, optional): User ID to check access for
            order_id (int, optional): Order ID to check access for
            bill_id (int, optional): Bill ID to check access for
            
        Returns:
            bool: True if access allowed, False otherwise
        """
        # Admins can access any return, regular users only their own
        if is_admin:
            return True
        
        if return_id:
            # Check if return belongs to current user
            ret = self.get_returns(return_id)
            if ret:
                return current_user.id == ret.user_id
            return False
        
        if user_id:
            return current_user.id == user_id
        
        if order_id or bill_id:
            # For order/bill specific returns, need to check ownership indirectly
            # This would require checking order/bill ownership, simplified for now
            return True  # Could be enhanced with cross-service validation
            
        return False

    # ============ PRIVATE HELPER METHODS ============

    def _is_valid_status_transition(self, current_status: ReturnStatus, new_status: ReturnStatus) -> bool:
        """
        Validate if status transition is allowed.
        
        Args:
            current_status (ReturnStatus): Current return status
            new_status (ReturnStatus): Proposed new status
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            ReturnStatus.REQUESTED: [ReturnStatus.APPROVED, ReturnStatus.REJECTED],
            ReturnStatus.APPROVED: [ReturnStatus.PROCESSED],
            ReturnStatus.REJECTED: [],  # Final state
            ReturnStatus.PROCESSED: []  # Final state
        }
        
        return new_status in valid_transitions.get(current_status, [])

    def validate_return_data(self, ret: Return) -> List[str]:
        """
        Validate return against business rules.
        
        Args:
            ret (Return): Return to validate
            
        Returns:
            list[str]: List of validation error messages, empty if valid
        """
        errors = []
        
        # Check items
        if not ret.items:
            errors.append("Return must contain at least one item")
        
        # Check total refund
        if ret.total_refund <= 0:
            errors.append("Return total refund must be greater than 0")
        
        # Check individual items
        for item in ret.items:
            if item.quantity <= 0:
                errors.append(f"Return item {item.product_name} must have quantity greater than 0")
            if item.refund_amount < 0:
                errors.append(f"Return item {item.product_name} cannot have negative refund amount")
            if not item.reason.strip():
                errors.append(f"Return item {item.product_name} must have a reason")
        
        # Check return timeframe (example: 30 days from creation)
        if ret.created_at:
            days_since_creation = (datetime.now() - ret.created_at).days
            if days_since_creation > 30:
                errors.append("Returns can only be processed within 30 days of request")
        
        return errors

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)