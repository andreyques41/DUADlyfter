from flask import request, jsonify, g
import logging
from flask.views import MethodView
from app.products.product_repository import ProductRepository
from app.products.product_service import ProductService
from app.products.product_controller import ProductController
from app.auth.user_repository import UserRepository
from app.utilities.decorators import require_admin_with_repo
from datetime import date
import json

class ProductAPI(MethodView):
    """CRUD operations for products."""
    """
    Product routes module.
    Defines ProductAPI class for CRUD endpoints using Flask MethodView.
    Uses ProductService and ProductController for business and presentation logic separation.
    """
    
    def __init__(self, db_manager, cache_manager):
        """
        Initialize dependencies and product controller.
        :param db_manager: DBManager instance
        :param cache_manager: CacheManager instance
        """
        self.logger = logging.getLogger(__name__)
        self.product_repository = ProductRepository(db_manager)
        self.product_service = ProductService(self.product_repository, cache_manager, self.logger)
        self.controller = ProductController(self.product_service, self.logger)
    
    def get(self, product_id=None):
        """
        GET /products         -> List all products
        GET /products/<id>    -> Get product by id
        """
        if product_id is not None:
            return self.controller.get_by_id(product_id)
        return self.controller.get_all()

    @require_admin_with_repo('user_repository')
    def post(self):
        """
        POST /products        -> Create a new product (admin only)
        """
        return self.controller.post()

    @require_admin_with_repo('user_repository')
    def put(self, product_id):
        """
        PUT /products/<id>    -> Update product (admin only)
        """
        return self.controller.put(product_id)

    @require_admin_with_repo('user_repository')
    def delete(self, product_id):
        """
        DELETE /products/<id> -> Delete product (admin only)
        """
        return self.controller.delete(product_id)


