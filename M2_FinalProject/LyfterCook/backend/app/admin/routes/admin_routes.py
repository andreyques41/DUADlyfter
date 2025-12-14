"""
Admin Routes
Endpoints administrativos con protección RBAC
"""
from flask import Blueprint
from app.core.middleware.auth_middleware import jwt_required, admin_required
from app.admin.controllers.admin_controller import admin_controller

# Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required
@admin_required
def dashboard():
    """Dashboard con estadísticas globales"""
    return admin_controller.dashboard()


@admin_bp.route('/chefs', methods=['GET'])
@jwt_required
@admin_required
def list_chefs():
    """Listar todos los chefs con filtros y paginación"""
    return admin_controller.list_chefs()


@admin_bp.route('/chefs/<int:chef_id>', methods=['GET'])
@jwt_required
@admin_required
def get_chef(chef_id):
    """Obtener detalles completos de un chef"""
    return admin_controller.get_chef(chef_id)


@admin_bp.route('/chefs/<int:chef_id>/status', methods=['PATCH'])
@jwt_required
@admin_required
def update_chef_status(chef_id):
    """Activar/desactivar un chef"""
    return admin_controller.update_chef_status(chef_id)


@admin_bp.route('/users', methods=['GET'])
@jwt_required
@admin_required
def list_users():
    """Listar todos los usuarios con filtros y paginación"""
    return admin_controller.list_users()


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_user(user_id):
    """Eliminar usuario (soft delete)"""
    return admin_controller.delete_user(user_id)


@admin_bp.route('/reports', methods=['GET'])
@jwt_required
@admin_required
def generate_report():
    """Generar reportes del sistema"""
    return admin_controller.generate_report()


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required
@admin_required
def get_audit_logs():
    """Consultar audit logs con filtros"""
    return admin_controller.get_audit_logs()


@admin_bp.route('/audit-logs/statistics', methods=['GET'])
@jwt_required
@admin_required
def get_audit_statistics():
    """Estadísticas de audit logs"""
    return admin_controller.get_audit_statistics()
