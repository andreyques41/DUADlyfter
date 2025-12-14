"""
Admin Service
Business logic para operaciones administrativas
"""
from typing import Optional, Dict
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.services.audit_service import AuditService


class AdminService:
    """Servicio para operaciones administrativas"""
    
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.audit_service = AuditService()
    
    def get_dashboard(self, admin_id: int) -> Dict:
        """
        Obtener estadísticas del dashboard
        
        Args:
            admin_id: ID del admin solicitante
            
        Returns:
            Dict con estadísticas globales
        """
        stats = self.admin_repo.get_dashboard_statistics()
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='view_dashboard'
        )
        
        return stats
    
    def get_all_chefs(self, admin_id: int, page: int = 1, per_page: int = 20,
                      status: str = 'all', search: Optional[str] = None,
                      sort: str = 'created_at', order: str = 'desc') -> Dict:
        """
        Obtener lista de chefs con paginación
        
        Args:
            admin_id: ID del admin solicitante
            page: Página actual
            per_page: Items por página
            status: Filtro de estado
            search: Búsqueda por nombre/email/especialidad
            sort: Campo de ordenamiento
            order: Dirección de orden
            
        Returns:
            Dict con chefs y metadata de paginación
        """
        chefs_data, total = self.admin_repo.get_all_chefs(
            page=page,
            per_page=per_page,
            status=status,
            search=search,
            sort=sort,
            order=order
        )
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='list_chefs',
            metadata={
                'page': page,
                'per_page': per_page,
                'status': status,
                'search': search
            }
        )
        
        return {
            'chefs': chefs_data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_chef_details(self, admin_id: int, chef_id: int) -> Optional[Dict]:
        """
        Obtener detalles completos de un chef
        
        Args:
            admin_id: ID del admin solicitante
            chef_id: ID del chef
            
        Returns:
            Dict con info del chef y estadísticas o None si no existe
        """
        chef_details = self.admin_repo.get_chef_details(chef_id)
        
        if not chef_details:
            return None
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='view_chef_details',
            target_type='chef',
            target_id=chef_id
        )
        
        return chef_details
    
    def update_chef_status(self, admin_id: int, chef_id: int, 
                          is_active: bool, reason: Optional[str] = None) -> bool:
        """
        Activar/desactivar un chef
        
        Args:
            admin_id: ID del admin
            chef_id: ID del chef
            is_active: Nuevo estado
            reason: Razón del cambio
            
        Returns:
            True si tuvo éxito, False si el chef no existe
        """
        success = self.admin_repo.update_chef_status(chef_id, is_active)
        
        if not success:
            return False
        
        # Log action
        action = 'activate_chef' if is_active else 'deactivate_chef'
        self.audit_service.log_action(
            admin_id=admin_id,
            action=action,
            target_type='chef',
            target_id=chef_id,
            reason=reason,
            metadata={'is_active': is_active}
        )
        
        return True
    
    def get_all_users(self, admin_id: int, page: int = 1, per_page: int = 20,
                      role: str = 'all', status: str = 'all',
                      search: Optional[str] = None) -> Dict:
        """
        Obtener lista de usuarios con paginación
        
        Args:
            admin_id: ID del admin solicitante
            page: Página actual
            per_page: Items por página
            role: Filtro por rol
            status: Filtro por estado
            search: Búsqueda por username/email
            
        Returns:
            Dict con usuarios y metadata de paginación
        """
        users_data, total = self.admin_repo.get_all_users(
            page=page,
            per_page=per_page,
            role=role,
            status=status,
            search=search
        )
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='list_users',
            metadata={
                'page': page,
                'per_page': per_page,
                'role': role,
                'status': status,
                'search': search
            }
        )
        
        return {
            'users': users_data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def delete_user(self, admin_id: int, user_id: int, 
                    reason: str) -> tuple[bool, Optional[str]]:
        """
        Eliminar usuario (soft delete)
        
        Args:
            admin_id: ID del admin que ejecuta
            user_id: ID del usuario a eliminar
            reason: Razón de la eliminación
            
        Returns:
            Tuple (success, error_message)
        """
        success, error_msg = self.admin_repo.delete_user(user_id, admin_id)
        
        if not success:
            return False, error_msg
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='delete_user',
            target_type='user',
            target_id=user_id,
            reason=reason
        )
        
        return True, None
    
    def generate_report(self, admin_id: int, report_type: str,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Optional[Dict]:
        """
        Generar reporte del sistema
        
        Args:
            admin_id: ID del admin solicitante
            report_type: Tipo de reporte (activity, chefs, quotations)
            start_date: Fecha inicio (opcional)
            end_date: Fecha fin (opcional)
            
        Returns:
            Dict con reporte o None si tipo inválido
        """
        report_data = None
        
        if report_type == 'activity':
            report_data = self.admin_repo.generate_activity_report(start_date, end_date)
        elif report_type == 'chefs':
            report_data = self.admin_repo.generate_chefs_report()
        elif report_type == 'quotations':
            report_data = self.admin_repo.generate_quotations_report(start_date, end_date)
        else:
            return None
        
        # Log action
        self.audit_service.log_action(
            admin_id=admin_id,
            action='generate_report',
            metadata={
                'report_type': report_type,
                'start_date': start_date,
                'end_date': end_date
            }
        )
        
        return report_data
