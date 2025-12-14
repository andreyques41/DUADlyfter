"""
Admin Schemas
Validación y serialización para endpoints administrativos
"""
from marshmallow import Schema, fields, validate


class ChefStatusUpdateSchema(Schema):
    """Schema para actualizar estado de chef"""
    is_active = fields.Boolean(required=True)
    reason = fields.String(required=False, allow_none=True)


class UserDeleteSchema(Schema):
    """Schema para eliminar usuario"""
    confirm = fields.Boolean(required=True)
    reason = fields.String(required=True, validate=validate.Length(min=10))


class PaginationSchema(Schema):
    """Schema para metadata de paginación"""
    page = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()


class ChefStatsSchema(Schema):
    """Schema para estadísticas de un chef"""
    clients = fields.Integer()
    dishes = fields.Integer()
    menus = fields.Integer()


class ChefListItemSchema(Schema):
    """Schema para item en lista de chefs"""
    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    specialty = fields.String()
    bio = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    stats = fields.Nested(ChefStatsSchema)


class ChefListResponseSchema(Schema):
    """Schema para respuesta de lista de chefs"""
    status = fields.String()
    data = fields.List(fields.Nested(ChefListItemSchema))
    pagination = fields.Nested(PaginationSchema)


class DetailedStatsSchema(Schema):
    """Schema para estadísticas detalladas"""
    clients = fields.Integer()
    dishes_total = fields.Integer()
    dishes_active = fields.Integer()
    menus_total = fields.Integer()
    menus_active = fields.Integer()
    quotations_by_status = fields.Dict()
    appointments_by_status = fields.Dict()


class RecentActivitySchema(Schema):
    """Schema para actividad reciente"""
    last_login = fields.DateTime(allow_none=True)
    last_dish_created = fields.DateTime(allow_none=True)
    last_quotation_sent = fields.DateTime(allow_none=True)


class ChefDetailsSchema(Schema):
    """Schema para detalles completos de chef"""
    id = fields.Integer()
    user_id = fields.Integer()
    username = fields.String()
    email = fields.String()
    specialty = fields.String()
    bio = fields.String()
    phone = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    statistics = fields.Nested(DetailedStatsSchema)
    recent_activity = fields.Nested(RecentActivitySchema)


class ChefDetailsResponseSchema(Schema):
    """Schema para respuesta de detalles de chef"""
    status = fields.String()
    data = fields.Nested(ChefDetailsSchema)


class DashboardStatisticsSchema(Schema):
    """Schema para estadísticas del dashboard"""
    chefs_total = fields.Integer()
    chefs_active = fields.Integer()
    chefs_inactive = fields.Integer()
    clients_total = fields.Integer()
    dishes_total = fields.Integer()
    menus_total = fields.Integer()
    quotations_total = fields.Integer()
    appointments_total = fields.Integer()


class RecentActivityStatsSchema(Schema):
    """Schema para actividad reciente del dashboard"""
    new_chefs = fields.Integer()
    new_clients = fields.Integer()
    new_quotations = fields.Integer()


class TopChefSchema(Schema):
    """Schema para top chef"""
    chef_id = fields.Integer()
    username = fields.String()
    total_clients = fields.Integer()


class DashboardResponseSchema(Schema):
    """Schema para respuesta del dashboard"""
    status = fields.String()
    data = fields.Dict(keys=fields.String(), values=fields.Raw())


class UserListItemSchema(Schema):
    """Schema para item en lista de usuarios"""
    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    last_login = fields.DateTime(allow_none=True)


class UserListResponseSchema(Schema):
    """Schema para respuesta de lista de usuarios"""
    status = fields.String()
    data = fields.List(fields.Nested(UserListItemSchema))
    pagination = fields.Nested(PaginationSchema)
