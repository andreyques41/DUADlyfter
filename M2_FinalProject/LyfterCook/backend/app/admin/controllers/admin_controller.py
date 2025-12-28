"""
Admin Controller
Handlers para endpoints administrativos
"""
from flask import jsonify, request, g
from app.admin.services.admin_service import AdminService
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.repositories.audit_log_repository import AuditLogRepository
from app.core.database import get_db


class AdminController:
    """Controller para operaciones administrativas"""
    
    def __init__(self):
        pass
    
    def _get_service(self):
        """
        Get admin service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        admin_repo = AdminRepository(db)
        audit_repo = AuditLogRepository(db)
        return AdminService(admin_repo, audit_repo)
    
    def dashboard(self):
        """
        GET /admin/dashboard
        Obtener estadísticas del dashboard
        """
        try:
            admin_id = g.user_id
            admin_service = self._get_service()
            stats = admin_service.get_dashboard(admin_id)
            
            return jsonify({
                'status': 'success',
                'data': stats
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def list_chefs(self):
        """
        GET /admin/chefs
        Listar todos los chefs con paginación y filtros
        """
        try:
            admin_id = g.user_id
            admin_service = self._get_service()
            
            # Query params
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status', 'all', type=str)
            search = request.args.get('search', None, type=str)
            sort = request.args.get('sort', 'created_at', type=str)
            order = request.args.get('order', 'desc', type=str)
            
            result = admin_service.get_all_chefs(
                admin_id=admin_id,
                page=page,
                per_page=per_page,
                status=status,
                search=search,
                sort=sort,
                order=order
            )
            
            return jsonify({
                'status': 'success',
                'data': result['chefs'],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages']
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def get_chef(self, chef_id: int):
        """
        GET /admin/chefs/:id
        Obtener detalles de un chef específico
        """
        try:
            admin_id = g.user_id
            admin_service = self._get_service()
            chef_details = admin_service.get_chef_details(admin_id, chef_id)
            
            if not chef_details:
                return jsonify({
                    'status': 'error',
                    'message': 'Chef no encontrado'
                }), 404
            
            return jsonify({
                'status': 'success',
                'data': chef_details
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def update_chef_status(self, chef_id: int):
        """
        PATCH /admin/chefs/:id/status
        Activar/desactivar un chef
        """
        try:
            admin_id = g.user_id
            admin_service = self._get_service()
            data = request.get_json()
            
            if not data or 'is_active' not in data:
                return jsonify({
                    'status': 'error',
                    'message': 'Campo is_active es requerido'
                }), 400
            
            is_active = data.get('is_active')
            reason = data.get('reason', None)
            
            success = admin_service.update_chef_status(
                admin_id=admin_id,
                chef_id=chef_id,
                is_active=is_active,
                reason=reason
            )
            
            if not success:
                return jsonify({
                    'status': 'error',
                    'message': 'Chef no encontrado'
                }), 404
            
            return jsonify({
                'status': 'success',
                'message': f'Chef {"activado" if is_active else "desactivado"} exitosamente'
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def list_users(self):
        """
        GET /admin/users
        Listar todos los usuarios con paginación y filtros
        """
        try:
            admin_id = g.user_id
            
            # Query params
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            role = request.args.get('role', 'all', type=str)
            status = request.args.get('status', 'all', type=str)
            search = request.args.get('search', None, type=str)
            
            admin_service = self._get_service()
            result = admin_service.get_all_users(
                admin_id=admin_id,
                page=page,
                per_page=per_page,
                role=role,
                status=status,
                search=search
            )
            
            return jsonify({
                'status': 'success',
                'data': result['users'],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages']
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def delete_user(self, user_id: int):
        """
        DELETE /admin/users/:id
        Eliminar usuario (soft delete)
        """
        try:
            admin_id = g.user_id
            data = request.get_json()
            
            # Validar campos requeridos
            if not data or not data.get('confirm'):
                return jsonify({
                    'status': 'error',
                    'message': 'Debes confirmar la eliminación con confirm=true'
                }), 400
            
            if 'reason' not in data or not data['reason']:
                return jsonify({
                    'status': 'error',
                    'message': 'Campo reason es requerido'
                }), 400
            
            if len(data['reason']) < 10:
                return jsonify({
                    'status': 'error',
                    'message': 'La razón debe tener al menos 10 caracteres'
                }), 400
            
            reason = data['reason']
            
            admin_service = self._get_service()
            success, error_msg = admin_service.delete_user(
                admin_id=admin_id,
                user_id=user_id,
                reason=reason
            )
            
            if not success:
                return jsonify({
                    'status': 'error',
                    'message': error_msg
                }), 403
            
            return jsonify({
                'status': 'success',
                'message': 'Usuario eliminado exitosamente'
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def generate_report(self):
        """
        GET /admin/reports
        Generar reportes del sistema
        """
        try:
            admin_id = g.user_id
            
            # Query params
            report_type = request.args.get('report_type', 'activity', type=str)
            start_date = request.args.get('start_date', None, type=str)
            end_date = request.args.get('end_date', None, type=str)
            format_type = request.args.get('format', 'json', type=str)
            
            # Validar report_type
            valid_types = ['activity', 'chefs', 'quotations']
            if report_type not in valid_types:
                return jsonify({
                    'status': 'error',
                    'message': f'Tipo de reporte inválido. Opciones: {", ".join(valid_types)}'
                }), 400
            
            admin_service = self._get_service()
            report_data = admin_service.generate_report(
                admin_id=admin_id,
                report_type=report_type,
                start_date=start_date,
                end_date=end_date
            )
            
            if not report_data:
                return jsonify({
                    'status': 'error',
                    'message': 'Error generando reporte'
                }), 500
            
            # Si solicitan CSV, convertir (básico)
            if format_type == 'csv':
                # Para simplificar, retornamos JSON con mensaje
                # En producción implementarías conversión real a CSV
                return jsonify({
                    'status': 'success',
                    'message': 'Formato CSV no implementado aún. Use format=json',
                    'data': report_data
                }), 200
            
            return jsonify({
                'status': 'success',
                'report_type': report_type,
                'data': report_data
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def get_audit_logs(self):
        """
        GET /admin/audit-logs
        Consultar audit logs con filtros
        """
        try:
            admin_id = g.user_id
            admin_service = self._get_service()
            audit_service = admin_service.audit_service
            
            # Query params
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            filter_admin_id = request.args.get('admin_id', None, type=int)
            action_type = request.args.get('action_type', None, type=str)
            start_date = request.args.get('start_date', None, type=str)
            end_date = request.args.get('end_date', None, type=str)
            
            result = audit_service.get_logs(
                page=page,
                per_page=per_page,
                admin_id=filter_admin_id,
                action_type=action_type,
                start_date=start_date,
                end_date=end_date
            )
            
            # Log esta acción
            admin_service.audit_service.log_action(
                admin_id=admin_id,
                action='view_audit_logs',
                metadata={
                    'filters': {
                        'admin_id': filter_admin_id,
                        'action_type': action_type,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                }
            )
            
            return jsonify({
                'status': 'success',
                'data': result['logs'],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages']
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def get_audit_statistics(self):
        """
        GET /admin/audit-logs/statistics
        Obtener estadísticas de audit logs
        """
        try:
            admin_id = g.user_id
            
            admin_service = self._get_service()
            stats = admin_service.audit_service.get_audit_statistics()
            
            # Log acción
            admin_service.audit_service.log_action(
                admin_id=admin_id,
                action='view_audit_statistics'
            )
            
            return jsonify({
                'status': 'success',
                'data': stats
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500


# Instancia global
admin_controller = AdminController()
