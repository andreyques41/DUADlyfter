from app.utilities.base_model import Product
from datetime import date
import logging


class ProductRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get_by_id(self, product_id):
        try:
            with self.db_manager.get_session() as session:
                product = session.query(Product).filter_by(id=product_id).first()
                if product:
                    return {
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "entry_date": str(product.entry_date),
                        "quantity": product.quantity
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error getting product: {e}")
            return False
    
    def get_all(self):
        try:
            with self.db_manager.get_session() as session:
                products = session.query(Product).all()
                return [{
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "entry_date": str(p.entry_date),
                    "quantity": p.quantity
                } for p in products]
        except Exception as e:
            self.logger.error(f"Error getting products: {e}")
            return False
    
    def create_product(self, name, price, quantity, entry_date=None):
        try:
            if not entry_date:
                entry_date = date.today()
            with self.db_manager.get_session() as session:
                new_product = Product(name=name, price=price, quantity=quantity, entry_date=entry_date)
                session.add(new_product)
                session.commit()
                return new_product.id
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return False
    
    def update_product(self, product_id, **kwargs):
        try:
            with self.db_manager.get_session() as session:
                product = session.query(Product).filter_by(id=product_id).first()
                if not product:
                    return None
                
                for key, value in kwargs.items():
                    if hasattr(product, key) and value is not None:
                        setattr(product, key, value)
                
                session.commit()
                return True
        except Exception as e:
            print(f"[ERROR] Error updating product: {e}")
            return False
    
    def delete_product(self, product_id):
        try:
            with self.db_manager.get_session() as session:
                product = session.query(Product).filter_by(id=product_id).first()
                if not product:
                    return False, "Product not found"
                
                session.delete(product)
                session.commit()
                return True, None
        except Exception as e:
            print(f"[ERROR] Error deleting product: {e}")
            return False, str(e)
