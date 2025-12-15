"""
Audit Service
Business logic para audit logging
"""
from typing import Optional, Dict
from app.admin.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Servicio para manejo de audit logs"""
    
    def __init__(self, audit_repository: AuditLogRepository):
        self.audit_repo = audit_repository
    
    def log_action(self, admin_id: int, action: str, 
                   target_type: Optional[str] = None,
                   target_id: Optional[int] = None,
                   reason: Optional[str] = None,
                   metadata: Optional[Dict] = None):
        """
        Loggear una acción administrativa
        
        Args:
            admin_id: ID del admin
            action: Tipo de acción
            target_type: Tipo de target
            target_id: ID del target
            reason: Razón de la acción
            metadata: Datos adicionales
        """
        return self.audit_repo.create(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            metadata=metadata
        )
    
    def get_logs(self, page: int = 1, per_page: int = 50,
                 admin_id: Optional[int] = None,
                 action_type: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None):
        """Obtener logs con filtros"""
        logs, total = self.audit_repo.find_all(
            page=page,
            per_page=per_page,
            admin_id=admin_id,
            action_type=action_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            'logs': [log.to_dict() for log in logs],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_audit_statistics(self) -> Dict:
        """
        Obtener estadísticas de audit logs
        
        Returns:
            Dict con estadísticas
        """
        return self.audit_repo.get_statistics()
