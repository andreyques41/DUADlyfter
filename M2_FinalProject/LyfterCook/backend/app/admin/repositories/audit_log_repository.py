"""
Audit Log Repository
Manejo de persistencia para audit logs
"""
from typing import Optional, List, Dict
from flask import request
from sqlalchemy import desc
from app.admin.models.audit_log_model import AuditLog
from app.core.database import db


class AuditLogRepository:
    """Repository para operaciones de audit logs"""
    
    @staticmethod
    def create(admin_id: int, action: str, target_type: Optional[str] = None,
               target_id: Optional[int] = None, reason: Optional[str] = None,
               metadata: Optional[Dict] = None) -> AuditLog:
        """
        Crear un audit log
        
        Args:
            admin_id: ID del admin que realiza la acción
            action: Tipo de acción ('deactivate_chef', 'delete_user', etc.)
            target_type: Tipo de target ('chef', 'user', 'system')
            target_id: ID del target
            reason: Razón de la acción
            metadata: Datos adicionales en JSON
            
        Returns:
            AuditLog creado
        """
        # Obtener IP address del request
        ip_address = request.remote_addr if request else None
        
        audit_log = AuditLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            metadata=metadata,
            ip_address=ip_address
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return audit_log
    
    @staticmethod
    def find_all(page: int = 1, per_page: int = 50, 
                 admin_id: Optional[int] = None,
                 action_type: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> tuple:
        """
        Obtener logs con filtros y paginación
        
        Returns:
            (logs, total_count)
        """
        query = AuditLog.query
        
        # Filtros
        if admin_id:
            query = query.filter(AuditLog.admin_id == admin_id)
        
        if action_type:
            query = query.filter(AuditLog.action == action_type)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Ordenar por más reciente primero
        query = query.order_by(desc(AuditLog.created_at))
        
        # Contar total antes de paginar
        total = query.count()
        
        # Paginar
        offset = (page - 1) * per_page
        logs = query.offset(offset).limit(per_page).all()
        
        return logs, total
    
    @staticmethod
    def find_by_admin(admin_id: int, limit: int = 100) -> List[AuditLog]:
        """Obtener logs de un admin específico"""
        return AuditLog.query.filter_by(admin_id=admin_id)\
            .order_by(desc(AuditLog.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def find_by_target(target_type: str, target_id: int, limit: int = 50) -> List[AuditLog]:
        """Obtener logs de un target específico (ej: todos los logs de un chef)"""
        return AuditLog.query.filter_by(target_type=target_type, target_id=target_id)\
            .order_by(desc(AuditLog.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_statistics() -> Dict:
        """
        Obtener estadísticas de audit logs
        
        Returns:
            Dict con estadísticas de acciones
        """
        from datetime import datetime, timedelta
        
        # Total de logs
        total_logs = AuditLog.query.count()
        
        # Logs por acción
        logs_by_action = db.session.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action)\
         .order_by(desc('count')).all()
        
        action_dict = {action: count for action, count in logs_by_action}
        
        # Actividad reciente (últimos 7 días)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_logs = AuditLog.query.filter(
            AuditLog.created_at >= seven_days_ago
        ).count()
        
        # Admins más activos
        top_admins = db.session.query(
            AuditLog.admin_id,
            func.count(AuditLog.id).label('action_count')
        ).group_by(AuditLog.admin_id)\
         .order_by(desc('action_count'))\
         .limit(5).all()
        
        return {
            'total_logs': total_logs,
            'recent_logs_7_days': recent_logs,
            'logs_by_action': action_dict,
            'top_admins': [
                {'admin_id': admin_id, 'action_count': count}
                for admin_id, count in top_admins
            ]
        }
