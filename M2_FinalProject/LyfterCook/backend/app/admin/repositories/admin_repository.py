"""
Admin Repository
Queries para módulo administrativo
"""
from typing import Optional, List, Dict, Tuple
from sqlalchemy import func, desc, or_
from sqlalchemy.orm import Session
from app.auth.models.user_model import User
from app.chefs.models.chef_model import Chef
from app.clients.models.client_model import Client
from app.dishes.models.dish_model import Dish
from app.menus.models.menu_model import Menu
from app.quotations.models.quotation_model import Quotation
from app.appointments.models.appointment_model import Appointment


class AdminRepository:
    """Repository para operaciones administrativas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_statistics(self) -> Dict:
        """
        Obtener estadísticas globales del sistema
        
        Returns:
            Dict con estadísticas
        """
        # Contar chefs
        total_chefs = self.db.query(Chef).count()
        active_chefs = self.db.query(Chef).filter_by(is_active=True).count()
        inactive_chefs = total_chefs - active_chefs
        
        # Contar otros recursos
        total_clients = self.db.query(Client).count()
        total_dishes = self.db.query(Dish).count()
        total_menus = self.db.query(Menu).count()
        total_quotations = self.db.query(Quotation).count()
        total_appointments = self.db.query(Appointment).count()
        
        # Actividad reciente (últimos 7 días)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        new_chefs_last_7_days = self.db.query(Chef).filter(Chef.created_at >= seven_days_ago).count()
        new_clients_last_7_days = self.db.query(Client).filter(Client.created_at >= seven_days_ago).count()
        quotations_last_7_days = self.db.query(Quotation).filter(Quotation.created_at >= seven_days_ago).count()
        
        # Top chefs (por número de clientes)
        top_chefs = self.db.query(
            Chef.id,
            User.username,
            func.count(Client.id).label('total_clients')
        ).join(User, Chef.user_id == User.id)\
         .outerjoin(Client, Chef.id == Client.chef_id)\
         .group_by(Chef.id, User.username)\
         .order_by(desc('total_clients'))\
         .limit(5)\
         .all()
        
        return {
            'statistics': {
                'total_chefs': total_chefs,
                'active_chefs': active_chefs,
                'inactive_chefs': inactive_chefs,
                'total_clients': total_clients,
                'total_dishes': total_dishes,
                'total_menus': total_menus,
                'total_quotations': total_quotations,
                'total_appointments': total_appointments
            },
            'recent_activity': {
                'new_chefs_last_7_days': new_chefs_last_7_days,
                'new_clients_last_7_days': new_clients_last_7_days,
                'quotations_last_7_days': quotations_last_7_days
            },
            'top_chefs': [
                {
                    'chef_id': chef.id,
                    'username': chef.username,
                    'total_clients': chef.total_clients
                }
                for chef in top_chefs
            ]
        }
    
    def get_all_chefs(self, page: int = 1, per_page: int = 20, 
                     status: str = 'all', search: Optional[str] = None,
                     sort: str = 'created_at', order: str = 'desc') -> Tuple:
        """
        Obtener todos los chefs con filtros
        
        Args:
            page: Número de página
            per_page: Items por página
            status: 'active', 'inactive', 'all'
            search: Búsqueda por username, email, specialty
            sort: Campo para ordenar
            order: 'asc' o 'desc'
            
        Returns:
            (chefs_data, total)
        """
        # Query base con JOIN a users
        query = self.db.query(
            Chef,
            User.username,
            User.email,
            func.count(Client.id).label('total_clients'),
            func.count(Dish.id).label('total_dishes')
        ).join(User, Chef.user_id == User.id)\
         .outerjoin(Client, Chef.id == Client.chef_id)\
         .outerjoin(Dish, Chef.id == Dish.chef_id)
        
        # Filtro por status
        if status == 'active':
            query = query.filter(Chef.is_active == True)
        elif status == 'inactive':
            query = query.filter(Chef.is_active == False)
        
        # Búsqueda
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Chef.specialty.ilike(search_pattern)
                )
            )
        
        # Group by
        query = query.group_by(Chef.id, User.username, User.email)
        
        # Ordenar
        if sort == 'username':
            sort_column = User.username
        elif sort == 'total_clients':
            sort_column = func.count(Client.id)
        else:  # created_at (default)
            sort_column = Chef.created_at
        
        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Contar total
        total = query.count()
        
        # Paginar
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        
        # Formatear resultados
        chefs_data = [
            {
                'id': result.Chef.id,
                'user_id': result.Chef.user_id,
                'username': result.username,
                'email': result.email,
                'specialty': result.Chef.specialty,
                'location': result.Chef.location,
                'is_active': result.Chef.is_active,
                'created_at': result.Chef.created_at.isoformat() if result.Chef.created_at else None,
                'stats': {
                    'total_clients': result.total_clients,
                    'total_dishes': result.total_dishes
                }
            }
            for result in results
        ]
        
        return chefs_data, total
    
    def get_chef_details(self, chef_id: int) -> Optional[Dict]:
        """
        Obtener detalles completos de un chef
        
        Returns:
            Dict con chef info + estadísticas detalladas
        """
        # Obtener chef con user info
        result = self.db.query(Chef, User)\
            .join(User, Chef.user_id == User.id)\
            .filter(Chef.id == chef_id)\
            .first()
        
        if not result:
            return None
        
        chef, user = result
        
        # Estadísticas
        total_clients = self.db.query(Client).filter_by(chef_id=chef_id).count()
        total_dishes = self.db.query(Dish).filter_by(chef_id=chef_id).count()
        active_dishes = self.db.query(Dish).filter_by(chef_id=chef_id, is_active=True).count()
        total_menus = self.db.query(Menu).filter_by(chef_id=chef_id).count()
        active_menus = self.db.query(Menu).filter_by(chef_id=chef_id, status='active').count()
        
        # Cotizaciones por status
        quotations_by_status = self.db.query(
            Quotation.status,
            func.count(Quotation.id)
        ).filter(Quotation.chef_id == chef_id)\
         .group_by(Quotation.status)\
         .all()
        
        quotations_dict = {status: count for status, count in quotations_by_status}
        total_quotations = sum(quotations_dict.values())
        
        # Citas por status
        appointments_by_status = self.db.query(
            Appointment.status,
            func.count(Appointment.id)
        ).filter(Appointment.chef_id == chef_id)\
         .group_by(Appointment.status)\
         .all()
        
        appointments_dict = {status: count for status, count in appointments_by_status}
        total_appointments = sum(appointments_dict.values())
        
        # Actividad reciente
        last_dish = self.db.query(Dish).filter_by(chef_id=chef_id)\
            .order_by(desc(Dish.created_at))\
            .first()
        
        last_quotation = self.db.query(Quotation).filter_by(chef_id=chef_id)\
            .order_by(desc(Quotation.created_at))\
            .first()
        
        return {
            'chef': {
                'id': chef.id,
                'user_id': chef.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'specialty': chef.specialty,
                'bio': chef.bio,
                'phone': chef.phone,
                'location': chef.location,
                'is_active': chef.is_active,
                'created_at': chef.created_at.isoformat() if chef.created_at else None,
                'updated_at': chef.updated_at.isoformat() if chef.updated_at else None
            },
            'statistics': {
                'total_clients': total_clients,
                'total_dishes': total_dishes,
                'active_dishes': active_dishes,
                'total_menus': total_menus,
                'active_menus': active_menus,
                'total_quotations': total_quotations,
                'quotations_by_status': quotations_dict,
                'total_appointments': total_appointments,
                'appointments_by_status': appointments_dict
            },
            'recent_activity': {
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'last_dish_created': last_dish.created_at.isoformat() if last_dish else None,
                'last_quotation_sent': last_quotation.created_at.isoformat() if last_quotation else None
            }
        }
    
    def update_chef_status(self, chef_id: int, is_active: bool) -> bool:
        """
        Actualizar status de chef Y su usuario asociado
        
        Returns:
            True si se actualizó correctamente
        """
        chef = self.db.query(Chef).get(chef_id)
        if not chef:
            return False
        
        # Actualizar chef
        chef.is_active = is_active
        
        # Actualizar usuario asociado (para bloquear login)
        user = self.db.query(User).get(chef.user_id)
        if user:
            user.is_active = is_active
        
        self.db.commit()
        return True
    
    def get_all_users(self, page: int = 1, per_page: int = 20, 
                      role: str = 'all', status: str = 'all',
                      search: Optional[str] = None) -> Tuple[List[Dict], int]:
        """
        Obtener todos los usuarios del sistema con filtros
        
        Args:
            page: Número de página
            per_page: Usuarios por página
            role: Filtro por rol (all, admin, chef)
            status: Filtro por estado (all, active, inactive)
            search: Búsqueda por username/email
            
        Returns:
            Tuple (lista de usuarios, total)
        """
        # Base query
        query = self.db.query(User)
        
        # Filtro por rol
        if role != 'all':
            query = query.filter(User.role == role)
        
        # Filtro por estado
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)
        
        # Búsqueda por username o email
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(desc(User.created_at))
        
        # Contar total antes de paginación
        total = query.count()
        
        # Aplicar paginación
        offset = (page - 1) * per_page
        users = query.offset(offset).limit(per_page).all()
        
        # Formatear resultados
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return users_data, total
    
    def delete_user(self, user_id: int, admin_id: int) -> Tuple[bool, Optional[str]]:
        """
        Eliminar usuario (soft delete)
        
        Args:
            user_id: ID del usuario a eliminar
            admin_id: ID del admin que ejecuta la acción
            
        Returns:
            Tuple (success, error_message)
        """
        # Validación 1: Admin no puede eliminarse a sí mismo
        if user_id == admin_id:
            return False, "No puedes eliminar tu propia cuenta"
        
        # Obtener usuario
        user = self.db.query(User).get(user_id)
        if not user:
            return False, "Usuario no encontrado"
        
        # Validación 2: No eliminar al último admin activo
        if user.role == 'admin' and user.is_active:
            active_admins_count = self.db.query(User).filter_by(
                role='admin',
                is_active=True
            ).count()
            
            if active_admins_count <= 1:
                return False, "No puedes eliminar al único administrador activo"
        
        # Soft delete del usuario
        user.is_active = False
        
        # Si el usuario es chef, también desactivar su perfil
        if user.role == 'chef':
            chef = self.db.query(Chef).filter_by(user_id=user_id).first()
            if chef:
                chef.is_active = False
        
        self.db.commit()
        return True, None
    
    def generate_activity_report(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict:
        """
        Generar reporte de actividad del sistema
        
        Args:
            start_date: Fecha inicio (ISO format)
            end_date: Fecha fin (ISO format)
            
        Returns:
            Dict con reporte de actividad
        """
        from datetime import datetime, timedelta
        
        # Fechas por defecto: últimos 30 días
        if not end_date:
            end = datetime.now()
        else:
            end = datetime.fromisoformat(start_date)
        
        if not start_date:
            start = end - timedelta(days=30)
        else:
            start = datetime.fromisoformat(start_date)
        
        # Nuevos registros en el período
        new_chefs = self.db.query(Chef).filter(
            Chef.created_at >= start,
            Chef.created_at <= end
        ).count()
        
        new_clients = self.db.query(Client).filter(
            Client.created_at >= start,
            Client.created_at <= end
        ).count()
        
        new_dishes = self.db.query(Dish).filter(
            Dish.created_at >= start,
            Dish.created_at <= end
        ).count()
        
        new_menus = self.db.query(Menu).filter(
            Menu.created_at >= start,
            Menu.created_at <= end
        ).count()
        
        new_quotations = self.db.query(Quotation).filter(
            Quotation.created_at >= start,
            Quotation.created_at <= end
        ).count()
        
        new_appointments = self.db.query(Appointment).filter(
            Appointment.created_at >= start,
            Appointment.created_at <= end
        ).count()
        
        # Cotizaciones por estado en el período
        quotations_by_status = self.db.query(
            Quotation.status,
            func.count(Quotation.id)
        ).filter(
            Quotation.created_at >= start,
            Quotation.created_at <= end
        ).group_by(Quotation.status).all()
        
        quotations_status_dict = {status: count for status, count in quotations_by_status}
        
        # Citas por estado en el período
        appointments_by_status = self.db.query(
            Appointment.status,
            func.count(Appointment.id)
        ).filter(
            Appointment.created_at >= start,
            Appointment.created_at <= end
        ).group_by(Appointment.status).all()
        
        appointments_status_dict = {status: count for status, count in appointments_by_status}
        
        return {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat(),
                'days': (end - start).days
            },
            'new_records': {
                'chefs': new_chefs,
                'clients': new_clients,
                'dishes': new_dishes,
                'menus': new_menus,
                'quotations': new_quotations,
                'appointments': new_appointments
            },
            'quotations_by_status': quotations_status_dict,
            'appointments_by_status': appointments_status_dict
        }
    
    def generate_chefs_report(self) -> Dict:
        """
        Generar reporte detallado de chefs
        
        Returns:
            Dict con estadísticas de chefs
        """
        # Totales
        total_chefs = self.db.query(Chef).count()
        active_chefs = self.db.query(Chef).filter_by(is_active=True).count()
        inactive_chefs = total_chefs - active_chefs
        
        # Chefs con más clientes
        top_chefs_by_clients = self.db.query(
            Chef.id,
            User.username,
            Chef.specialty,
            func.count(Client.id).label('total_clients')
        ).join(User, User.id == Chef.user_id)\
         .outerjoin(Client, Client.chef_id == Chef.id)\
         .group_by(Chef.id, User.username, Chef.specialty)\
         .order_by(desc('total_clients'))\
         .limit(10).all()
        
        # Chefs con más platos
        top_chefs_by_dishes = self.db.query(
            Chef.id,
            User.username,
            func.count(Dish.id).label('total_dishes')
        ).join(User, User.id == Chef.user_id)\
         .outerjoin(Dish, Dish.chef_id == Chef.id)\
         .group_by(Chef.id, User.username)\
         .order_by(desc('total_dishes'))\
         .limit(10).all()
        
        # Chefs por especialidad
        chefs_by_specialty = self.db.query(
            Chef.specialty,
            func.count(Chef.id).label('count')
        ).group_by(Chef.specialty)\
         .order_by(desc('count')).all()
        
        return {
            'summary': {
                'total': total_chefs,
                'active': active_chefs,
                'inactive': inactive_chefs,
                'activity_rate': round((active_chefs / total_chefs * 100), 2) if total_chefs > 0 else 0
            },
            'top_chefs_by_clients': [
                {
                    'chef_id': chef_id,
                    'username': username,
                    'specialty': specialty,
                    'total_clients': total_clients
                }
                for chef_id, username, specialty, total_clients in top_chefs_by_clients
            ],
            'top_chefs_by_dishes': [
                {
                    'chef_id': chef_id,
                    'username': username,
                    'total_dishes': total_dishes
                }
                for chef_id, username, total_dishes in top_chefs_by_dishes
            ],
            'by_specialty': [
                {
                    'specialty': specialty,
                    'count': count
                }
                for specialty, count in chefs_by_specialty
            ]
        }
    
    def generate_quotations_report(self, start_date: Optional[str] = None,
                                    end_date: Optional[str] = None) -> Dict:
        """
        Generar reporte de cotizaciones
        
        Args:
            start_date: Fecha inicio (ISO format)
            end_date: Fecha fin (ISO format)
            
        Returns:
            Dict con estadísticas de cotizaciones
        """
        from datetime import datetime, timedelta
        
        # Fechas por defecto: últimos 30 días
        if not end_date:
            end = datetime.now()
        else:
            end = datetime.fromisoformat(end_date)
        
        if not start_date:
            start = end - timedelta(days=30)
        else:
            start = datetime.fromisoformat(start_date)
        
        # Query base
        query = self.db.query(Quotation).filter(
            Quotation.created_at >= start,
            Quotation.created_at <= end
        )
        
        total_quotations = query.count()
        
        # Por estado
        by_status = self.db.query(
            Quotation.status,
            func.count(Quotation.id)
        ).filter(
            Quotation.created_at >= start,
            Quotation.created_at <= end
        ).group_by(Quotation.status).all()
        
        status_dict = {status: count for status, count in by_status}
        
        # Tasa de aceptación
        accepted = status_dict.get('accepted', 0)
        acceptance_rate = round((accepted / total_quotations * 100), 2) if total_quotations > 0 else 0
        
        # Chefs con más cotizaciones aceptadas
        top_chefs = self.db.query(
            Chef.id,
            User.username,
            func.count(Quotation.id).label('accepted_count')
        ).join(User, User.id == Chef.user_id)\
         .join(Quotation, Quotation.chef_id == Chef.id)\
         .filter(
            Quotation.status == 'accepted',
            Quotation.created_at >= start,
            Quotation.created_at <= end
        ).group_by(Chef.id, User.username)\
         .order_by(desc('accepted_count'))\
         .limit(10).all()
        
        return {
            'period': {
                'start': start.isoformat(),
                'end': end.isoformat()
            },
            'summary': {
                'total': total_quotations,
                'by_status': status_dict,
                'acceptance_rate': acceptance_rate
            },
            'top_chefs_by_accepted': [
                {
                    'chef_id': chef_id,
                    'username': username,
                    'accepted_quotations': count
                }
                for chef_id, username, count in top_chefs
            ]
        }
