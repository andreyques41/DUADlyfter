"""
Quotation Repository - Data access layer for Quotation and QuotationItem models
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from app.quotations.models.quotation_model import Quotation
from app.quotations.models.quotation_item_model import QuotationItem
from datetime import datetime
from decimal import Decimal
from config.logging import get_logger

logger = get_logger(__name__)


class QuotationRepository:
    """Repository for Quotation and QuotationItem database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_quotation_number(self, chef_id: int) -> str:
        """
        Generate unique quotation number
        Format: QT-{chef_id}-{year}{month}{day}-{sequence}
        """
        now = datetime.utcnow()
        date_str = now.strftime('%Y%m%d')
        prefix = f"QT-{chef_id}-{date_str}"
        
        # Count quotations with this prefix
        count = self.db.query(Quotation).filter(
            Quotation.quotation_number.like(f"{prefix}-%")
        ).count()
        
        sequence = count + 1
        return f"{prefix}-{sequence:03d}"
    
    def _calculate_totals(self, items_data: List[dict]) -> Decimal:
        """Calculate total price from items"""
        total = Decimal('0.00')
        for item in items_data:
            quantity = Decimal(str(item['quantity']))
            unit_price = Decimal(str(item['unit_price']))
            total += quantity * unit_price
        return total
    
    def create(self, quotation_data: dict, items_data: List[dict]) -> Quotation:
        """
        Create a new quotation with items
        
        Args:
            quotation_data: Dictionary with quotation information
            items_data: List of item dictionaries
            
        Returns:
            Created Quotation instance with items
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Generate quotation number
            quotation_number = self._generate_quotation_number(quotation_data['chef_id'])
            quotation_data['quotation_number'] = quotation_number
            
            # Calculate total
            total_price = self._calculate_totals(items_data)
            quotation_data['total_price'] = total_price
            
            # Create quotation
            quotation = Quotation(**quotation_data)
            self.db.add(quotation)
            self.db.flush()  # Get quotation ID
            
            # Add items
            for item_data in items_data:
                quantity = Decimal(str(item_data['quantity']))
                unit_price = Decimal(str(item_data['unit_price']))
                subtotal = quantity * unit_price
                
                item = QuotationItem(
                    quotation_id=quotation.id,
                    dish_id=item_data.get('dish_id'),
                    item_name=item_data['item_name'],
                    description=item_data.get('description'),
                    quantity=item_data['quantity'],
                    unit_price=unit_price,
                    subtotal=subtotal
                )
                self.db.add(item)
            
            self.db.flush()
            logger.info(f"Quotation created: {quotation_number} with {len(items_data)} items")
            return quotation
        except SQLAlchemyError as e:
            logger.error(f"Error creating quotation: {e}", exc_info=True)
            raise
    
    def get_by_id(self, quotation_id: int) -> Optional[Quotation]:
        """
        Get quotation by ID with items
        
        Args:
            quotation_id: Quotation ID
            
        Returns:
            Quotation instance or None if not found
        """
        try:
            quotation = self.db.query(Quotation).options(
                joinedload(Quotation.items)
            ).filter(Quotation.id == quotation_id).first()
            
            if quotation:
                logger.debug(f"Retrieved quotation ID: {quotation_id}")
            return quotation
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving quotation by ID {quotation_id}: {e}", exc_info=True)
            raise
    
    def get_by_chef_id(self, chef_id: int, status: str = None) -> List[Quotation]:
        """
        Get all quotations for a specific chef
        
        Args:
            chef_id: Chef ID
            status: Optional status filter
            
        Returns:
            List of Quotation instances with items
        """
        try:
            query = self.db.query(Quotation).options(
                joinedload(Quotation.items)
            ).filter(Quotation.chef_id == chef_id)
            
            if status:
                query = query.filter(Quotation.status == status)
            
            quotations = query.order_by(desc(Quotation.created_at)).all()
            logger.debug(f"Retrieved {len(quotations)} quotations for chef {chef_id}")
            return quotations
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving quotations for chef {chef_id}: {e}", exc_info=True)
            raise
    
    def update(self, quotation: Quotation, update_data: dict, items_data: List[dict] = None) -> Quotation:
        """
        Update quotation and optionally replace items
        
        Args:
            quotation: Quotation instance to update
            update_data: Dictionary with fields to update
            items_data: Optional list of new items (replaces existing)
            
        Returns:
            Updated Quotation instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            # Update basic fields
            for key, value in update_data.items():
                if hasattr(quotation, key) and key != 'total_price':
                    setattr(quotation, key, value)
            
            # Replace items if provided
            if items_data is not None:
                # Delete existing items
                self.db.query(QuotationItem).filter(
                    QuotationItem.quotation_id == quotation.id
                ).delete()
                
                # Add new items
                for item_data in items_data:
                    quantity = Decimal(str(item_data['quantity']))
                    unit_price = Decimal(str(item_data['unit_price']))
                    subtotal = quantity * unit_price
                    
                    item = QuotationItem(
                        quotation_id=quotation.id,
                        dish_id=item_data.get('dish_id'),
                        item_name=item_data['item_name'],
                        description=item_data.get('description'),
                        quantity=item_data['quantity'],
                        unit_price=unit_price,
                        subtotal=subtotal
                    )
                    self.db.add(item)
                
                # Recalculate total
                quotation.total_price = self._calculate_totals(items_data)
            
            self.db.flush()
            logger.info(f"Updated quotation ID: {quotation.id}")
            return quotation
        except SQLAlchemyError as e:
            logger.error(f"Error updating quotation ID {quotation.id}: {e}", exc_info=True)
            raise
    
    def update_status(self, quotation: Quotation, status: str) -> Quotation:
        """
        Update quotation status
        
        Args:
            quotation: Quotation instance
            status: New status
            
        Returns:
            Updated Quotation instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            quotation.status = status
            
            # Update timestamps based on status
            if status == 'sent' and not quotation.sent_at:
                quotation.sent_at = datetime.utcnow()
            elif status in ['accepted', 'rejected'] and not quotation.responded_at:
                quotation.responded_at = datetime.utcnow()
            
            self.db.flush()
            logger.info(f"Quotation {quotation.id} status updated to {status}")
            return quotation
        except SQLAlchemyError as e:
            logger.error(f"Error updating quotation status: {e}", exc_info=True)
            raise
    
    def delete(self, quotation: Quotation) -> None:
        """
        Delete quotation (items cascade delete automatically)
        
        Args:
            quotation: Quotation instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(quotation)
            self.db.flush()
            logger.info(f"Deleted quotation ID: {quotation.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting quotation ID {quotation.id}: {e}", exc_info=True)
            raise
