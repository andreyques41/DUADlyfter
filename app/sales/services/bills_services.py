"""
Bills Service Module

This module provides comprehensive bills management functionality including:
- CRUD operations for bills (Create, Read, Update, Delete)
- Bill status management (paid, pending, overdue, refunded)
- Business logic for bill calculations and validation
- Data persistence and user-specific bill operations

Used by: Bills routes for API operations
Dependencies: Bills models, shared CRUD utilities
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from app.sales.models.bills import Bill, BillStatus
import logging
from app.shared.utils import read_json, write_json, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id

logger = logging.getLogger(__name__)

class BillsService:
    """
    Service class for bills management operations.
    
    Handles all business logic for bills CRUD operations, status management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./bills.json'):
        """Initialize bills service with database path."""
        self.db_path = db_path
        self.logger = logger

    # ============ BILLS RETRIEVAL METHODS ============

    def get_bills(self, bill_id=None, user_id=None):
        """
        Unified method to get all bills, specific bill by ID, or bills by user ID.
        
        Args:
            bill_id (int, optional): If provided, returns single bill by ID
            user_id (int, optional): If provided, returns bills for specific user
            
        Returns:
            list[Bill] or Bill or None: Bills collection, single bill, or None if not found
        """
        if bill_id:
            return load_single_model_by_field(self.db_path, Bill, 'id', bill_id)
        
        all_bills = load_models_from_json(self.db_path, Bill)
        
        if user_id:
            return [bill for bill in all_bills if bill.user_id == user_id]
            
        return all_bills

    # ============ BILLS CRUD OPERATIONS ============

    def create_bill(self, bill_instance: Bill) -> Tuple[Optional[Bill], Optional[str]]:
        """
        Create a new bill with Bill instance from schema.
        
        Args:
            bill_instance (Bill): Bill instance from schema with @post_load
            
        Returns:
            tuple: (Bill, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and sets creation timestamp
        """
        try:
            # Load existing bills to generate next ID
            existing_bills = load_models_from_json(self.db_path, Bill)

            # Check if bill already exists for this order
            existing_bill = self.get_bill_by_order_id(bill_instance.order_id)
            if existing_bill:
                return None, f"Bill already exists for order {bill_instance.order_id}"
            
            # Set the ID for the new bill instance
            bill_instance.id = generate_next_id(existing_bills)
            bill_instance.created_at = datetime.now()
            
            # Set due date if not provided (default 30 days)
            if not bill_instance.due_date:
                bill_instance.due_date = bill_instance.created_at + timedelta(days=30)
            
            # Save bill to database
            existing_bills.append(bill_instance)
            save_models_to_json(existing_bills, self.db_path)

            self.logger.info(f"Bill created successfully for order {bill_instance.order_id}")
            return bill_instance, None
            
        except Exception as e:
            error_msg = f"Error creating bill: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def update_bill(self, bill_id: int, bill_instance: Bill) -> Tuple[Optional[Bill], Optional[str]]:
        """
        Update an existing bill with Bill instance from schema.
        
        Args:
            bill_id (int): ID of the bill to update
            bill_instance (Bill): Updated bill instance from schema
            
        Returns:
            tuple: (Bill, None) on success, (None, error_message) on failure
            
        Note:
            Updates the entire bill with new instance data
        """
        try:
            existing_bill = self.get_bills(bill_id)
            if not existing_bill:
                return None, f"No bill found with ID {bill_id}"
            
            # Preserve original bill ID and creation time
            bill_instance.id = existing_bill.id
            bill_instance.created_at = existing_bill.created_at
            
            # Load all bills, replace the specific one, and save
            all_bills = load_models_from_json(self.db_path, Bill)
            for i, bill in enumerate(all_bills):
                if bill.id == bill_id:
                    all_bills[i] = bill_instance
                    break
            
            save_models_to_json(all_bills, self.db_path)
            
            self.logger.info(f"Bill updated: {bill_id}")
            return bill_instance, None
            
        except Exception as e:
            error_msg = f"Error updating bill: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def delete_bill(self, bill_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a bill by ID.
        
        Args:
            bill_id (int): ID of the bill to delete
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
            
        Note:
            Permanently removes bill from database
        """
        try:
            bill = self.get_bills(bill_id)
            if not bill:
                return False, f"No bill found with ID {bill_id}"
            
            # Remove bill from database
            all_bills = load_models_from_json(self.db_path, Bill)
            all_bills = [b for b in all_bills if b.id != bill_id]
            save_models_to_json(all_bills, self.db_path)
            
            self.logger.info(f"Bill deleted: {bill_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting bill: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    # ============ BILL STATUS MANAGEMENT METHODS ============

    def update_bill_status(self, bill_id: int, new_status: BillStatus) -> Tuple[Optional[Bill], Optional[str]]:
        """
        Update bill status.
        
        Args:
            bill_id (int): ID of the bill
            new_status (BillStatus): New status to set
            
        Returns:
            tuple: (Bill, None) on success, (None, error_message) on failure
        """
        try:
            bill = self.get_bills(bill_id)
            if not bill:
                return None, f"No bill found with ID {bill_id}"
            
            # Update status
            bill.status = new_status
            
            # Update bill in database
            all_bills = load_models_from_json(self.db_path, Bill)
            for i, b in enumerate(all_bills):
                if b.id == bill_id:
                    all_bills[i] = bill
                    break
            
            save_models_to_json(all_bills, self.db_path)
            
            self.logger.info(f"Bill {bill_id} status updated to {new_status.value}")
            return bill, None
            
        except Exception as e:
            self.logger.error(f"Error updating bill status for {bill_id}: {e}")
            return None, f"Failed to update bill status: {str(e)}"

    def get_bill_by_order_id(self, order_id: int) -> Optional[Bill]:
        """
        Get bill by order ID.
        
        Args:
            order_id (int): ID of the order
            
        Returns:
            Bill or None: Bill if found, None otherwise
        """
        return load_single_model_by_field(self.db_path, Bill, 'order_id', order_id)

    def get_overdue_bills(self) -> List[Bill]:
        """
        Get all overdue bills.
        
        Returns:
            list[Bill]: List of overdue bills
        """
        try:
            all_bills = load_models_from_json(self.db_path, Bill)
            current_date = datetime.now()
            
            overdue_bills = []
            for bill in all_bills:
                if (bill.due_date and bill.due_date < current_date and 
                    bill.status in [BillStatus.PENDING]):
                    overdue_bills.append(bill)
            
            return overdue_bills
            
        except Exception as e:
            self.logger.error(f"Error getting overdue bills: {e}")
            return []

    # ============ ACCESS CONTROL METHODS ============

    def check_user_access(self, current_user, is_admin, bill_id=None, user_id=None):
        """
        Check if current user can access the specified bill or user's bills
        
        Args:
            current_user: Current authenticated user object
            is_admin (bool): Whether current user is admin
            bill_id (int, optional): Bill ID to check access for
            user_id (int, optional): User ID to check access for
            
        Returns:
            bool: True if access allowed, False otherwise
        """
        # Admins can access any bill, regular users only their own
        if is_admin:
            return True
        
        if bill_id:
            # Check if bill belongs to current user
            bill = self.get_bills(bill_id)
            if bill:
                return current_user.id == bill.user_id
            return False
        
        if user_id:
            return current_user.id == user_id
            
        return False

    # ============ PRIVATE HELPER METHODS ============

    def validate_bill_data(self, bill: Bill) -> List[str]:
        """
        Validate bill against business rules.
        
        Args:
            bill (Bill): Bill to validate
            
        Returns:
            list[str]: List of validation error messages, empty if valid
        """
        errors = []
        
        # Check amount
        if bill.amount <= 0:
            errors.append("Bill amount must be greater than 0")
        
        # Check due date
        if bill.due_date and bill.created_at and bill.due_date <= bill.created_at:
            errors.append("Due date must be after creation date")
        
        return errors

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)