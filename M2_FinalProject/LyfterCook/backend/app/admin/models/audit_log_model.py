"""
Audit Log Model
Tracking de todas las acciones administrativas
"""
from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    """
    Modelo para audit trail de acciones administrativas
    """
    __tablename__ = 'admin_audit_logs'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('auth.users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50))  # 'chef', 'user', 'system'
    target_id = Column(Integer)
    reason = Column(Text)
    metadata = Column(JSON)  # Additional context
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
