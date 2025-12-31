"""
Audit Log Repository
Manejo de persistencia para audit logs
"""
from typing import Optional, List, Dict, Tuple
from flask import request
import logging
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.admin.models.audit_log_model import AuditLog


logger = logging.getLogger(__name__)


class AuditLogRepository:
    """Repository para operaciones de audit logs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, admin_id: int, action: str, target_type: Optional[str] = None,
               target_id: Optional[int] = None, reason: Optional[str] = None,
               metadata: Optional[Dict] = None) -> Optional[AuditLog]:
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
            action_metadata=metadata,
            ip_address=ip_address
        )
        
        try:
            self.db.add(audit_log)
            self.db.commit()
            return audit_log
        except SQLAlchemyError as e:
            # Best-effort audit logging: do not break admin endpoints if the
            # audit table is missing or unavailable.
            self.db.rollback()
            logger.warning(f"Failed to write admin audit log: {e}")
            return None
    
    def find_all(self, page: int = 1, per_page: int = 50,
                 admin_id: Optional[int] = None,
                 action_type: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> Tuple[List[AuditLog], int]:
        """
        Obtener logs con filtros y paginación
        
        Returns:
            (logs, total_count)
        """
        try:
            query = self.db.query(AuditLog)
        
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
        except SQLAlchemyError as e:
            logger.warning(f"Failed to read admin audit logs: {e}")
            return [], 0
    
    def find_by_admin(self, admin_id: int, limit: int = 100) -> List[AuditLog]:
        """Obtener logs de un admin específico"""
        return self.db.query(AuditLog).filter_by(admin_id=admin_id)\
            .order_by(desc(AuditLog.created_at))\
            .limit(limit)\
            .all()
    
    def find_by_target(self, target_type: str, target_id: int, limit: int = 50) -> List[AuditLog]:
        """Obtener logs de un target específico (ej: todos los logs de un chef)"""
        return self.db.query(AuditLog).filter_by(target_type=target_type, target_id=target_id)\
            .order_by(desc(AuditLog.created_at))\
            .limit(limit)\
            .all()
    
    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas de audit logs
        
        Returns:
            Dict con estadísticas de acciones
        """
        from datetime import datetime, timedelta

        try:
            # Total de logs
            total_logs = self.db.query(AuditLog).count()

            # Logs por acción
            logs_by_action = self.db.query(
                AuditLog.action,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.action)\
             .order_by(desc('count')).all()

            action_dict = {action: count for action, count in logs_by_action}

            # Actividad reciente (últimos 7 días)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_logs = self.db.query(AuditLog).filter(
                AuditLog.created_at >= seven_days_ago
            ).count()

            # Admins más activos
            top_admins = self.db.query(
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
        except SQLAlchemyError as e:
            logger.warning(f"Failed to compute admin audit log statistics: {e}")
            return {
                'total_logs': 0,
                'recent_logs_7_days': 0,
                'logs_by_action': {},
                'top_admins': []
            }
