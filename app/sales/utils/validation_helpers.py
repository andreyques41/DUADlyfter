"""
Shared validation utilities for sales module.

This module provides reusable validation functions for monetary integrity checks,
item total calculations, and field validation across order, invoice, and return services.
"""
from typing import List, Any


FLOAT_TOLERANCE = 0.01


def validate_total_integrity(
    stored_total: float,
    calculated_total: float,
    entity_name: str = "Total"
) -> List[str]:
    """
    Validate that stored total matches calculated total within tolerance.
    
    This is a critical security check to prevent financial discrepancies
    between stored totals and actual item sums.
    
    Args:
        stored_total: Total stored in database
        calculated_total: Calculated total from items
        entity_name: Name for error message (e.g., "Order", "Invoice")
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if stored_total is None:
        errors.append(f"{entity_name} total is missing")
        return errors
    
    difference = abs(stored_total - calculated_total)
    if difference > FLOAT_TOLERANCE:
        errors.append(
            f"{entity_name} integrity mismatch: stored={stored_total:.2f}, "
            f"calculated={calculated_total:.2f}, difference={difference:.2f}"
        )
    
    return errors


def calculate_items_total(items: List[Any], amount_field: str = 'amount') -> float:
    """
    Calculate total from list of items.
    
    Args:
        items: List of item objects (OrderItem, ReturnItem, etc.)
        amount_field: Name of field containing amount (default: 'amount')
        
    Returns:
        Sum of all item amounts
    """
    if not items:
        return 0.0
    
    return sum(getattr(item, amount_field, 0) for item in items)


def validate_required_field(obj: Any, field_name: str, errors: List[str]) -> bool:
    """
    Validate that a field exists and is not None.
    
    Args:
        obj: Object to validate
        field_name: Name of field to check
        errors: List to append error message to
        
    Returns:
        True if field is valid, False otherwise
    """
    if not hasattr(obj, field_name) or getattr(obj, field_name) is None:
        errors.append(f"{field_name} is required")
        return False
    return True


def validate_non_negative(obj: Any, field_name: str, errors: List[str]) -> bool:
    """
    Validate that a numeric field is non-negative.
    
    Args:
        obj: Object to validate
        field_name: Name of field to check
        errors: List to append error message to
        
    Returns:
        True if field is valid, False otherwise
    """
    value = getattr(obj, field_name, None)
    if value is not None and value < 0:
        errors.append(f"{field_name} must be non-negative")
        return False
    return True


def validate_positive(obj: Any, field_name: str, errors: List[str]) -> bool:
    """
    Validate that a numeric field is positive (> 0).
    
    Args:
        obj: Object to validate
        field_name: Name of field to check
        errors: List to append error message to
        
    Returns:
        True if field is valid, False otherwise
    """
    value = getattr(obj, field_name, None)
    if value is not None and value <= 0:
        errors.append(f"{field_name} must be positive")
        return False
    return True
