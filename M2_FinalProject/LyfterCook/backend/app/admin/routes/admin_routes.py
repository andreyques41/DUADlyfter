"""
Admin Routes
Endpoints administrativos con protección RBAC
"""
from flask import Blueprint, jsonify, request
from app.core.middleware.auth_middleware import jwt_required, admin_required
from app.admin.controllers.admin_controller import admin_controller
from app.core.cache_manager import get_cache

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


@admin_bp.route('/cache/stats', methods=['GET'])
@jwt_required
@admin_required
def get_cache_stats():
    """
    GET /admin/cache/stats
    Get Redis cache statistics
    Returns: cache enabled status, keys count, memory usage, hit rate
    """
    cache = get_cache()
    
    if not cache.enabled:
        return jsonify({
            'status': 'success',
            'data': {
                'enabled': False,
                'message': 'Cache is disabled or Redis not connected'
            }
        }), 200
    
    try:
        info = cache.redis_client.info()
        
        total_requests = info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)
        hit_rate = (info.get('keyspace_hits', 0) / total_requests) if total_requests > 0 else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'enabled': True,
                'keys_count': cache.redis_client.dbsize(),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'memory_peak': info.get('used_memory_peak_human', 'N/A'),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': round(hit_rate * 100, 2),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_days': info.get('uptime_in_days', 0)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get cache stats: {str(e)}'
        }), 500


@admin_bp.route('/cache/clear', methods=['DELETE'])
@jwt_required
@admin_required
def clear_cache():
    """
    DELETE /admin/cache/clear
    Clear Redis cache by pattern
    Query params: pattern (optional, default '*' = all)
    Examples:
      - /admin/cache/clear → Clear all cache
      - /admin/cache/clear?pattern=public:* → Clear all public caches
      - /admin/cache/clear?pattern=chefs:* → Clear all chef caches
    """
    cache = get_cache()
    
    if not cache.enabled:
        return jsonify({
            'status': 'error',
            'message': 'Cache is disabled or Redis not connected'
        }), 400
    
    pattern = request.args.get('pattern', '*')
    
    try:
        if pattern == '*':
            cache.flush_all()
            return jsonify({
                'status': 'success',
                'message': 'All cache cleared successfully'
            }), 200
        else:
            deleted = cache.delete_pattern(pattern)
            return jsonify({
                'status': 'success',
                'message': f'{deleted} cache keys deleted',
                'pattern': pattern,
                'deleted_count': deleted
            }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to clear cache: {str(e)}'
        }), 500
