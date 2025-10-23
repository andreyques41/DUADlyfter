from app.utilities.base_model import Invoice, InvoiceItem, Product
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import logging


class InvoiceRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get_by_id(self, invoice_id):
        try:
            with self.db_manager.get_session() as session:
                invoice = session.query(Invoice).filter_by(id=invoice_id).first()
                if invoice:
                    return {
                        "id": invoice.id,
                        "user_id": invoice.user_id,
                        "username": invoice.user.username,
                        "invoice_date": str(invoice.invoice_date),
                        "total": invoice.total,
                        "items": [{ 
                            "product_id": item.product_id,
                            "product_name": item.product.name,
                            "quantity": item.quantity,
                            "unit_price": item.unit_price,
                            "subtotal": item.subtotal
                        } for item in invoice.items]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error getting invoice: {e}")
            return False
    
    def get_all(self):
        try:
            with self.db_manager.get_session() as session:
                invoices = session.query(Invoice).all()
                return [{
                    "id": inv.id,
                    "user_id": inv.user_id,
                    "username": inv.user.username,
                    "invoice_date": str(inv.invoice_date),
                    "total": inv.total
                } for inv in invoices]
        except Exception as e:
            self.logger.error(f"Error getting invoices: {e}")
            return False
    
    def get_by_user(self, user_id):
        try:
            with self.db_manager.get_session() as session:
                invoices = session.query(Invoice).filter_by(user_id=user_id).all()
                return [{
                    "id": inv.id,
                    "invoice_date": str(inv.invoice_date),
                    "total": inv.total
                } for inv in invoices]
        except Exception as e:
            self.logger.error(f"Error getting user invoices: {e}")
            return False
    
    def create_invoice(self, user_id, items_data):
        """
        Create invoice with items using PESSIMISTIC LOCKING to prevent race conditions.
        
        items_data: [{"product_id": 1, "quantity": 2}, ...]
        """
        session = self.db_manager.get_session()
        
        try:
            # Begin explicit transaction
            session.begin()
            
            # Calculate total
            total = 0
            invoice_items = []
            
            for item_data in items_data:
                # PESSIMISTIC LOCK: SELECT FOR UPDATE
                # This prevents other transactions from modifying this product until we commit
                # Similar to the SQL example's WHERE stock = v_stock_before pattern
                product = session.query(Product).filter_by(
                    id=item_data["product_id"]
                ).with_for_update().first()
                
                if not product:
                    session.rollback()
                    return False, f"Product {item_data['product_id']} not found"
                
                # Read current stock (already locked)
                stock_before = product.quantity
                
                if stock_before < item_data["quantity"]:
                    session.rollback()
                    return False, f"Insufficient stock for {product.name}. Available: {stock_before}, Requested: {item_data['quantity']}"
                
                subtotal = product.price * item_data["quantity"]
                total += subtotal
                
                invoice_items.append({
                    "product_id": product.id,
                    "quantity": item_data["quantity"],
                    "unit_price": product.price,
                    "subtotal": subtotal
                })
                
                # Update stock (guaranteed atomic because of lock)
                product.quantity = stock_before - item_data["quantity"]
            
            # Create invoice
            new_invoice = Invoice(user_id=user_id, invoice_date=date.today(), total=total)
            session.add(new_invoice)
            session.flush()  # Get invoice ID without committing
            
            # Create invoice items
            for item_data in invoice_items:
                invoice_item = InvoiceItem(
                    invoice_id=new_invoice.id,
                    **item_data
                )
                session.add(invoice_item)
            
            # COMMIT: All operations succeed or all fail (ACID)
            session.commit()
            print(f"✅ Invoice {new_invoice.id} created successfully with {len(invoice_items)} items")
            return new_invoice.id, None
            
        except IntegrityError as e:
            session.rollback()
            print(f"[ERROR] Database integrity error: {e}")
            return False, "Database integrity violation"
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error creating invoice: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def delete_invoice(self, invoice_id):
        try:
            with self.db_manager.get_session() as session:
                invoice = session.query(Invoice).filter_by(id=invoice_id).first()
                if not invoice:
                    return False, "Invoice not found"
                
                session.delete(invoice)
                session.commit()
                return True, None
        except Exception as e:
            print(f"[ERROR] Error deleting invoice: {e}")
            return False, str(e)
